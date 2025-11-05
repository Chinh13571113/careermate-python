import os, json, re
import google.generativeai as genai
from . import analyzer_service,clean_json_output,extract_text

# ⚙️ Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

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


def analyze_cv_vs_jd(cv_file, job_description: str):
    """
    AI-powered CV + JD analysis (Cake.me style)
    Returns structured JSON with sections:
    summary, content, skills, format, sections, style, recommendations, overall_score
    """

    # 1️⃣ Extract and normalize CV text
    cv_text = extract_text.extract_text(cv_file)

    # 2️⃣ Extract basic structure (name, skills, education, experience, etc.)
    cv_json = analyzer_service.analyze_resume_text(cv_text)

    # 3️⃣ Build the analysis prompt for Gemini
    prompt = f"""
You are an AI Resume Analysis Engine like Cake.me.
Analyze the following resume and job description.

Tasks:
- Evaluate the resume (score 0–100)
- Identify strengths, weaknesses, and actionable improvements
- Analyze 5 ATS categories: Content, Skills, Format, Sections, and Style
- Provide a short summary and overall feedback
- Finally, suggest 2–3 actionable recommendations to improve or learn new skills.

Return ONLY valid JSON strictly following this structure:
{{
  "summary": {{
    "overall_match": <int 0–100>,
    "overview_comment": "<string>",
    "strengths": ["<string>", ...],
    "improvements": ["<string>", ...]
  }},
  "content": {{ "score": <int>, "measurable_results": [...], "grammar_issues": [...], "tips": [...] }},
  "skills": {{ "score": <int>, "technical": {{"matched": [...], "missing": [...]}}, "soft": {{"missing": [...]}}, "tips": [...] }},
  "format": {{ "score": <int>, "checks": {{"date_format": "<PASS|FAIL>", "length": "<PASS|FAIL>", "bullet_points": "<PASS|FAIL>"}}, "tips": [...] }},
  "sections": {{ "score": <int>, "missing": [...], "tips": [...] }},
  "style": {{ "score": <int>, "tone": [...], "buzzwords": [...], "tips": [...] }},
  "recommendations": {{ "items": ["<string>", "<string>", "<string>"] }},
  "overall_score": <int>,
  "overall_comment": "<string>"
}}

Now analyze the following content carefully:

--- RESUME ---
{cv_text[:4000]}

--- JOB DESCRIPTION ---
{job_description[:4000]}
"""

    # 4️⃣ Run Gemini API
    model = genai.GenerativeModel(MODEL_NAME)

    # 📊 Count input tokens
    token_count = model.count_tokens(prompt)
    input_tokens = token_count.total_tokens
    print(f"📥 Input tokens: {input_tokens}")

    response = model.generate_content(prompt)
    raw_text = (response.text or "").strip()

    # 📊 Count output tokens
    output_tokens = response.usage_metadata.candidates_token_count if hasattr(response, 'usage_metadata') else 0
    total_tokens = response.usage_metadata.total_token_count if hasattr(response, 'usage_metadata') else 0

    print(f"📤 Output tokens: {output_tokens}")
    print(f"📊 Total tokens: {total_tokens}")
    print(f"💰 Token breakdown - Prompt: {input_tokens}, Completion: {output_tokens}, Total: {total_tokens}")

    # 5️⃣ Clean and parse the JSON safely
    result = clean_json_output.clean_json_output(raw_text)

    # 6️⃣ Inject static explanations into each ATS field
    for key, desc in FIELD_EXPLANATIONS.items():
        if key in result:
            result[key]["description"] = desc
        else:
            result[key] = {"description": desc}

    # 7️⃣ Ensure recommendations section exists
    if "recommendations" not in result:
        result["recommendations"] = {"items": []}
    result["recommendations"].update(RECOMMENDATION_HEADER)

    # 8️⃣ Include structured CV for reference/debug
    result["structured_resume"] = cv_json

    # 9️⃣ Add token usage info to result
    result["token_usage"] = {
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": total_tokens
    }

    return result
