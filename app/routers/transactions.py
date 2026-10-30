import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.dependencies import get_current_user
from app.jalali import month_range, parse_jalali
from app.routers.categories import get_category_or_404

router = APIRouter(prefix="/transactions", tags=["transactions"])


def get_transaction_or_404(
    db: Session,
    transaction_id: int,
    user_id: int | None = None
) -> models.Transaction:
    query = db.query(models.Transaction).filter(
        models.Transaction.id == transaction_id
    )
    if user_id is not None:
        query = query.filter(models.Transaction.user_id == user_id)

    transaction = query.first()
    if transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction


def jalali_or_422(value: str) -> datetime.date:
    try:
        return parse_jalali(value)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


def build_summary(
    db: Session,
    user_id: int,
    start=None,
    end=None,
) -> schemas.Summary:
    def total(transaction_type: models.TransactionType) -> int:
        query = db.query(func.sum(models.Transaction.amount)).filter(
            models.Transaction.type == transaction_type,
            models.Transaction.user_id == user_id,
        )

        if start is not None:
            query = query.filter(models.Transaction.date >= start)
        if end is not None:
            query = query.filter(models.Transaction.date <= end)
        return query.scalar() or 0

    income = total(models.TransactionType.income)
    expense = total(models.TransactionType.expense)
    return schemas.Summary(
        total_income=income,
        total_expense=expense,
        balance=income - expense,
    )


@router.post("/", response_model=schemas.TransactionRead, status_code=201)
def create_transaction(
    data: schemas.TransactionCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if data.category_id is not None:
        get_category_or_404(db, data.category_id, current_user.id)

    values = data.model_dump(exclude_none=True)
    if "jalali_date" in values:
        values["date"] = parse_jalali(values.pop("jalali_date"))

    transaction = models.Transaction(**values, user_id=current_user.id)
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction


@router.get("/", response_model=list[schemas.TransactionRead])
def list_transactions(
    type: models.TransactionType | None = None,
    category_id: int | None = None,
    from_jalali: str | None = None,
    to_jalali: str | None = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    query = db.query(models.Transaction).filter(
        models.Transaction.user_id == current_user.id
    )
    if type is not None:
        query = query.filter(models.Transaction.type == type)
    if category_id is not None:
        query = query.filter(models.Transaction.category_id == category_id)

    start = jalali_or_422(from_jalali) if from_jalali is not None else None
    end = jalali_or_422(to_jalali) if to_jalali is not None else None

    if start is not None and end is not None and start > end:
        raise HTTPException(
            status_code=422, detail="from_jalali must not be after to_jalali"
        )

    if start is not None:
        query = query.filter(models.Transaction.date >= start)
    if end is not None:
        query = query.filter(models.Transaction.date <= end)
    return query.all()


@router.get("/summary", response_model=schemas.Summary)
def get_summary(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return build_summary(db, current_user.id)


@router.get("/summary/monthly", response_model=schemas.Summary)
def get_monthly_summary(
    year: int,
    month: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    try:
        start, end = month_range(year, month)
    except ValueError as exc:
        raise HTTPException(
            status_code=422, detail="invalid year or month"
        ) from exc
    return build_summary(db, current_user.id, start, end)


@router.get("/summary/by-category", response_model=list[schemas.CategoryTotal])
def get_expense_by_category(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
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
        .filter(models.Transaction.user_id == current_user.id)
        .group_by(models.Category.id, models.Category.name)
        .all()
    )
    return [
        schemas.CategoryTotal(category_id=cid, category_name=name, total=total)
        for cid, name, total in rows
    ]


@router.get("/{transaction_id}", response_model=schemas.TransactionRead)
def get_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return get_transaction_or_404(db, transaction_id, current_user.id)


@router.delete("/{transaction_id}", status_code=204)
def delete_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    transaction = get_transaction_or_404(db, transaction_id, current_user.id)
    db.delete(transaction)
    db.commit()


@router.patch("/{transaction_id}", response_model=schemas.TransactionRead)
def update_transaction(
    transaction_id: int,
    data: schemas.TransactionUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    transaction = get_transaction_or_404(db, transaction_id, current_user.id)
    changes = data.model_dump(exclude_unset=True)

    if "jalali_date" in changes:
        jalali = changes.pop("jalali_date")
        changes["date"] = parse_jalali(jalali) if jalali is not None else None

    if changes.get("category_id") is not None:
        get_category_or_404(db, changes["category_id"], current_user.id)

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
