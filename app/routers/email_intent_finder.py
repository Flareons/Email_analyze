# app/routers/email_intent_finder.py

import base64
from typing import Dict, List, Optional

from fastapi import APIRouter, Request
from pydantic import BaseModel

from app.model.attachment_model import analyze_attachment
from app.model.intent_model import intent_email
from app.model.sumarize_model import sumarize_email

router = APIRouter(
    prefix="/email_intent_finder",
    tags=["Email intent analysis"],
)


class EmailRequest(BaseModel):
    email: str
    attachment: Optional[List[Dict]] = None


@router.post("/email")
async def analyze_email(request: Request, req: List[EmailRequest]):
    """
    Nhận một danh sách EmailRequest, mỗi email có thể kèm attachments (list of dict).
    Trả về list kết quả gồm intent, sumarize và attachments (phân tích).
    """
    client = request.app.state.gemini_client
    results = []

    for e in req:
        if e.attachment:
            imgs: List[bytes] = []
            mime_types: List[str] = []

            for b64_img in e.attachment:
                # Lấy chuỗi Base64; nếu có prefix "data:...;base64," thì loại bỏ
                raw_b64 = b64_img.get("base_64_str", "")
                if not raw_b64:
                    continue

                if "," in raw_b64:
                    _, raw_b64 = raw_b64.split(",", 1)

                # decode base64 -> bytes
                try:
                    img_bytes = base64.b64decode(raw_b64)
                except Exception:
                    # Nếu decode thất bại, bỏ file đó qua (giữ logic: không dừng toàn bộ request)
                    continue

                imgs.append(img_bytes)
                mime_types.append(b64_img.get("mime_type", "application/octet-stream"))

            # Gọi hàm phân tích attachment (giữ nguyên signature bạn đã dùng)
            attachment_analyze = analyze_attachment(imgs, e.email, mime_types, client)
            sumarize = sumarize_email(e.email, client, attachment_analyze)
        else:
            attachment_analyze = "Email không có tệp đính kèm"
            sumarize = sumarize_email(e.email, client)

        intent = intent_email(e.email, client)
        results.append(
            {
                "intent": intent,
                "sumarize": sumarize,
                "attachments": attachment_analyze,
            }
        )

    return results


# @router.get("/")
# async def test():
#     return "Hello World"
