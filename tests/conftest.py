import os

# Must be set before the app is imported so the app's own engine never touches dpp.db.
os.environ["DATABASE_URL"] = "sqlite://"

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app import models  # noqa: F401  (registers tables on Base.metadata)
from app.database import Base, get_db
from app.main import app


@pytest.fixture
def db_session() -> Iterator[Session]:
    """A fresh in-memory database per test. StaticPool keeps one shared connection,
    otherwise every new connection would see an empty in-memory database."""
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    TestingSession = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    with TestingSession() as session:
        yield session
    engine.dispose()


@pytest.fixture
def client(db_session: Session) -> Iterator[TestClient]:
    app.dependency_overrides[get_db] = lambda: db_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def battery_payload() -> dict:
    return {
        "product_id": "TEST-LFP-0001",
        "manufacturer": "Demo Battery Works GmbH",
        "model": "Test Pack 10",
        "serial_number": "TP10-0001",
        "chemistry": "LFP",
        "capacity_kwh": 10.0,
        "manufacturing_date": "2024-05-01",
        "lifecycle_status": "manufactured",
        "nominal_voltage_v": 51.2,
        "weight_kg": 95.0,
        "expected_cycle_life": 6000,
        "carbon_footprint_kg_co2e_per_kwh": 60.0,
        "recycled_lithium_pct": 5.0,
        "end_of_life_info": "Return to manufacturer.",
    }


@pytest.fixture
def created_battery(client: TestClient, battery_payload: dict) -> dict:
    response = client.post("/api/batteries", json=battery_payload)
    assert response.status_code == 201
    return response.json()
