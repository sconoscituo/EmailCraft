from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, func
from app.database import Base


class GenerationLog(Base):
    __tablename__ = "generation_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    prompt_summary = Column(String(500), nullable=True)
    purpose = Column(String(500), nullable=True)
    recipient = Column(String(200), nullable=True)
    tone = Column(String(50), nullable=True)
    language = Column(String(10), default="ko")
    generated_email = Column(Text, nullable=True)
    subject = Column(String(300), nullable=True)
    cta = Column(String(300), nullable=True)
    is_variant = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
