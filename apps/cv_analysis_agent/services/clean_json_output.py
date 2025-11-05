import json
import re

def clean_json_output(text):
    """
    Chuẩn hóa và parse JSON từ output AI.
    - Hỗ trợ input dạng dict, list, str, bytes
    - Xóa markdown code fence (```json ... ```)
    - Bóc JSON đầu tiên trong chuỗi
    - Trả về dict/list, hoặc {"raw_text": "..."} nếu parse thất bại
    """
    # 🟢 Nếu model đã trả về JSON object
    if text is None:
        return {}
    if isinstance(text, (dict, list)):
        return text
    if isinstance(text, bytes):
        text = text.decode("utf-8", errors="ignore")

    # 🟡 Chuẩn hóa chuỗi
    text = str(text).strip()
    # Xóa code block kiểu ```json ... ```
    text = re.sub(r"^```(?:json)?", "", text, flags=re.IGNORECASE).strip()
    text = text.replace("```", "").strip()
    # Xóa mấy prefix kiểu “Here’s the JSON: …”
    text = re.sub(r"(?i)(here(\s+is|'s)?\s+the\s+json:?|json\s*output:?|formatted\s*json:?|sure[:,]?\s*)", "", text).strip()

    # 🧩 Thử tìm JSON trong chuỗi
    match = re.search(r"(\{[\s\S]*\}|\[[\s\S]*\])", text)
    if match:
        candidate = match.group(1)
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            pass  # thử parse toàn bộ chuỗi ở dưới

    # 🧠 Thử parse toàn bộ chuỗi
    try:
        return json.loads(text)
    except Exception:
        pass

    # 🔴 Fallback: trả text thô
    return {"raw_text": text}
