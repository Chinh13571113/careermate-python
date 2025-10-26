import os, numpy as np, google.generativeai as genai

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def gemini_embed(text: str) -> np.ndarray:
    """Sinh embedding từ Gemini (semantic vector 768 chiều)."""
    text = (text or "").strip().replace("\n", " ")
    if not text:
        return np.zeros(768)
    resp = genai.embed_content(
        model="models/embedding-001",
        content=text,
        task_type="semantic_similarity",
    )
    return np.array(resp["embedding"], dtype=float)
