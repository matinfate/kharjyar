from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.security import hash_password

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=schemas.UserRead, status_code=201)
def register(data: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(
        models.User.username == data.username).first()
    if existing is not None:
        raise HTTPException(status_code=409, detail="Username already exists")

    user = models.User(
        username=data.username,
        hashed_password=hash_password(data.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
