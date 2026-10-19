def test_list_categories_empty(client):
    response = client.get("/categories/")
    assert response.status_code == 200
    assert response.json() == []


def test_create_category(client):
    response = client.post("/categories/", json={"name": "food"})
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "food"
    assert "id" in data


def test_create_duplicate_category_returns_409(client):
    client.post("/categories/", json={"name": "food"})
    response = client.post("categories/", json={"name": "food"})
    assert response.status_code == 409


def test_create_category_with_empty_name_returns_422(client):
    response = client.post("/categories/", json={"name": ""})
    assert response.status_code == 422


def test_delete_category_with_transactions_returns_409(client, category):
    created = client.post(
        "/transactions/",
        json={
            "amount": 5000,
            "type": "expense",
            "jalali_date": "1405/07/21",
            "category_id": category["id"],
        },
    )
    assert created.status_code == 201
    response = client.delete(f"/categories/{category['id']}")
    assert response.status_code == 409
