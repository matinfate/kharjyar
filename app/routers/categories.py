from fastapi import  APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.sql import crud

from app import models, schemas
from app.database import get_db

router = APIRouter(prefix="/categories", tags=["categories"])

@router.post("/", response_model=schemas.CategoryRead, status_code=200)
def create_category(data: schemas.CategoryCreate, db: Session = Depends(get_db)):
    existing = db.query(models.Category).filter_by(name=data.name).first()
    if existing:
        raise HTTPException(status_code=409, detail="Category already exists")

    category = models.Category(name=data.name)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category

@router.get("/", response_model=list[schemas.CategoryRead])
def list_categories(db: Session = Depends(get_db)):
    return db.query(models.Category).all()

@router.get("/{category_id}", response_model=schemas.CategoryRead)
def get_category(category_id: int, db: Session = Depends(get_db)):
    category = db.get(models.Category, category_id)
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return category