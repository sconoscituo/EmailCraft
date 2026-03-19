from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from app.database import Base


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    amount = Column(Integer, nullable=False)
    currency = Column(String(10), default="KRW")
    status = Column(String(50), default="pending")
    plan = Column(String(50), default="premium_monthly")
    payment_method = Column(String(50), nullable=True)
    transaction_id = Column(String(200), nullable=True, unique=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
