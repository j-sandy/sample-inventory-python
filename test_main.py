from fastapi.testclient import TestClient
from main import app, items_db, sessions_db, VALID_USERNAME, VALID_PASSWORD
from datetime import date
import pytest

client = TestClient(app)

@pytest.fixture(autouse=True)
def clear_dbs():
    """Fixture to clear in-memory databases before each test."""
    items_db.clear()
    sessions_db.clear()

def test_login_success():
    response = client.post("/login", json={"username": VALID_USERNAME, "password": VALID_PASSWORD})
    assert response.status_code == 200
    assert "session_token" in response.json()

def test_login_failure_invalid_credentials():
    response = client.post("/login", json={"username": "wronguser", "password": "wrongpassword"})
    assert response.status_code == 401
    assert response.json() == {"detail": "Incorrect username or password"}

def test_logout_success():
    # First, log in to get a session token
    login_response = client.post("/login", json={"username": VALID_USERNAME, "password": VALID_PASSWORD})
    session_token = login_response.json()["session_token"]

    # Then, logout
    response = client.post("/logout", headers={"session_token": session_token})
    assert response.status_code == 200
    assert response.json() == {"message": "Logged out successfully"}
    assert session_token not in sessions_db

def test_logout_failure_invalid_token():
    response = client.post("/logout", headers={"session_token": "invalid-token"})
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid authentication credentials"}

def test_add_item_success():
    login_response = client.post("/login", json={"username": VALID_USERNAME, "password": VALID_PASSWORD})
    session_token = login_response.json()["session_token"]

    item_data = {
        "name": "Laptop",
        "item_code": "LAP001",
        "quantity": 10,
        "procurement_date": "2023-01-15"
    }
    response = client.post("/items", json=item_data, headers={"session_token": session_token})
    assert response.status_code == 201
    assert response.json()["item_code"] == "LAP001"
    assert items_db["LAP001"].name == "Laptop"

def test_add_item_failure_duplicate_code():
    login_response = client.post("/login", json={"username": VALID_USERNAME, "password": VALID_PASSWORD})
    session_token = login_response.json()["session_token"]

    item_data = {
        "name": "Laptop",
        "item_code": "LAP001",
        "quantity": 10,
        "procurement_date": "2023-01-15"
    }
    client.post("/items", json=item_data, headers={"session_token": session_token}) # Add first item

    response = client.post("/items", json=item_data, headers={"session_token": session_token}) # Add duplicate
    assert response.status_code == 400
    assert response.json() == {"detail": "Item with this item_code already exists"}

def test_add_item_unauthorized():
    item_data = {
        "name": "Laptop",
        "item_code": "LAP001",
        "quantity": 10,
        "procurement_date": "2023-01-15"
    }
    response = client.post("/items", json=item_data, headers={"session_token": "invalid-token"})
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid authentication credentials"}

def test_get_item_by_code_success():
    login_response = client.post("/login", json={"username": VALID_USERNAME, "password": VALID_PASSWORD})
    session_token = login_response.json()["session_token"]

    item_data = {
        "name": "Laptop",
        "item_code": "LAP001",
        "quantity": 10,
        "procurement_date": "2023-01-15"
    }
    client.post("/items", json=item_data, headers={"session_token": session_token})

    response = client.get("/items/LAP001", headers={"session_token": session_token})
    assert response.status_code == 200
    assert response.json()["item_code"] == "LAP001"
    assert response.json()["name"] == "Laptop"

def test_get_item_by_code_not_found():
    login_response = client.post("/login", json={"username": VALID_USERNAME, "password": VALID_PASSWORD})
    session_token = login_response.json()["session_token"]

    response = client.get("/items/NONEXISTENT", headers={"session_token": session_token})
    assert response.status_code == 404
    assert response.json() == {"detail": "Item not found"}

def test_update_item_success():
    login_response = client.post("/login", json={"username": VALID_USERNAME, "password": VALID_PASSWORD})
    session_token = login_response.json()["session_token"]

    item_data = {
        "name": "Laptop",
        "item_code": "LAP001",
        "quantity": 10,
        "procurement_date": "2023-01-15"
    }
    client.post("/items", json=item_data, headers={"session_token": session_token})

    updated_data = {
        "name": "Gaming Laptop",
        "item_code": "LAP001",
        "quantity": 8,
        "procurement_date": "2023-01-15",
        "description": "High-end gaming laptop"
    }
    response = client.put("/items/LAP001", json=updated_data, headers={"session_token": session_token})
    assert response.status_code == 200
    assert response.json()["name"] == "Gaming Laptop"
    assert items_db["LAP001"].name == "Gaming Laptop"

def test_update_item_not_found():
    login_response = client.post("/login", json={"username": VALID_USERNAME, "password": VALID_PASSWORD})
    session_token = login_response.json()["session_token"]

    updated_data = {
        "name": "Gaming Laptop",
        "item_code": "NONEXISTENT",
        "quantity": 8,
        "procurement_date": "2023-01-15"
    }
    response = client.put("/items/NONEXISTENT", json=updated_data, headers={"session_token": session_token})
    assert response.status_code == 404
    assert response.json() == {"detail": "Item not found"}

def test_update_item_code_mismatch():
    login_response = client.post("/login", json={"username": VALID_USERNAME, "password": VALID_PASSWORD})
    session_token = login_response.json()["session_token"]

    item_data = {
        "name": "Laptop",
        "item_code": "LAP001",
        "quantity": 10,
        "procurement_date": "2023-01-15"
    }
    client.post("/items", json=item_data, headers={"session_token": session_token})

    updated_data = {
        "name": "Gaming Laptop",
        "item_code": "LAP002", # Mismatch
        "quantity": 8,
        "procurement_date": "2023-01-15"
    }
    response = client.put("/items/LAP001", json=updated_data, headers={"session_token": session_token})
    assert response.status_code == 400
    assert response.json() == {"detail": "Item code in path and body must match"}

def test_delete_item_success():
    login_response = client.post("/login", json={"username": VALID_USERNAME, "password": VALID_PASSWORD})
    session_token = login_response.json()["session_token"]

    item_data = {
        "name": "Laptop",
        "item_code": "LAP001",
        "quantity": 10,
        "procurement_date": "2023-01-15"
    }
    client.post("/items", json=item_data, headers={"session_token": session_token})

    response = client.delete("/items/LAP001", headers={"session_token": session_token})
    assert response.status_code == 204
    assert "LAP001" not in items_db

def test_delete_item_not_found():
    login_response = client.post("/login", json={"username": VALID_USERNAME, "password": VALID_PASSWORD})
    session_token = login_response.json()["session_token"]

    response = client.delete("/items/NONEXISTENT", headers={"session_token": session_token})
    assert response.status_code == 404
    assert response.json() == {"detail": "Item not found"}

def test_search_items_by_name():
    login_response = client.post("/login", json={"username": VALID_USERNAME, "password": VALID_PASSWORD})
    session_token = login_response.json()["session_token"]

    item1_data = {"name": "Laptop Pro", "item_code": "LP001", "quantity": 5, "procurement_date": "2023-01-01"}
    item2_data = {"name": "Desktop PC", "item_code": "DP001", "quantity": 3, "procurement_date": "2023-01-05"}
    item3_data = {"name": "Laptop Air", "item_code": "LA001", "quantity": 7, "procurement_date": "2023-01-10"}

    client.post("/items", json=item1_data, headers={"session_token": session_token})
    client.post("/items", json=item2_data, headers={"session_token": session_token})
    client.post("/items", json=item3_data, headers={"session_token": session_token})

    response = client.get("/items/search/?name=Laptop", headers={"session_token": session_token})
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]["name"] == "Laptop Pro"
    assert response.json()[1]["name"] == "Laptop Air"

def test_search_items_by_procurement_date():
    login_response = client.post("/login", json={"username": VALID_USERNAME, "password": VALID_PASSWORD})
    session_token = login_response.json()["session_token"]

    item1_data = {"name": "Laptop Pro", "item_code": "LP001", "quantity": 5, "procurement_date": "2023-01-01"}
    item2_data = {"name": "Desktop PC", "item_code": "DP001", "quantity": 3, "procurement_date": "2023-01-05"}
    item3_data = {"name": "Laptop Air", "item_code": "LA001", "quantity": 7, "procurement_date": "2023-01-01"}

    client.post("/items", json=item1_data, headers={"session_token": session_token})
    client.post("/items", json=item2_data, headers={"session_token": session_token})
    client.post("/items", json=item3_data, headers={"session_token": session_token})

    response = client.get("/items/search/?procurement_date=2023-01-01", headers={"session_token": session_token})
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]["name"] == "Laptop Pro"
    assert response.json()[1]["name"] == "Laptop Air"

def test_search_items_by_expiry_date():
    login_response = client.post("/login", json={"username": VALID_USERNAME, "password": VALID_PASSWORD})
    session_token = login_response.json()["session_token"]

    item1_data = {"name": "Item A", "item_code": "A001", "quantity": 1, "procurement_date": "2023-01-01", "expiry_date": "2024-12-31"}
    item2_data = {"name": "Item B", "item_code": "B001", "quantity": 1, "procurement_date": "2023-01-01", "expiry_date": "2025-12-31"}
    item3_data = {"name": "Item C", "item_code": "C001", "quantity": 1, "procurement_date": "2023-01-01", "expiry_date": "2024-12-31"}

    client.post("/items", json=item1_data, headers={"session_token": session_token})
    client.post("/items", json=item2_data, headers={"session_token": session_token})
    client.post("/items", json=item3_data, headers={"session_token": session_token})

    response = client.get("/items/search/?expiry_date=2024-12-31", headers={"session_token": session_token})
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]["name"] == "Item A"
    assert response.json()[1]["name"] == "Item C"

def test_search_items_combined_filters():
    login_response = client.post("/login", json={"username": VALID_USERNAME, "password": VALID_PASSWORD})
    session_token = login_response.json()["session_token"]

    item1_data = {"name": "Laptop Pro", "item_code": "LP001", "quantity": 5, "procurement_date": "2023-01-01", "expiry_date": "2024-12-31"}
    item2_data = {"name": "Desktop PC", "item_code": "DP001", "quantity": 3, "procurement_date": "2023-01-05", "expiry_date": "2025-12-31"}
    item3_data = {"name": "Laptop Air", "item_code": "LA001", "quantity": 7, "procurement_date": "2023-01-01", "expiry_date": "2024-12-31"}

    client.post("/items", json=item1_data, headers={"session_token": session_token})
    client.post("/items", json=item2_data, headers={"session_token": session_token})
    client.post("/items", json=item3_data, headers={"session_token": session_token})

    response = client.get("/items/search/?name=Laptop&procurement_date=2023-01-01&expiry_date=2024-12-31", headers={"session_token": session_token})
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]["name"] == "Laptop Pro"
    assert response.json()[1]["name"] == "Laptop Air"

def test_search_items_no_match():
    login_response = client.post("/login", json={"username": VALID_USERNAME, "password": VALID_PASSWORD})
    session_token = login_response.json()["session_token"]

    item1_data = {"name": "Laptop Pro", "item_code": "LP001", "quantity": 5, "procurement_date": "2023-01-01"}
    client.post("/items", json=item1_data, headers={"session_token": session_token})

    response = client.get("/items/search/?name=NonExistent", headers={"session_token": session_token})
    assert response.status_code == 200
    assert len(response.json()) == 0
