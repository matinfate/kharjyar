from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.dependencies import get_current_user

router = APIRouter(prefix="/categories", tags=["categories"])


def get_category_or_404(
    db: Session,
    category_id: int,
    user_id: int | None = None
) -> models.Category:
    query = db.query(models.Category).filter(models.Category.id == category_id)
    if user_id is not None:
        query = query.filter(models.Category.user_id == user_id)

    category = query.first()
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.post("/", response_model=schemas.CategoryRead, status_code=201)
def create_category(
    data: schemas.CategoryCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    existing = (
        db.query(models.Category)
        .filter(
            models.Category.user_id == current_user.id,
            models.Category.name == data.name,
        )
        .first()
    )
    if existing:
        raise HTTPException(status_code=409, detail="Category already exists")

    category = models.Category(name=data.name, user_id=current_user.id)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@router.get("/", response_model=list[schemas.CategoryRead])
def list_categories(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return (
        db.query(models.Category)
        .filter(models.Category.user_id == current_user.id)
        .all()
    )


@router.get("/{category_id}", response_model=schemas.CategoryRead)
def get_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return get_category_or_404(db, category_id, current_user.id)


@router.delete("/{category_id}", status_code=204)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    category = get_category_or_404(db, category_id, current_user.id)

    has_transactions = (db.query(models.Transaction).filter_by(
        category_id=category_id).first())

    if has_transactions is not None:
        raise HTTPException(
            status_code=409, detail="Category has transactions and cannot be deleted")

    db.delete(category)
    db.commit()
