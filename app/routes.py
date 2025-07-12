from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import uuid
from uuid import UUID
from app.crypto import encrypt_secret, decrypt_secret
from app.db import SessionLocal
from sqlalchemy.orm import Session
from app import models
from datetime import datetime, timedelta


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

@router.get("/secret/{secret_id}")
def get_secret(secret_id: str, db: Session = Depends(get_db)):
    secret = db.query(models.Secret).filter(models.Secret.id == secret_id).first()

    if not secret:
        raise HTTPException(status_code=404, detail="Secret not found")
    
    if secret.expire_after_minutes > 0 and datetime.now() - secret.created_at > timedelta(minutes=secret.expire_after_minutes):
        db.delete(secret)
        db.commit()
        raise HTTPException(status_code=410, detail="Secret has expired")
    
    try:
        plain_text = decrypt_secret(secret.encrypted_secret)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to decrypt secret: {str(e)}")
    
    return {
        "secret": plain_text
    }