import datetime
import enum

from sqlalchemy import  Column, Integer, String, Date, Enum, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base

class TransactionType(str, enum.Enum):
    income = "income"
    expense = "expense"

class Category(Base):
    __tablename__ = "categories"

    id=Column(Integer, primary_key=True)
    name=Column(String, unique=True, nullable=False)

    transactions = relationship("Transaction", back_populates="category")

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True)
    amount = Column(Integer, nullable=False)
    type = Column(Enum(TransactionType), nullable=False)
    description = Column(String)
    date = Column(Date, default=datetime.date.today(), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"))

    category = relationship("Category", back_populates="transactions")