import base64
import io
from celery import shared_task
from .services.extract_text import extract_text
from .services.analyzer_service import analyze_resume_text


class FileWrapper:
    """Wrapper class to mimic file object with name attribute"""
    def __init__(self, content: bytes, name: str):
        self._buffer = io.BytesIO(content)
        self.name = name

    def read(self):
        return self._buffer.read()

    def seek(self, pos):
        return self._buffer.seek(pos)


@shared_task(bind=True, max_retries=2)
def process_resume_task(self, file_content_b64: str, filename: str) -> dict:
    try:
        # Decode base64 content
        file_content = base64.b64decode(file_content_b64)

        # Create file-like object
        file_obj = FileWrapper(file_content, filename)

        text = extract_text(file_obj)
        print("text extracted:", text)

        structured = analyze_resume_text(text)

        return {
            "result": structured
        }
    except Exception as e:
        raise self.retry(exc=e, countdown=10)
