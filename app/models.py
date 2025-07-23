from sqlalchemy import Column, String, Integer, Boolean, DateTime
from app.db import Base
from datetime import datetime, timezone
class Secret(Base):
    __tablename__ = "secrets"

    id = Column(String, primary_key=True, index=True)  # UUID or token
    encrypted_secret = Column(String, nullable=False)
    password_hash = Column(String, nullable=True)
    expire_after_minutes = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    viewed = Column(Boolean, default=False)
