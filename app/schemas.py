import datetime

import jdatetime
from pydantic import BaseModel, ConfigDict, Field, computed_field

from app.models import TransactionType


class CategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=50)


class CategoryRead(BaseModel):
    id: int
    name: str
    model_config = ConfigDict(from_attributes=True)


class TransactionCreate(BaseModel):
    amount: int = Field(gt=0)
    type: TransactionType
    description: str | None = None
    date: datetime.date | None = None
    category_id: int | None = None


class TransactionRead(BaseModel):
    id: int
    amount: int
    type: TransactionType
    description: str | None
    date: datetime.date
    category_id: int | None
    model_config = ConfigDict(from_attributes=True)

    @computed_field
    @property
    def jalali_date(self) -> str:
        return jdatetime.date.fromgregorian(date=self.date).strftime("%Y/%m/%d")


class TransactionUpdate(BaseModel):
    amount: int | None = Field(default=None, gt=0)
    type: TransactionType | None = None
    description: str | None = None
    date: datetime.date | None = None
    category_id: int | None = None


class Summary(BaseModel):
    total_income: int
    total_expense: int
    balance: int


class CategoryTotal(BaseModel):
    category_id: int | None
    category_name: str | None
    total: int
