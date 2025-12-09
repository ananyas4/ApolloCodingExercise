"""Test suite for Vehicle API endpoints."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_vehicles.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function")
def client():
    """Create test client with fresh database for each test."""
    Base.metadata.create_all(bind=engine)
    yield TestClient(app)
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def sample_vehicle():
    """Sample vehicle data for testing."""
    return {
        "vin": "1HGBH41JXMN109186",
        "manufacturer_name": "Honda",
        "description": "A reliable sedan",
        "horse_power": 180,
        "model_name": "Accord",
        "model_year": 2020,
        "purchase_price": 25000.00,
        "fuel_type": "Gasoline",
    }


def test_create_vehicle(client, sample_vehicle):
    """Test creating a vehicle."""
    response = client.post("/vehicle", json=sample_vehicle)
    assert response.status_code == 201
    data = response.json()
    assert data["vin"] == sample_vehicle["vin"].upper()
    assert data["manufacturer_name"] == sample_vehicle["manufacturer_name"]
    assert data["horse_power"] == sample_vehicle["horse_power"]


def test_create_vehicle_vin_normalization(client, sample_vehicle):
    """Test that VIN is normalized to uppercase."""
    sample_vehicle["vin"] = "1hgbh41jxmn109186"
    response = client.post("/vehicle", json=sample_vehicle)
    assert response.status_code == 201
    data = response.json()
    assert data["vin"] == "1HGBH41JXMN109186"


def test_create_duplicate_vin(client, sample_vehicle):
    """Test that duplicate VINs are rejected."""
    client.post("/vehicle", json=sample_vehicle)
    response = client.post("/vehicle", json=sample_vehicle)
    assert response.status_code == 422
    assert "errors" in response.json()["detail"]


def test_create_vehicle_case_insensitive_vin(client, sample_vehicle):
    """Test that VIN uniqueness is case-insensitive."""
    client.post("/vehicle", json=sample_vehicle)
    sample_vehicle["vin"] = sample_vehicle["vin"].lower()
    response = client.post("/vehicle", json=sample_vehicle)
    assert response.status_code == 422


def test_get_all_vehicles(client, sample_vehicle):
    """Test getting all vehicles."""
    client.post("/vehicle", json=sample_vehicle)
    response = client.get("/vehicle")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["vin"] == sample_vehicle["vin"].upper()


def test_get_vehicle_by_vin(client, sample_vehicle):
    """Test getting a vehicle by VIN."""
    client.post("/vehicle", json=sample_vehicle)
    response = client.get(f"/vehicle/{sample_vehicle['vin']}")
    assert response.status_code == 200
    data = response.json()
    assert data["vin"] == sample_vehicle["vin"].upper()


def test_get_vehicle_by_vin_case_insensitive(client, sample_vehicle):
    """Test getting a vehicle by VIN is case-insensitive."""
    client.post("/vehicle", json=sample_vehicle)
    response = client.get(f"/vehicle/{sample_vehicle['vin'].lower()}")
    assert response.status_code == 200
    data = response.json()
    assert data["vin"] == sample_vehicle["vin"].upper()


def test_get_nonexistent_vehicle(client):
    """Test getting a non-existent vehicle."""
    response = client.get("/vehicle/INVALID123")
    assert response.status_code == 404


def test_update_vehicle(client, sample_vehicle):
    """Test updating a vehicle."""
    client.post("/vehicle", json=sample_vehicle)
    update_data = {"horse_power": 200, "purchase_price": 27000.00}
    response = client.put(f"/vehicle/{sample_vehicle['vin']}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["horse_power"] == 200
    assert data["purchase_price"] == 27000.00
    assert data["manufacturer_name"] == sample_vehicle["manufacturer_name"]


def test_update_nonexistent_vehicle(client):
    """Test updating a non-existent vehicle."""
    update_data = {"horse_power": 200}
    response = client.put("/vehicle/INVALID123", json=update_data)
    assert response.status_code == 404


def test_delete_vehicle(client, sample_vehicle):
    """Test deleting a vehicle."""
    client.post("/vehicle", json=sample_vehicle)
    response = client.delete(f"/vehicle/{sample_vehicle['vin']}")
    assert response.status_code == 204
    # Verify it's deleted
    get_response = client.get(f"/vehicle/{sample_vehicle['vin']}")
    assert get_response.status_code == 404


def test_delete_nonexistent_vehicle(client):
    """Test deleting a non-existent vehicle."""
    response = client.delete("/vehicle/INVALID123")
    assert response.status_code == 404


def test_malformed_json(client):
    """Test handling of malformed JSON."""
    response = client.post(
        "/vehicle", data="not json", headers={"Content-Type": "application/json"}
    )
    assert response.status_code == 400 or response.status_code == 422


def test_validation_errors_missing_fields(client):
    """Test validation errors for missing required fields."""
    incomplete_vehicle = {
        "vin": "1HGBH41JXMN109186",
        "manufacturer_name": "Honda",
        # Missing other required fields
    }
    response = client.post("/vehicle", json=incomplete_vehicle)
    assert response.status_code == 422
    assert "errors" in response.json()


def test_validation_errors_invalid_data(client):
    """Test validation errors for invalid data."""
    invalid_vehicle = {
        "vin": "1HGBH41JXMN109186",
        "manufacturer_name": "Honda",
        "description": "A reliable sedan",
        "horse_power": -10,  # Invalid: negative
        "model_name": "Accord",
        "model_year": 1800,  # Invalid: too old
        "purchase_price": -1000.00,  # Invalid: negative
        "fuel_type": "Gasoline",
    }
    response = client.post("/vehicle", json=invalid_vehicle)
    assert response.status_code == 422
    assert "errors" in response.json()


def test_empty_vin(client, sample_vehicle):
    """Test that empty VIN is rejected."""
    sample_vehicle["vin"] = ""
    response = client.post("/vehicle", json=sample_vehicle)
    assert response.status_code == 422


def test_multiple_vehicles(client, sample_vehicle):
    """Test handling multiple vehicles."""
    # Create first vehicle
    client.post("/vehicle", json=sample_vehicle)

    # Create second vehicle
    vehicle2 = sample_vehicle.copy()
    vehicle2["vin"] = "2HGBH41JXMN109187"
    vehicle2["manufacturer_name"] = "Toyota"
    client.post("/vehicle", json=vehicle2)

    # Get all vehicles
    response = client.get("/vehicle")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
