# apps/cv_creation_agent/services/analyzer_service.py
import io
import os
import re

import fitz  # PyMuPDF
import docx2txt
import pytesseract
from PIL import Image
from sklearn.feature_extraction.text import TfidfVectorizer

pytesseract_path = os.environ["TESSERACT_PATH"]
pytesseract.pytesseract.tesseract_cmd = pytesseract_path

# Initialize TfidfVectorizer with stopwords removal
tfidf_vectorizer = TfidfVectorizer(
    stop_words='english',  # Remove common English stopwords like 'a', 'an', 'the', etc.
    lowercase=True,
    token_pattern=r'\b[a-zA-Z]{2,}\b'  # Only keep words with 2+ letters
)


def remove_stopwords_tfidf(text):
    """
    Remove stopwords and extract meaningful terms using TfidfVectorizer.
    This is more sophisticated than simple stopword removal as it:
    - Removes common words like 'a', 'an', 'the', 'is', 'are', etc.
    - Removes punctuation and special characters
    - Keeps only alphabetic words with 2+ characters
    - Preserves word order
    """
    if not text or not text.strip():
        return ""

    # Get feature names (valid tokens after stopword removal)
    try:
        tfidf_vectorizer.fit([text])
        feature_names = tfidf_vectorizer.get_feature_names_out()

        # Create a set for fast lookup
        valid_words = set(feature_names)

        # Tokenize original text and keep only valid words (preserving order)
        words = re.findall(r'\b[a-zA-Z]{2,}\b', text.lower())
        filtered_words = [word for word in words if word in valid_words]

        return ' '.join(filtered_words)
    except Exception:
        # Fallback: just lowercase and remove short words
        words = re.findall(r'\b[a-zA-Z]{2,}\b', text.lower())
        return ' '.join(words)


def extract_text(file):
    """
    Extract plain text content from uploaded file.
    Supports PDF (via PyMuPDF) and DOCX (via docx2txt).
    Falls back to Tesseract OCR if PDF is scanned.
    Automatically removes stopwords using TfidfVectorizer.
    Returns UTF-8 string.
    """

    filename = file.name.lower()

    # ✅ Handle PDF
    if filename.endswith(".pdf"):
        text = ""
        try:
            # Reset file pointer to beginning before reading
            if hasattr(file, 'seek'):
                file.seek(0)

            pdf_bytes = file.read()

            # Reset file pointer after reading so it can be read again if needed
            if hasattr(file, 'seek'):
                file.seek(0)

            with fitz.open(stream=io.BytesIO(pdf_bytes), filetype="pdf") as doc:
                for page in doc:
                    page_text = page.get_text("text")
                    text += page_text

                # Nếu toàn bộ PDF không có text => có thể là scanned PDF
                if not text.strip():
                    ocr_text = ""
                    for page_index, page in enumerate(doc):
                        # render page thành ảnh
                        pix = page.get_pixmap(dpi=300)
                        img = Image.open(io.BytesIO(pix.tobytes("png")))
                        # OCR
                        ocr_text += pytesseract.image_to_string(img, lang="eng+vie")

                    text = ocr_text

            text = text.strip()
            return remove_stopwords_tfidf(text)

        except Exception as e:
            raise ValueError(f"PDF parsing failed: {e}")

    # ✅ Handle DOCX
    elif filename.endswith(".docx"):
        try:
            # Reset file pointer to beginning before reading
            if hasattr(file, 'seek'):
                file.seek(0)

            text = docx2txt.process(file)

            # Reset file pointer after reading
            if hasattr(file, 'seek'):
                file.seek(0)

            return remove_stopwords_tfidf(text)
        except Exception as e:
            raise ValueError(f"DOCX parsing failed: {e}")

    # ✅ Fallback for TXT or others
    try:
        text = file.read().decode("utf-8", errors="ignore")
        return remove_stopwords_tfidf(text)
    except Exception:
        return ""
