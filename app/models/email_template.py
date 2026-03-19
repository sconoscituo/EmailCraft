from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, func
from app.database import Base


class EmailTemplate(Base):
    __tablename__ = "email_templates"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    purpose = Column(String(500), nullable=False)
    tone = Column(String(50), nullable=False, default="professional")
    content = Column(Text, nullable=False)
    subject = Column(String(300), nullable=True)
    cta = Column(String(300), nullable=True)
    language = Column(String(10), default="ko")
    is_public = Column(Boolean, default=False)
    use_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
