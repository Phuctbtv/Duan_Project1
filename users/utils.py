import base64
import json

import requests
from django.conf import settings

def process_ocr_cccd(image_file):
    """
    Hàm utility để xử lý OCR CCCD
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

    image_base64 = base64.b64encode(image_file.read()).decode("utf-8")
    GEMINI_API_KEY = settings.GEMINI_API_KEY
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro:generateContent?key={GEMINI_API_KEY}"

    # Xác minh loại ảnh
    verify_payload = {
        "contents": [{
            "parts": [
                {
                    "text": (
                        "Ảnh này có phải là Căn cước công dân Việt Nam (mặt trước hoặc mặt sau) không? "
                        "Chỉ trả về JSON dạng: {'is_cccd': true hoặc false}."
                    )
                },
                {
                    "inline_data": {"mime_type": image_type, "data": image_base64}
                }
            ]
        }]
    }

    try:
        verify_res = requests.post(url, json=verify_payload, timeout=20)
        verify_data = verify_res.json()
        verify_text = verify_data["candidates"][0]["content"]["parts"][0]["text"].strip()

        if verify_text.startswith("```json"):
            verify_text = verify_text.replace("```json", "").replace("```", "").strip()

        # Parse kết quả xác minh
        try:
            verify_result = json.loads(verify_text)
            if not verify_result.get("is_cccd", False):
                return {
                    "success": False,
                    "error": "Ảnh tải lên không phải là Căn cước công dân Việt Nam. Vui lòng thử lại."
                }
        except Exception:
            return {
                "success": False,
                "error": "Không thể xác minh loại ảnh. Hãy tải lên ảnh CCCD mặt trước hoặc sau."
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Lỗi khi xác minh loại ảnh: {str(e)}"
        }

    # Trích xuất thông tin OCR
    extract_payload = {
        "contents": [{
            "parts": [
                {
                    "text": (
                        "Trích xuất thông tin từ ảnh CCCD và trả về DẠNG JSON thuần. "
                        "Các trường cần có: "
                        "'ho_va_ten_dem', 'ten', 'id_number', 'gioi_tinh', "
                        "'date_of_birth' (YYYY-MM-DD), 'address'. "
                        "Không thêm mô tả khác ngoài JSON."
                    )
                },
                {
                    "inline_data": {"mime_type": image_type, "data": image_base64}
                }
            ]
        }]
    }

    try:
        res = requests.post(url, json=extract_payload, timeout=30)
        data = res.json()

        if "candidates" not in data:
            return {
                "success": False,
                "error": data.get("error", {}).get("message", "Gemini không phản hồi hợp lệ"),
                "raw_response": data
            }

        text = data["candidates"][0]["content"]["parts"][0]["text"].strip()

        if text.startswith("```json"):
            text = text.replace("```json", "").replace("```", "").strip()

        if not text.startswith("{") or not text.endswith("}"):
            raise ValueError("Phản hồi không phải JSON hợp lệ")

        result = json.loads(text)

        # ✅ Kiểm tra các trường bắt buộc
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
        return {"success": False, "error": "Gemini API timeout. Thử lại sau."}
    except Exception as e:
        return {"success": False, "error": str(e)}