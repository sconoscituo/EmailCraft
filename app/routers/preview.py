"""
이메일 미리보기 + A/B 테스트 라우터
"""
import json
import google.generativeai as genai
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from app.utils.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/preview", tags=["이메일 미리보기"])

try:
    from app.config import config
    GEMINI_KEY = config.GEMINI_API_KEY
except Exception:
    GEMINI_KEY = ""


class EmailPreviewRequest(BaseModel):
    subject: str
    body: str
    recipient_name: Optional[str] = "고객"


class ABTestRequest(BaseModel):
    topic: str
    target_audience: str
    goal: str  # 클릭률 향상, 오픈율 향상 등


@router.post("/render")
async def preview_email(request: EmailPreviewRequest):
    """이메일 미리보기 생성 (HTML 렌더링)"""
    html = f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><style>
body{{font-family:Arial,sans-serif;max-width:600px;margin:0 auto;padding:20px;}}
.header{{background:#4F46E5;color:white;padding:20px;border-radius:8px 8px 0 0;}}
.body{{background:#f9f9f9;padding:20px;border:1px solid #e0e0e0;}}
.footer{{background:#eee;padding:10px;font-size:12px;color:#888;border-radius:0 0 8px 8px;}}
</style></head>
<body>
<div class="header"><h2>{request.subject}</h2></div>
<div class="body"><p>안녕하세요, {request.recipient_name}님</p>{request.body.replace(chr(10), '<br>')}</div>
<div class="footer">수신거부는 여기를 클릭하세요</div>
</body></html>"""

    return {
        "subject": request.subject,
        "html_preview": html,
        "char_count": len(request.body),
        "estimated_read_time": f"{max(1, len(request.body.split()) // 200)}분",
    }


@router.post("/ab-test")
async def generate_ab_variants(
    request: ABTestRequest,
    current_user: User = Depends(get_current_user),
):
    """A/B 테스트용 이메일 제목 변형 생성"""
    if not GEMINI_KEY:
        raise HTTPException(500, "AI 서비스 설정이 필요합니다")

    genai.configure(api_key=GEMINI_KEY)
    model = genai.GenerativeModel("gemini-1.5-flash")

    prompt = f"""다음 이메일 캠페인을 위한 A/B 테스트 제목 3개를 만들어줘.

주제: {request.topic}
대상: {request.target_audience}
목표: {request.goal}

각 변형은 다른 접근법 사용:
A: 호기심 유발
B: 혜택 강조
C: 긴급성 강조

JSON으로 반환:
[
  {{"variant": "A", "subject": "제목A", "approach": "호기심 유발", "expected_open_rate": "높음"}},
  {{"variant": "B", "subject": "제목B", "approach": "혜택 강조", "expected_open_rate": "중간"}},
  {{"variant": "C", "subject": "제목C", "approach": "긴급성", "expected_open_rate": "높음"}}
]"""

    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        if text.startswith("```"):
            text = text[text.find("["):text.rfind("]") + 1]
        variants = json.loads(text)
        return {"topic": request.topic, "variants": variants}
    except Exception:
        raise HTTPException(500, "A/B 테스트 생성 중 오류")
