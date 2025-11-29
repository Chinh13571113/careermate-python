import os
import json
import hashlib
import time
from agent_core.llm import get_openai_model
from . import clean_json_output, extract_text



# 🧾 Fixed explanations for each section (like Cake.me)
FIELD_EXPLANATIONS = {
    "content": (
        "This section ensures your resume includes clearly quantifiable results "
        "and is free of grammatical or spelling errors. These improvements make your resume "
        "more impressive and memorable to recruiters."
    ),
    "skills": (
        "This section compares your resume against the job description to identify missing or "
        "underrepresented skills. Adding these skills increases the chance of passing ATS filters."
    ),
    "format": (
        "This section checks date formats, resume length, and the effective use of bullet points "
        "to ensure your resume is clean, concise, and ATS-friendly."
    ),
    "sections": (
        "This section checks whether all required fields — such as contact information and "
        "work experience — are properly filled and formatted, ensuring ATS compatibility."
    ),
    "style": (
        "This section helps adjust the tone and wording of your resume to align with the job "
        "description while avoiding generic or cliché phrases, resulting in a more professional and impactful resume."
    ),
}

# 🧭 Footer section — personalized improvement recommendations
RECOMMENDATION_HEADER = {
    "title": "Recommendations for You",
    "description": (
        "Here are some personalized recommendations to help you improve your resume and "
        "increase your ATS score, as well as suggestions to guide your skill or career development."
    ),
}

CACHE_DIR = os.path.join(os.path.dirname(__file__), "../../../.cache/ai_cv_analysis")
CACHE_TTL_SECONDS = int(os.getenv("AI_CV_ANALYSIS_CACHE_TTL", "604800"))  # 7 days default
CACHE_VERSION = os.getenv("AI_CV_ANALYSIS_CACHE_VERSION", "v1")


def _ensure_cache_dir():
    os.makedirs(os.path.abspath(CACHE_DIR), exist_ok=True)


def _cache_path(key: str) -> str:
    _ensure_cache_dir()
    return os.path.abspath(os.path.join(CACHE_DIR, f"{key}.json"))


def _cache_get(key: str):
    try:
        path = _cache_path(key)
        if not os.path.exists(path):
            return None
        # TTL check
        if CACHE_TTL_SECONDS > 0:
            mtime = os.path.getmtime(path)
            if time.time() - mtime > CACHE_TTL_SECONDS:
                return None
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        # mark cache hit
        if isinstance(data, dict):
            data.setdefault("cache", {})
            data["cache"].update({"hit": True, "key": key, "age_seconds": int(time.time() - os.path.getmtime(path))})
        return data
    except Exception:
        return None


def _cache_set(key: str, result: dict):
    path = _cache_path(key)
    tmp = path + ".tmp"
    # include cache metadata
    to_write = dict(result)
    to_write.setdefault("cache", {})
    to_write["cache"].update({"hit": False, "key": key, "stored_at": int(time.time())})
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(to_write, f, ensure_ascii=False)
    os.replace(tmp, path)


def try_get_cached_result(cv_file, job_description: str):
    """
    Try to get cached result without calling AI API.
    Returns cached result if found, None otherwise.
    """
    try:
        # Extract and normalize CV text
        cv_text = extract_text.extract_text(cv_file)
        cv_summary = cv_text[:2000]
        jd_summary = job_description[:1500]

        # Build same cache key as analyze_cv_vs_jd
        model_config = {
            "model": os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            "temperature": 0.5,
            "top_p": 0.9,
        }

        prompt = f"""Analyze CV vs Job. Score 0-100. Return ONLY valid JSON.

{{
  "summary": {{"overall_match": <int>, "overview_comment": "<text>", "strengths": ["item1", "item2", "item3"], "improvements": ["item1", "item2", "item3"]}},
  "content": {{"score": <int>, "measurable_results": ["item1", "item2"], "grammar_issues": ["item1", "item2"], "tips": ["item1", "item2"]}},
  "skills": {{"score": <int>, "technical": {{"matched": ["skill1", "skill2", "skill3"], "missing": ["skill1", "skill2", "skill3"]}}, "soft": {{"missing": ["skill1", "skill2"]}}, "tips": ["item1", "item2"]}},
  "format": {{"score": <int>, "checks": {{"date_format": "PASS|FAIL", "length": "PASS|FAIL", "bullet_points": "PASS|FAIL"}}, "tips": ["item1", "item2"]}},
  "sections": {{"score": <int>, "missing": ["section1", "section2"], "tips": ["item1", "item2"]}},
  "style": {{"score": <int>, "tone": ["issue1", "issue2"], "buzzwords": ["word1", "word2"], "tips": ["item1", "item2"]}},
  "recommendations": {{"items": ["rec1", "rec2", "rec3"]}},
  "overall_score": <int>,
  "overall_comment": "<text max 50 words>"
}}

RESUME:
{cv_summary}

JOB DESCRIPTION:
{jd_summary}

Analyze and return complete JSON:"""

        key_basis = json.dumps({
            "version": CACHE_VERSION,
            "prompt": prompt,
            "config": model_config,
        }, ensure_ascii=False)
        key = hashlib.sha256(key_basis.encode("utf-8")).hexdigest()

        # Try to get from cache
        return _cache_get(key)
    except Exception as e:
        print(f"⚠️ Cache check error: {e}")
        return None


def analyze_cv_vs_jd(cv_file, job_description: str, force_refresh: bool = False):
    """
    AI-powered CV + JD analysis (Cake.me style)
    Returns structured JSON with sections:
    summary, content, skills, format, sections, style, recommendations, overall_score
    """

    # 1️⃣ Extract and normalize CV text
    cv_text = extract_text.extract_text(cv_file)

    # 2️⃣ Tóm tắt CV và JD để giảm token
    cv_summary = cv_text[:2000]
    jd_summary = job_description[:1500]

    # 3️⃣ Build the analysis prompt - Tối ưu cho OpenAI
    prompt = f"""Analyze CV vs Job. Score 0-100. Return ONLY valid JSON.

{{
  "summary": {{"overall_match": <int>, "overview_comment": "<text>", "strengths": ["item1", "item2", "item3"], "improvements": ["item1", "item2", "item3"]}},
  "content": {{"score": <int>, "measurable_results": ["item1", "item2"], "grammar_issues": ["item1", "item2"], "tips": ["item1", "item2"]}},
  "skills": {{"score": <int>, "technical": {{"matched": ["skill1", "skill2", "skill3"], "missing": ["skill1", "skill2", "skill3"]}}, "soft": {{"missing": ["skill1", "skill2"]}}, "tips": ["item1", "item2"]}},
  "format": {{"score": <int>, "checks": {{"date_format": "PASS|FAIL", "length": "PASS|FAIL", "bullet_points": "PASS|FAIL"}}, "tips": ["item1", "item2"]}},
  "sections": {{"score": <int>, "missing": ["section1", "section2"], "tips": ["item1", "item2"]}},
  "style": {{"score": <int>, "tone": ["issue1", "issue2"], "buzzwords": ["word1", "word2"], "tips": ["item1", "item2"]}},
  "recommendations": {{"items": ["rec1", "rec2", "rec3"]}},
  "overall_score": <int>,
  "overall_comment": "<text max 50 words>"
}}

RESUME:
{cv_summary}

JOB DESCRIPTION:
{jd_summary}

Analyze and return complete JSON:"""

    # 3.5️⃣ Cache key by full prompt hash + config (prompt caching)
    # Include cache version, model/config to avoid stale collisions after changes
    model_config = {
        "model": os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        "temperature": 0.5,
        "top_p": 0.9,
    }
    key_basis = json.dumps({
        "version": CACHE_VERSION,
        "prompt": prompt,
        "config": model_config,
    }, ensure_ascii=False)
    key = hashlib.sha256(key_basis.encode("utf-8")).hexdigest()

    if not force_refresh:
        cached = _cache_get(key)
        if cached:
            print(f"🗃️ Cache HIT: {key} (age={cached.get('cache',{}).get('age_seconds','?')}s)")
            return cached
    else:
        print("🗃️ Cache BYPASSED (force_refresh=True)")

    # 4️⃣ Run OpenAI API
    model = get_openai_model(temperature=model_config["temperature"], top_p=model_config["top_p"])

    try:
        # Gọi OpenAI invoke() thay vì generate_content()
        response = model.invoke(prompt)
        raw_text = response.content if hasattr(response, 'content') else str(response)
        raw_text = raw_text.strip()

        # OpenAI không có usage_metadata như Gemini
        # Tính token ước tính (OpenAI ~4 chars = 1 token)
        input_tokens = len(prompt) // 4
        output_tokens = len(raw_text) // 4
        total_tokens = input_tokens + output_tokens

        print(f"📥 Input tokens (estimated): {input_tokens}")
        print(f"📤 Output tokens (estimated): {output_tokens}")
        print(f"📊 Total tokens (estimated): {total_tokens}")

    except Exception as e:
        print(f"❌ OpenAI Error: {str(e)}")

        # Fallback JSON nếu lỗi
        raw_text = json.dumps({
            "summary": {
                "overall_match": 50,
                "overview_comment": "Analysis incomplete",
                "strengths": ["Resume submitted"],
                "improvements": ["Please try again"]
            },
            "content": {"score": 50, "measurable_results": [], "grammar_issues": [], "tips": []},
            "skills": {"score": 50, "technical": {"matched": [], "missing": []}, "soft": {"missing": []}, "tips": []},
            "format": {"score": 50, "checks": {"date_format": "PASS", "length": "PASS", "bullet_points": "PASS"}, "tips": []},
            "sections": {"score": 50, "missing": [], "tips": []},
            "style": {"score": 50, "tone": [], "buzzwords": [], "tips": []},
            "recommendations": {"items": ["Please retry"]},
            "overall_score": 50,
            "overall_comment": "Error occurred"
        })

        input_tokens = len(prompt) // 4
        output_tokens = len(raw_text) // 4
        total_tokens = input_tokens + output_tokens

    # 5️⃣ Clean and parse the JSON safely
    result = clean_json_output.clean_json_output(raw_text)

    # 6️⃣ Inject static explanations into each ATS field
    for key_field, desc in FIELD_EXPLANATIONS.items():
        if key_field in result:
            result[key_field]["description"] = desc
        else:
            result[key_field] = {"description": desc}

    # 7️⃣ Ensure recommendations section exists
    if "recommendations" not in result:
        result["recommendations"] = {"items": []}
    result["recommendations"].update({
        "title": "Recommendations for You",
        "description": (
            "Here are some personalized recommendations to help you improve your resume and "
            "increase your ATS score, as well as suggestions to guide your skill or career development."
        ),
    })

    # 8️⃣ Add token usage info to result
    result["token_usage"] = {
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": total_tokens,
        "estimated": True,
        "cache": {
            "key": key,
            "hit": False if force_refresh else False,
        },
    }

    # 9️⃣ Save to cache
    _cache_set(key, result)

    return result
