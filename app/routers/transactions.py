from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas
from app.database import get_db
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

    transaction = models.Transaction(**data.model_dump(exclude_none=True))
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