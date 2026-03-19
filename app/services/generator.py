import json
import re
from typing import Optional
import google.generativeai as genai
from app.config import get_settings

settings = get_settings()


def _init_genai():
    if settings.gemini_api_key:
        genai.configure(api_key=settings.gemini_api_key)


async def generate_email(
    purpose: str,
    recipient: str,
    tone: str,
    language: str = "ko",
    context: str = "",
) -> dict:
    """AI 이메일 생성"""
    _init_genai()
    model = genai.GenerativeModel("gemini-1.5-flash")
    tone_map = {
        "formal": "격식체",
        "casual": "친근한",
        "professional": "전문적인",
        "persuasive": "설득력있는",
    }
    lang_map = {"ko": "한국어", "en": "English", "ja": "日本語"}
    prompt = f"""이메일을 작성해주세요.

목적: {purpose}
수신자: {recipient}
톤: {tone_map.get(tone, tone)}
언어: {lang_map.get(language, "한국어")}
{f"추가 컨텍스트: {context}" if context else ""}

JSON 형식으로만 응답하세요:
{{"subject": "제목", "body": "본문 전체", "cta": "행동 유도 문구"}}"""

    response = model.generate_content(prompt)
    match = re.search(r"\{.*\}", response.text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass
    return {"subject": "", "body": response.text, "cta": ""}


async def generate_email_variants(
    purpose: str,
    recipient: str,
    tone: str,
    language: str = "ko",
    count: int = 2,
) -> list[dict]:
    """A/B 테스트용 이메일 변형 생성"""
    _init_genai()
    model = genai.GenerativeModel("gemini-1.5-flash")
    tone_map = {
        "formal": "격식체",
        "casual": "친근한",
        "professional": "전문적인",
        "persuasive": "설득력있는",
    }
    lang_map = {"ko": "한국어", "en": "English", "ja": "日本語"}
    prompt = f"""A/B 테스트를 위해 이메일 {count}가지 변형을 작성해주세요.

목적: {purpose}
수신자: {recipient}
톤: {tone_map.get(tone, tone)}
언어: {lang_map.get(language, "한국어")}

각각 다른 접근 방식으로 작성하고 JSON 배열로만 응답하세요:
[
  {{"variant": "A", "subject": "제목A", "body": "본문A", "cta": "CTA_A"}},
  {{"variant": "B", "subject": "제목B", "body": "본문B", "cta": "CTA_B"}}
]"""

    response = model.generate_content(prompt)
    match = re.search(r"\[.*\]", response.text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass
    return []
