from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone

from ..serializers import ResumeAnalysisSerializer
from ..services import ai_checker_resume_service
from ..utils.rate_limit import enforce_rate_limit

@extend_schema(
    tags=["CV Analysis"],
    summary="Analyze CV/Resume (Async)",
    description="Upload a CV/Resume file and description for asynchronous analysis. Returns a task_id to check status "
                "later.",
    request=ResumeAnalysisSerializer,
    responses={
        202: OpenApiResponse(
            response={"type": "object"},
            description="Task created successfully",
            examples=[
                OpenApiExample(
                    "Success",
                    value={
                        "task_id": "a1b2c3d4-5678-90ef-ghij-klmnopqrstuv",
                        "status": "processing"
                    }
                )
            ]
        ),
    }
)
class ResumeAtsAnalyzeView(APIView):
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser]

    def _get_user_identity_and_plan(self, request):
        # Identify user: prefer authenticated JWT subject, else IP-based fallback
        if getattr(request, 'user', None) and getattr(request.user, 'is_authenticated', False):
            user_id = str(getattr(request.user, 'identifier', 'anonymous'))
        else:
            # Basic IP fallback (not perfect behind proxies)
            user_id = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', 'anonymous'))
        plan = (request.headers.get('X-Plan') or request.query_params.get('plan') or 'free').lower()
        return user_id, plan

    def post(self, request):
        user_id, plan = self._get_user_identity_and_plan(request)

        # Check if force_refresh is requested (bypass cache)
        force_refresh = request.data.get('force_refresh', 'false').lower() == 'true'

        # Parse request early to check cache BEFORE rate limiting
        s = ResumeAnalysisSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        jd = s.validated_data.get("job_description", "")
        cv = s.validated_data["cv_file"]

        # Try cache first (if not force_refresh) - doesn't count against rate limit
        if not force_refresh:
            cached_result = ai_checker_resume_service.try_get_cached_result(cv, jd)
            if cached_result:
                # Cache HIT - return immediately without consuming rate limit
                cached_result.setdefault("rate_limit", {}).update({
                    "plan": plan,
                    "user": user_id,
                    "cached": True,
                    "quota_used": False,
                    "tip": "This result was served from cache and did not consume your quota."
                })
                return Response(cached_result)

        # Cache MISS or force_refresh - enforce rate limit
        allowed, info = enforce_rate_limit(user_id=user_id, plan=plan)
        if not allowed:
            return Response({
                "detail": info.get("message") or "Rate limit exceeded",
                "reason": info.get("reason"),
                "retry_after": info.get("retry_after"),
                "plan": plan,
                "user": user_id,
                "tip": "If you're analyzing the same CV and job description, the cached result will be returned instantly without consuming your quota."
            }, status=status.HTTP_429_TOO_MANY_REQUESTS)

        # Pass force_refresh to service
        result = ai_checker_resume_service.analyze_cv_vs_jd(cv, jd, force_refresh=force_refresh)

        # Attach rate-limit meta for transparency
        result.setdefault("rate_limit", {}).update({
            "plan": plan,
            "user": user_id,
            "cached": False,
            "quota_used": True,
            **({k: v for k, v in info.items() if k in ("remaining_today", "interval_lock")}),
        })
        return Response(result)
