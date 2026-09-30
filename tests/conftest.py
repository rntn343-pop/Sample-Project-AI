import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import os
from pathlib import Path

os.environ.setdefault("SECRET_KEY", "test-secret-key-for-pocketsmart-123456")
os.environ.setdefault("GEMINI_API_KEY", "")
os.environ.setdefault("DATABASE_URL", "sqlite:///./data/test_pocketsmart.db")

import pytest
from fastapi.testclient import TestClient

from app.db import Base, engine
from app.main import app


@pytest.fixture(autouse=True)
def reset_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client
