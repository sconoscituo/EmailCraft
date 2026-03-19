from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional
from app.database import get_db
from app.models.user import User
from app.models.email_template import EmailTemplate
from app.models.generation_log import GenerationLog
from app.utils.auth import get_current_user
from app.services.generator import generate_email, generate_email_variants
from app.config import get_settings

router = APIRouter(prefix="/api/emails", tags=["emails"])
settings = get_settings()


class GenerateRequest(BaseModel):
    purpose: str
    recipient: str
    tone: str = "professional"
    language: str = "ko"
    context: str = ""


class VariantRequest(BaseModel):
    purpose: str
    recipient: str
    tone: str = "professional"
    language: str = "ko"
    count: int = 2


class TemplateCreate(BaseModel):
    title: str
    purpose: str
    tone: str = "professional"
    content: str
    subject: str = ""
    cta: str = ""
    language: str = "ko"
    is_public: bool = False


class TemplateResponse(BaseModel):
    id: int
    title: str
    purpose: str
    tone: str
    content: str
    subject: str | None
    cta: str | None
    language: str
    is_public: bool
    use_count: int

    class Config:
        from_attributes = True


async def _check_usage(db: AsyncSession, user: User):
    today = str(date.today())
    if user.last_usage_date != today:
        user.daily_usage = 0
        user.last_usage_date = today
    if not user.is_premium and user.daily_usage >= settings.free_daily_limit:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=f"무료 플랜은 하루 {settings.free_daily_limit}회까지 생성 가능합니다. 프리미엄으로 업그레이드하세요.",
        )
    user.daily_usage += 1
    await db.commit()


@router.post("/generate")
async def generate(
    req: GenerateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await _check_usage(db, current_user)
    result = await generate_email(req.purpose, req.recipient, req.tone, req.language, req.context)
    log = GenerationLog(
        user_id=current_user.id,
        prompt_summary=f"{req.purpose[:100]}",
        purpose=req.purpose,
        recipient=req.recipient,
        tone=req.tone,
        language=req.language,
        generated_email=result.get("body", ""),
        subject=result.get("subject", ""),
        cta=result.get("cta", ""),
    )
    db.add(log)
    await db.commit()
    return {"success": True, "data": result}


@router.post("/variants")
async def generate_variants(
    req: VariantRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await _check_usage(db, current_user)
    variants = await generate_email_variants(req.purpose, req.recipient, req.tone, req.language, req.count)
    return {"success": True, "data": variants}


@router.post("/templates", response_model=TemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_template(
    body: TemplateCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    tmpl = EmailTemplate(user_id=current_user.id, **body.model_dump())
    db.add(tmpl)
    await db.commit()
    await db.refresh(tmpl)
    return tmpl


@router.get("/templates", response_model=list[TemplateResponse])
async def list_templates(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(EmailTemplate).where(EmailTemplate.user_id == current_user.id).order_by(EmailTemplate.created_at.desc())
    )
    return result.scalars().all()


@router.get("/templates/{template_id}", response_model=TemplateResponse)
async def get_template(
    template_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(EmailTemplate).where(EmailTemplate.id == template_id))
    tmpl = result.scalar_one_or_none()
    if not tmpl or (tmpl.user_id != current_user.id and not tmpl.is_public):
        raise HTTPException(status_code=404, detail="템플릿을 찾을 수 없습니다")
    return tmpl


@router.put("/templates/{template_id}", response_model=TemplateResponse)
async def update_template(
    template_id: int,
    body: TemplateCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(EmailTemplate).where(EmailTemplate.id == template_id))
    tmpl = result.scalar_one_or_none()
    if not tmpl or tmpl.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="템플릿을 찾을 수 없습니다")
    for k, v in body.model_dump().items():
        setattr(tmpl, k, v)
    await db.commit()
    await db.refresh(tmpl)
    return tmpl


@router.delete("/templates/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_template(
    template_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(EmailTemplate).where(EmailTemplate.id == template_id))
    tmpl = result.scalar_one_or_none()
    if not tmpl or tmpl.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="템플릿을 찾을 수 없습니다")
    await db.delete(tmpl)
    await db.commit()


@router.get("/history")
async def get_history(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(GenerationLog).where(GenerationLog.user_id == current_user.id).order_by(GenerationLog.created_at.desc()).limit(50)
    )
    logs = result.scalars().all()
    return {"success": True, "data": [
        {"id": l.id, "purpose": l.purpose, "subject": l.subject, "created_at": str(l.created_at)}
        for l in logs
    ]}
