from fastapi import FastAPI
from app import models
from app.database import engine
from app.routers import categories, transactions

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="kharjyar")
app.include_router(categories.router)
app.include_router(transactions.router)

@app.get("/health")
def health_check():
    return {"status": "ok"}