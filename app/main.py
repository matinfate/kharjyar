from fastapi import FastAPI

from app import models
from app.database import engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="kharjyar")


@app.get("/health")
def health_check():
    return {"status": "ok"}