# apps/cv_creation_agent/services/analyzer_service.py
import json
import re
from functools import lru_cache

from agent_core.llm import get_openai_model
from agent_core.prompts import extract_resume_prompts
from apps.cv_analysis_agent.services.extract_text import extract_text


# Cache model instances to avoid recreation overhead
@lru_cache(maxsize=2)
def get_cached_model(temperature: float):
    """Cache model instances for reuse"""
    return get_openai_model(temperature=temperature)


def extract_json_from_response(response: str) -> str:
    """Extract JSON from a response that may contain markdown or extra text."""
    if not response or not response.strip():
        raise ValueError("Model returned empty response")

    response = response.strip()

    # Try to find JSON in markdown code blocks first (most common case)
    json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response, re.DOTALL)
    if json_match:
        return json_match.group(1).strip()

    # Fast path: check if it's already valid JSON
    if response.startswith('{') and response.endswith('}'):
        try:
            json.loads(response)
            return response
        except json.JSONDecodeError:
            pass

    # Try to find JSON object directly (first occurrence)
    json_match = re.search(r'\{.*\}', response, re.DOTALL)
    if json_match:
        potential_json = json_match.group(0).strip()
        try:
            json.loads(potential_json)
            return potential_json
        except json.JSONDecodeError:
            pass

    raise ValueError(f"No valid JSON found in response: {response[:200]}")


def analyze_resume_text(text: str) -> dict:
    if not text or not text.strip():
        raise ValueError("Cannot analyze empty resume text. PDF extraction may have failed.")

    text = text.strip()
    if len(text) < 50:
        raise ValueError(f"Resume text too short ({len(text)} chars). May not contain valid resume content.")

    # Use cached model for better performance
    model = get_cached_model(temperature=0.1)

    # Streamlined prompt - system instruction + user content
    full_prompt = f"""{extract_resume_prompts.SYSTEM_PROMPT}

            Extract fields from this resume:

            {text}

            Return ONLY valid JSON."""

    response = model.invoke(full_prompt)

    # LangChain returns AIMessage object, get the content
    response_text = response.content if hasattr(response, 'content') else str(response)

    # Debug: Check if response is empty
    if not response_text:
        raise ValueError("Model returned None or empty string. Check API key and model configuration.")
    # return response_text
    try:
        json_str = extract_json_from_response(response_text)
        parsed = json.loads(json_str)
        return parsed
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON response from model. Response preview: {response_text[:500]}") from e




def analyze_resume_sync(file) -> dict:
    """
    Synchronously analyze a resume file.
    Returns structured data and feedback.
    """
    # Step 1: Extract text from PDF
    text = extract_text(file)
    # Step 2: Extract structured information
    structured = analyze_resume_text(text)
    print("feedback data:", type(structured))
    return {
        "result": structured,
    }






