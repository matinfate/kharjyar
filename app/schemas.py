import datetime

from pydantic import BaseModel, ConfigDict, Field, computed_field, field_validator

from app.jalali import parse_jalali, to_jalali_str
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
    jalali_date: str | None = None
    category_id: int | None = None

    @field_validator("jalali_date")
    @classmethod
    def check_jalali_date(cls, value):
        if value is not None:
            parse_jalali(value)
        return value


class TransactionRead(BaseModel):
    id: int
    amount: int
    type: TransactionType
    description: str | None
    date: datetime.date = Field(exclude=True)
    category_id: int | None
    model_config = ConfigDict(from_attributes=True)

    @computed_field
    @property
    def jalali_date(self) -> str:
        return to_jalali_str(self.date)


class TransactionUpdate(BaseModel):
    amount: int | None = Field(default=None, gt=0)
    type: TransactionType | None = None
    description: str | None = None
    jalali_date: str | None = None
    category_id: int | None = None

    @field_validator("jalali_date")
    @classmethod
    def check_jalali_date(cls, value):
        if value is not None:
            parse_jalali(value)
        return value


class Summary(BaseModel):
    total_income: int
    total_expense: int
    balance: int


class CategoryTotal(BaseModel):
    category_id: int | None
    category_name: str | None
    total: int
