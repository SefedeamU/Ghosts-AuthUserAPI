import pytest

@pytest.fixture
def address_data():
    return {
        "user_id": 1,
        "street": "Main St",
        "city": "City",
        "state": "ST",
        "zip_code": "12345",
        "country": "USA"
    }

def test_create_address(client, address_data, test_user):
    response = client.post("/addresses/", json=address_data)
    assert response.status_code == 201 or response.status_code == 200
    data = response.json()
    assert data["street"] == address_data["street"]
    assert "id" in data
    address_data["id"] = data["id"]

def test_get_address(client, address_data, test_user):
    create_resp = client.post("/addresses/", json=address_data)
    address_id = create_resp.json()["id"]
    response = client.get(f"/addresses/{address_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == address_id

def test_list_addresses_by_user(client, address_data, test_user):
    client.post("/addresses/", json=address_data)
    address_data2 = address_data.copy()
    address_data2["street"] = "Second St"
    client.post("/addresses/", json=address_data2)
    response = client.get(f"/addresses/user/{address_data['user_id']}")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2

def test_replace_address(client, address_data, test_user):
    create_resp = client.post("/addresses/", json=address_data)
    address_id = create_resp.json()["id"]

    replace_data = {
        "user_id": test_user.id,
        "street": "Replaced St",
        "city": "New City",
        "state": "NC",
        "zip_code": "54321",
        "country": "USA"
    }
    response = client.put(f"/addresses/{address_id}", json=replace_data)
    assert response.status_code == 200
    data = response.json()
    assert data["street"] == "Replaced St"
    assert data["city"] == "New City"
    assert data["zip_code"] == "54321"

def test_partial_update_address(client, address_data, test_user):
    create_resp = client.post("/addresses/", json=address_data)
    address_id = create_resp.json()["id"]

    patch_data = {
        "street": "Patched St"
    }
    response = client.patch(f"/addresses/{address_id}", json=patch_data)
    assert response.status_code == 200
    data = response.json()
    assert data["street"] == "Patched St"
    assert data["city"] == address_data["city"]

def test_delete_address(client, address_data, test_user):
    create_resp = client.post("/addresses/", json=address_data)
    address_id = create_resp.json()["id"]
    response = client.delete(f"/addresses/{address_id}")
    assert response.status_code == 200
    get_resp = client.get(f"/addresses/{address_id}")
    assert get_resp.status_code == 404

def test_get_nonexistent_address(client, test_user):
    response = client.get("/addresses/99999")
    assert response.status_code == 404

def test_update_nonexistent_address(client, test_user):
    update_data = {
        "street": "No existe",
        "city": "City",
        "state": "ST",
        "zip_code": "12345",
        "country": "USA",
        "user_id": test_user.id
    }
    response = client.put("/addresses/99999", json=update_data)
    assert response.status_code == 404

def test_delete_nonexistent_address(client, test_user):
    response = client.delete("/addresses/99999")
    assert response.status_code == 404