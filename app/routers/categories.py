from fastapi import  APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.sql import crud

from app import models, schemas
from app.database import get_db

router = APIRouter(prefix="/categories", tags=["categories"])

def get_category_or_404(db: Session, category_id: int) -> models.Category:
    category = db.get(models.Category, category_id)
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return category

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
    return get_category_or_404(db, category_id)

@router.delete("/{category_id}", status_code=204)
def delete_category(category_id: int, db: Session = Depends(get_db)):
    category = get_category_or_404(db, category_id)
    db.delete(category)
    db.commit()