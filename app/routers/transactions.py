from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app import models, schemas
from app.database import get_db
from app.routers.categories import get_category_or_404

router = APIRouter(prefix="/transactions", tags=["transactions"])

@router.post("/", response_model=schemas.TransactionRead, status_code=201)
def create_transaction(data: schemas.TransactionCreate, db: Session = Depends(get_db)):
    if data.category_id is not None:
        get_category_or_404(db, data.category_id)

    transaction = models.Transaction(**data.model_dump(exclude_none=True))
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction