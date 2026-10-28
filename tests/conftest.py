import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app

TEST_DATABASE_URL = "sqlite://"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(bind=test_engine, autoflush=False)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def anon_client():
    Base.metadata.create_all(bind=test_engine)
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def client(anon_client):
    credentials = {"username": "testuser", "password": "testpass123"}
    anon_client.post("/auth/register", json=credentials)
    response = anon_client.post("/auth/login", data=credentials)
    token = response.json()["access_token"]
    anon_client.headers["Authorization"] = f"Bearer {token}"
    return anon_client


@pytest.fixture
def category(client):
    response = client.post("/categories/", json={"name": "food"})
    return response.json()


@pytest.fixture
def other_client(anon_client):
    credentials = {"username": "otheruser", "password": "otherpass123"}
    other = TestClient(app)
    other.post("/auth/register", json=credentials)
    response = other.post("/auth/login", data=credentials)
    token = response.json()['access_token']
    other.headers["Authorization"] = f"Bearer {token}"
    return other
