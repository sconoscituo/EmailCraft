from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.models.payment import Payment


async def create_payment(
    db: AsyncSession,
    user_id: int,
    amount: int,
    plan: str = "premium_monthly",
    payment_method: str = "card",
    transaction_id: str = None,
) -> Payment:
    payment = Payment(
        user_id=user_id,
        amount=amount,
        plan=plan,
        payment_method=payment_method,
        transaction_id=transaction_id,
        status="completed",
        expires_at=datetime.utcnow() + timedelta(days=30),
    )
    db.add(payment)
    await db.commit()
    await db.refresh(payment)
    return payment


async def activate_premium(db: AsyncSession, user_id: int) -> User:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user:
        user.is_premium = True
        await db.commit()
        await db.refresh(user)
    return user


async def get_payment_history(db: AsyncSession, user_id: int) -> list[Payment]:
    result = await db.execute(
        select(Payment).where(Payment.user_id == user_id).order_by(Payment.created_at.desc())
    )
    return result.scalars().all()
