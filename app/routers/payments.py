from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from app.database import get_db
from app.models.user import User
from app.utils.auth import get_current_user
from app.services.payment import create_payment, activate_premium, get_payment_history
from app.config import get_settings

router = APIRouter(prefix="/api/payments", tags=["payments"])
settings = get_settings()


class PaymentRequest(BaseModel):
    payment_method: str = "card"
    transaction_id: str


@router.post("/subscribe")
async def subscribe(
    req: PaymentRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    payment = await create_payment(
        db,
        user_id=current_user.id,
        amount=settings.premium_monthly_price,
        payment_method=req.payment_method,
        transaction_id=req.transaction_id,
    )
    await activate_premium(db, current_user.id)
    return {"success": True, "message": "프리미엄 플랜이 활성화되었습니다", "payment_id": payment.id}


@router.get("/history")
async def payment_history(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    history = await get_payment_history(db, current_user.id)
    return {"success": True, "data": [
        {"id": p.id, "amount": p.amount, "status": p.status, "plan": p.plan, "created_at": str(p.created_at)}
        for p in history
    ]}
