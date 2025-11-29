"""
Embedding Service - Handles text embedding generation using Gemini API
"""
import os
import numpy as np
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

# Initialize Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


def get_gemini_embedding(text: str):
    """
    Generate vector embedding using Gemini (text-embedding-004)

    Args:
        text: Input text to embed

    Returns:
        list[float]: Vector embedding or None if text is empty
    """
    text = (text or "").strip()
    if not text:
        return None

    response = genai.embed_content(
        model="models/text-embedding-004",
        content=text
    )

    return np.array(response['embedding'], dtype=np.float32).tolist()


def combine_weighted_text(query_item: dict, weights: dict = None) -> str:
    """
    Combine query fields into weighted text for embedding

    Args:
        query_item: Dict with skills, title, description
        weights: Field weights (default: skills=0.4, title=0.4, description=0.2)

    Returns:
        str: Combined weighted text
    """
    if weights is None:
        weights = {"skills": 0.4, "title": 0.4, "description": 0.2}

    def to_text(v):
        if isinstance(v, list):
            return ", ".join(str(x) for x in v)
        return str(v or "")

    skills_text = to_text(query_item.get("skills", ""))
    title_text = to_text(query_item.get("title", ""))
    description_text = to_text(query_item.get("description", ""))

    # Repeat important fields to increase their weight
    combined_parts = []
    if skills_text:
        combined_parts.extend([skills_text] * int(weights.get("skills", 0.4) * 10))
    if title_text:
        combined_parts.extend([title_text] * int(weights.get("title", 0.4) * 10))
    if description_text:
        combined_parts.extend([description_text] * int(weights.get("description", 0.2) * 10))

    return " ".join(combined_parts)

