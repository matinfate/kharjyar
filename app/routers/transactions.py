from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.jalali import parse_jalali
from app.routers.categories import get_category_or_404

router = APIRouter(prefix="/transactions", tags=["transactions"])


def get_transaction_or_404(db: Session, transaction_id: int) -> models.Transaction:
    transaction = db.get(models.Transaction, transaction_id)
    if transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction


@router.post("/", response_model=schemas.TransactionRead, status_code=201)
def create_transaction(data: schemas.TransactionCreate, db: Session = Depends(get_db)):
    if data.category_id is not None:
        get_category_or_404(db, data.category_id)

    values = data.model_dump(exclude_none=True)
    if "jalali_date" in values:
        values["date"] = parse_jalali(values.pop("jalali_date"))

    transaction = models.Transaction(**values)
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction


@router.get("/", response_model=list[schemas.TransactionRead])
def list_transactions(type: models.TransactionType | None = None, category_id: int | None = None, db: Session = Depends(get_db)):
    query = db.query(models.Transaction)
    if type is not None:
        query = query.filter(models.Transaction.type == type)
    if category_id is not None:
        query = query.filter(models.Transaction.category_id == category_id)
    return query.all()


@router.get("/summary", response_model=schemas.Summary)
def get_summary(db: Session = Depends(get_db)):
    def total(transaction_type: models.TransactionType) -> int:
        result = (
            db.query(func.sum(models.Transaction.amount))
            .filter(models.Transaction.type == transaction_type)
            .scalar()
        )
        return result or 0

    income = total(models.TransactionType.income)
    expense = total(models.TransactionType.expense)
    return schemas.Summary(
        total_income=income,
        total_expense=expense,
        balance=income - expense,
    )


@router.get("/summary/by-category", response_model=list[schemas.CategoryTotal])
def get_expense_by_category(db: Session = Depends(get_db)):
    rows = (
        db.query(
            models.Category.id,
            models.Category.name,
            func.sum(models.Transaction.amount)
        )
        .select_from(models.Transaction)
        .outerjoin(
            models.Category, models.Transaction.category_id == models.Category.id
        )
        .filter(models.Transaction.type == models.TransactionType.expense)
        .group_by(models.Category.id, models.Category.name)
        .all()
    )
    return [
        schemas.CategoryTotal(category_id=cid, category_name=name, total=total)
        for cid, name, total in rows
    ]


@router.get("/{transaction_id}", response_model=schemas.TransactionRead)
def get_transaction(transaction_id: int, db: Session = Depends(get_db)):
    return get_transaction_or_404(db, transaction_id)


@router.delete("/{transaction_id}", status_code=204)
def delete_transaction(transaction_id: int, db: Session = Depends(get_db)):
    transaction = get_transaction_or_404(db, transaction_id)
    db.delete(transaction)
    db.commit()


@router.patch("/{transaction_id}", response_model=schemas.TransactionRead)
def update_transaction(transaction_id: int, data: schemas.TransactionUpdate, db: Session = Depends(get_db)):
    transaction = get_transaction_or_404(db, transaction_id)
    changes = data.model_dump(exclude_unset=True)

    if changes.get("category_id") is not None:
        get_category_or_404(db, changes["category_id"])

    for required in ("amount", "type", "date"):
        if required in changes and changes[required] is None:
            raise HTTPException(
                status_code=422, detail=f"{required} cannot be null"
            )

    for field, value in changes.items():
        setattr(transaction, field, value)

    db.commit()
    db.refresh(transaction)
    return transaction
