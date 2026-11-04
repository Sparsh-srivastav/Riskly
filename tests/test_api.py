import os
import sys
import uuid
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from app.main import app
from app.core.database import Base, get_db
from app.models.contact_identity import ContactIdentity
from app.models.report import Report

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
Base.metadata.create_all(bind=engine)

client = TestClient(app)


@pytest.fixture(autouse=True)
def clean_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


def test_health_or_root():
    response = client.get("/")
    assert response.status_code in [200, 404]


def test_reputation_lookup_empty():
    response = client.get(
        "/reports/reputation",
        params={"contact_type": "phone", "contact_value": "+918888888888"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "score" in data
    assert "risk_level" in data
    assert "report_count" in data
    assert data["report_count"] == 0


def test_reputation_lookup_with_data():
    db = TestingSessionLocal()

    identity = ContactIdentity(
        id=uuid.uuid4(),
        contact_type="phone",
        normalized_value="+918800112233",
    )
    db.add(identity)
    db.flush()

    report = Report(
        id=uuid.uuid4(),
        reporter_id=uuid.uuid4(),
        identity_id=identity.id,
        report_type="fraud",
        description="Bank KYC SMS scam",
    )
    db.add(report)
    db.commit()
    db.close()

    response = client.get(
        "/reports/reputation",
        params={"contact_type": "phone", "contact_value": "+918800112233"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["report_count"] == 1
    assert data["score"] > 0


def test_unauthenticated_report_submission():
    payload = {
        "contact_type": "phone",
        "contact_value": "+919999999999",
        "report_type": "spam",
        "description": "Spam telemarketing call",
    }
    response = client.post("/reports", json=payload)
    assert response.status_code in [401, 403]


def test_websocket_feed_connection():
    with client.websocket_connect("/ws/feed") as websocket:
        assert websocket is not None

def test_auth_registration_and_login_dual_tokens():
    reg_resp = client.post(
        "/auth/register",
        json={"email": "officer@riskly.dev", "password": "securepassword123", "role": "admin"}
    )
    assert reg_resp.status_code == 201
    assert reg_resp.json()["role"] == "admin"

    login_resp = client.post(
        "/auth/login",
        json={"email": "officer@riskly.dev", "password": "securepassword123"}
    )
    assert login_resp.status_code == 200
    data = login_resp.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["role"] == "admin"


def test_auth_refresh_rotation():
    client.post(
        "/auth/register",
        json={"email": "analyst2@riskly.dev", "password": "password123", "role": "analyst"}
    )
    login_resp = client.post(
        "/auth/login",
        json={"email": "analyst2@riskly.dev", "password": "password123"}
    )
    refresh_token = login_resp.json()["refresh_token"]

    refresh_resp = client.post(
        "/auth/refresh",
        json={"refresh_token": refresh_token}
    )
    assert refresh_resp.status_code == 200
    new_data = refresh_resp.json()
    assert "access_token" in new_data
    assert "refresh_token" in new_data
    assert new_data["role"] == "analyst"


def test_auth_reject_invalid_refresh_token():
    resp = client.post(
        "/auth/refresh",
        json={"refresh_token": "malformed.invalid.token"}
    )
    assert resp.status_code == 401
