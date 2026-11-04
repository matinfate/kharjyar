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
    response = client.post("/categories/", json={"name": "food"})
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


def test_user_cannot_see_other_users_categories(client, other_client):
    client.post("/categories/", json={"name": "food"})

    response = other_client.get("/categories/")

    assert response.status_code == 200
    assert response.json() == []


def test_user_cannot_get_other_users_category(client, other_client):
    created = client.post("/categories/", json={"name": "food"})
    category_id = created.json()["id"]

    response = other_client.get(f"/categories/{category_id}")

    assert response.status_code == 404


def test_user_cannot_delete_other_users_category(client, other_client):
    created = client.post("/categories/", json={"name": "food"})
    category_id = created.json()["id"]

    response = other_client.delete(f"/categories/{category_id}")

    assert response.status_code == 404
    assert client.get(f"/categories/{category_id}").status_code == 200


def test_different_users_can_use_same_category_name(client, other_client):
    first = client.post("/categories/", json={"name": "food"})
    response = other_client.post("/categories/", json={"name": "food"})

    assert first.status_code == 201
    assert response.status_code == 201


def test_update_category(client, category):
    response = client.put(
        f"/categories/{category['id']}",
        json={"name": "transport"},
    )
    body = response.json()
    assert response.status_code == 200
    assert body['name'] == "transport"
    assert body['id'] == category['id']

    verify = client.get(f"/categories/{category['id']}")
    assert verify.status_code == 200
    assert verify.json()["name"] == "transport"


def test_update_category_to_duplicate_name_returns_409(client, category):
    client.post("/categories/", json={"name": "transport"})
    response = client.put(
        f"/categories/{category['id']}",
        json={"name": "transport"},
    )
    assert response.status_code == 409


def test_update_category_to_same_name_returns_200(client, category):
    response = client.put(
        f"/categories/{category['id']}",
        json={"name": "food"},
    )
    assert response.status_code == 200


def test_update_other_users_category_returns_404(client, other_client, category):
    response = other_client.put(
        f"/categories/{category['id']}",
        json={"name": "hacked"},
    )
    assert response.status_code == 404

    verify = client.get(f"/categories/{category['id']}")
    assert verify.status_code == 200
    assert verify.json()["name"] == "food"


def test_update_category_with_empty_name_returns_422(client, category):
    response = client.put(
        f"/categories/{category['id']}",
        json={"name": ""},
    )
    assert response.status_code == 422
