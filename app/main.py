from pathlib import Path

from alembic.config import Config
from fastapi import FastAPI

from alembic import command
from app.routers import auth, categories, transactions

BASE_DIR = Path(__file__).resolve().parent.parent
alembic_cfg = Config(str(BASE_DIR / "alembic.ini"))
alembic_cfg.set_main_option("script_location", str(BASE_DIR / "alembic"))
command.upgrade(alembic_cfg, "head")

app = FastAPI(title="kharjyar")
app.include_router(categories.router)
app.include_router(transactions.router)
app.include_router(auth.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
