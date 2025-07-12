from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import uuid

from app.crypto import encrypt_secret
from app.db import SessionLocal
from sqlalchemy.orm import Session
from app import models


router = APIRouter()

class SecretRequest(BaseModel):
    secret: str
    expire_after_minutes: int
    password: str | None = None

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/secret")
def create_secret(req: SecretRequest, db: Session = Depends(get_db)):
    secret_id = str(uuid.uuid4())
    encrypted_secret = encrypt_secret(req.secret)

    # Save to DB
    db_secret = models.Secret(
        id=secret_id,
        encrypted_secret=encrypted_secret,
        password_hash=None,  # implement bcrypt later
        expire_after_minutes=req.expire_after_minutes
    )
    db.add(db_secret)
    db.commit()
    return {"url": f"http://localhost:8000/secret/{secret_id}"}