import os
import datetime as dt
import logging
from typing import Optional, Tuple

try:
    import redis  # type: ignore
except Exception:  # pragma: no cover
    redis = None  # Fallback if redis not installed at runtime

from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)


def _get_redis_url() -> str:
    """Get Redis URL, prioritizing REDIS_URL for production."""
    redis_url = os.getenv("REDIS_URL")
    if redis_url:
        return redis_url

    # Fallback to constructing URL from individual vars (local dev)
    host = os.getenv("REDIS_HOST", "localhost")
    port = os.getenv("REDIS_PORT", "6379")
    db = os.getenv("REDIS_DB", "0")
    password = os.getenv("REDIS_PASSWORD", "")

    if password:
        return f"redis://:{password}@{host}:{port}/{db}"
    return f"redis://{host}:{port}/{db}"


def get_redis_client():
    if redis is None:
        return None
    try:
        url = _get_redis_url()
        client = redis.Redis.from_url(url, decode_responses=True, socket_connect_timeout=5)
        # Test connection
        client.ping()
        return client
    except redis.exceptions.AuthenticationError as e:
        logger.warning(f"Redis authentication failed: {e}")
        return None
    except redis.exceptions.ConnectionError as e:
        logger.warning(f"Redis connection failed: {e}")
        return None
    except Exception as e:
        logger.warning(f"Redis client error: {e}")
        return None


def _end_of_day_seconds(now: Optional[dt.datetime] = None) -> int:
    tz = timezone.get_current_timezone()
    now = now or timezone.now()
    now = now.astimezone(tz)
    eod = (now + dt.timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    return int((eod - now).total_seconds())


def _plan_quota(plan: str) -> Tuple[int, int]:
    plan = (plan or "free").lower()
    if plan == "pro":
        return (
            int(os.getenv("AI_CV_PRO_DAILY", "200")),
            int(os.getenv("AI_CV_PRO_INTERVAL", "5")),
        )
    if plan in ("enterprise", "ent"):  # alias
        return (
            int(os.getenv("AI_CV_ENT_DAILY", "1000")),
            int(os.getenv("AI_CV_ENT_INTERVAL", "1")),
        )
    # default: free - Giảm từ 30s → 10s để UX tốt hơn
    # Cache sẽ xử lý việc tránh gọi API nhiều lần
    return (
        int(os.getenv("AI_CV_FREE_DAILY", "10")),  # Tăng từ 5 → 10 lần/ngày
        int(os.getenv("AI_CV_FREE_INTERVAL", "10")),  # Giảm từ 30s → 10s
    )


def _user_key_base(user_id: str, plan: str) -> str:
    return f"rl:cv:{plan}:{user_id}"


def enforce_rate_limit(user_id: str, plan: str = "free") -> Tuple[bool, dict]:
    """
    Enforce both daily quota and min-interval throttle for a user.
    Returns (allowed: bool, info: dict).
    info contains reason and retry_after on block, or remaining on allow.
    """
    r = get_redis_client()
    daily_limit, min_interval = _plan_quota(plan)
    base = _user_key_base(user_id, plan)

    # If Redis is unavailable, allow request but mark degraded
    if r is None:
        return True, {
            "degraded": True,
            "message": "Rate limit backend unavailable; allowing request",
        }

    # Throttle: 1 request per min_interval seconds (SETNX with TTL)
    throttle_key = f"{base}:throttle"
    if min_interval > 0:
        set_ok = r.set(throttle_key, "1", nx=True, ex=min_interval)
        if not set_ok:
            ttl = r.ttl(throttle_key)
            return False, {
                "reason": "interval",
                "retry_after": max(ttl, 1) if ttl and ttl > 0 else min_interval,
                "message": f"Too many requests. Try again in {max(ttl,1) if ttl else min_interval}s",
            }

    # Daily quota: INCR with expiry at end of day
    today = timezone.now().astimezone(timezone.get_current_timezone()).strftime("%Y%m%d")
    daily_key = f"{base}:daily:{today}"
    current = r.incr(daily_key, 1)
    # set expiry if new
    if current == 1:
        r.expire(daily_key, _end_of_day_seconds())

    if current > daily_limit:
        ttl = r.ttl(daily_key)
        return False, {
            "reason": "daily",
            "retry_after": max(ttl, 60) if ttl and ttl > 0 else 3600,
            "message": "Daily quota exceeded",
            "limit": daily_limit,
            "used": int(current),
            "reset_in": ttl,
        }

    return True, {
        "remaining_today": max(daily_limit - int(current), 0),
        "interval_lock": min_interval,
    }
