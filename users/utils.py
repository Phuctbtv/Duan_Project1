import base64
import json

import requests
from django.conf import settings

API_TIMEOUT = 15

def process_ocr_cccd(image_file):
    """
    Hàm utility tối ưu tốc độ để xử lý OCR CCCD bằng một lần gọi Gemini API.
    """
    if not image_file:
        return {"success": False, "error": "No image uploaded"}

    image_type = image_file.content_type
    allowed_types = ["image/jpeg", "image/png", "image/webp"]

    if image_type not in allowed_types:
        return {
            "success": False,
            "error": f"Invalid image type: {image_type}. Only JPEG, PNG, or WebP are allowed."
        }

    # Đọc tệp và mã hóa Base64
    try:
        image_base64 = base64.b64encode(image_file.read()).decode("utf-8")
    except Exception as e:
        return {"success": False, "error": f"Lỗi đọc tệp ảnh: {str(e)}"}

    GEMINI_API_KEY = settings.GEMINI_API_KEY

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"

    # 1. GỘP CẢ XÁC MINH VÀ TRÍCH XUẤT VÀO MỘT LẦN GỌI
    unified_payload = {
        "contents": [{
            "parts": [
                {
                    "text": (
                        "Đầu tiên, xác minh ảnh này có phải là Căn cước công dân Việt Nam (mặt trước hoặc mặt sau) không. "
                        "Chỉ trả về DẠNG JSON thuần. "
                        "Nếu KHÔNG phải CCCD, JSON phải có trường: {'is_cccd': false}. "
                        "Nếu LÀ CCCD, JSON phải có trường: {'is_cccd': true, ...}. "
                        "Trong trường hợp LÀ CCCD, trích xuất thêm các trường sau: "
                        "'ho_va_ten_dem', 'ten', 'id_number', 'gioi_tinh', "
                        "'date_of_birth' (theo định dạng YYYY-MM-DD), 'address'. "
                        "Tuyệt đối KHÔNG thêm mô tả hoặc ký tự khác ngoài JSON."
                    )
                },
                {
                    "inline_data": {"mime_type": image_type, "data": image_base64}
                }
            ]
        }]
    }

    try:

        res = requests.post(url, json=unified_payload, timeout=API_TIMEOUT)
        data = res.json()

        if "candidates" not in data:
            error_message = data.get("error", {}).get("message", "Gemini không phản hồi hợp lệ")
            return {
                "success": False,
                "error": f"Lỗi Gemini API: {error_message}",
                "raw_response": data
            }

        text = data["candidates"][0]["content"]["parts"][0]["text"].strip()

        # Xử lý dọn dẹp JSON
        if text.startswith("```json"):
            text = text.replace("```json", "").replace("```", "").strip()

        if not text.startswith("{") or not text.endswith("}"):
            raise ValueError("Phản hồi không phải JSON hợp lệ")

        result = json.loads(text)

        # 2. Xử lý kết quả Xác minh (Verification)
        if not result.get("is_cccd", False):
            return {
                "success": False,
                "error": "Ảnh tải lên không phải là Căn cước công dân Việt Nam. Vui lòng thử lại."
            }

        # 3. Xử lý kết quả Trích xuất (Extraction)
        required_fields = ["id_number", "gioi_tinh", "date_of_birth"]
        missing = [f for f in required_fields if not result.get(f)]
        if missing:
            return {
                "success": False,
                "error": "Ảnh CCCD không đủ thông tin để nhận diện. Hãy thử ảnh rõ nét hơn."
            }

        return {
            "success": True,
            "data": {
                "first_name": result.get("ho_va_ten_dem"),
                "last_name": result.get("ten"),
                "id_number": result.get("id_number"),
                "gender": result.get("gioi_tinh"),
                "date_of_birth": result.get("date_of_birth"),
                "address": result.get("address")
            }
        }

    except json.JSONDecodeError:
        return {"success": False, "error": "OCR không trả về JSON hợp lệ."}
    except requests.exceptions.Timeout:
        return {"success": False, "error": f"Gemini API timeout sau {API_TIMEOUT} giây. Thử lại sau."}
    except Exception as e:
        return {"success": False, "error": str(e)}