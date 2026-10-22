from fastapi import FastAPI

from app import models
from app.database import engine
from app.routers import auth, categories, transactions

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="kharjyar")
app.include_router(categories.router)
app.include_router(transactions.router)
app.include_router(auth.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
