def create_transaction(client, amount, type, jalali_date):
    response = client.post(
        "/transactions/",
        json={
            "amount": amount,
            "type": type,
            "jalali_date": jalali_date,
        },
    )
    assert response.status_code == 201
    return response.json()


def test_create_transaction_with_jalali_date(client, category):
    response = client.post(
        "/transactions/",
        json={
            "amount": 5000,
            "type": "expense",
            "jalali_date": "1405/07/21",
            "category_id": category["id"],
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["amount"] == 5000
    assert data["type"] == "expense"
    assert data["jalali_date"] == "1405/07/21"
    assert data["category_id"] == category["id"]
    assert "date" not in data


def test_create_transaction_with_unknown_category_returns_404(client):
    response = client.post(
        "/transactions/",
        json={
            "amount": 5000,
            "type": "expense",
            "jalali_date": "1405/07/21",
            "category_id": 999,
        },
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Category not found"


def test_create_transaction_with_invalid_jalali_date_returns_422(client):
    response = client.post(
        "/transactions/",
        json={
            "amount": 5000,
            "type": "expense",
            "jalali_date": "1405/13/21",
        },
    )
    assert response.status_code == 422


def test_monthly_summary_counts_only_given_month(client):
    create_transaction(client, 1000, "income", "1405/07/01")
    create_transaction(client, 300, "expense", "1405/07/30")
    create_transaction(client, 999, "expense", "1405/08/01")

    response = client.get(
        "/transactions/summary/monthly",
        params={"year": 1405, "month": 7},
    )

    assert response.status_code == 200
    assert response.json() == {
        "total_income": 1000,
        "total_expense": 300,
        "balance": 700,
    }


def test_monthly_summary_empty_month_returns_zeros(client):
    response = client.get(
        "/transactions/summary/monthly",
        params={"year": 1405, "month": 7},
    )
    assert response.status_code == 200
    assert response.json() == {
        "total_income": 0,
        "total_expense": 0,
        "balance": 0,
    }


def test_monthly_summary_includes_last_day_of_leap_year(client):
    create_transaction(client, 1000, "income", "1403/12/30")
    create_transaction(client, 500, "income", "1404/01/01")

    response = client.get(
        "/transactions/summary/monthly",
        params={"year": 1403, "month": 12},
    )

    assert response.status_code == 200
    assert response.json() == {
        "total_income": 1000,
        "total_expense": 0,
        "balance": 1000,
    }


def test_cannot_create_transaction_with_other_users_category(client, other_client):
    created = other_client.post("/categories/", json={"name": "food"})
    other_category_id = created.json()["id"]

    response = client.post(
        "/transactions/",
        json={
            "amount": 5000,
            "type": "expense",
            "category_id": other_category_id,
        },
    )

    assert response.status_code == 404


def test_get_other_users_transaction_returns_404(client, other_client, category):
    created = client.post(
        "/transactions/",
        json={
            "amount": 100000,
            "type": "expense",
            "category_id": category["id"],
            "jalali_date": "1404/08/01",
        },
    )
    assert created.status_code == 201
    transaction_id = created.json()["id"]

    response = other_client.get(f"/transactions/{transaction_id}")
    assert response.status_code == 404


def test_list_transactions_only_returns_own(client, other_client):
    mine = client.post(
        "/transactions/",
        json={
            "amount": 100000,
            "type": "income",
            "jalali_date": "1405/08/01",
        }
    )
    assert mine.status_code == 201

    theirs = other_client.post(
        "/transactions/",
        json={
            "amount": 5000,
            "type": "expense",
            "jalali_date": "1405/08/26",
        }
    )
    assert theirs.status_code == 201

    response = client.get("/transactions/")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["id"] == mine.json()["id"]


def test_update_other_users_transaction_returns_404(client, other_client):
    created = client.post(
        "/transactions/",
        json={
            "amount": 10000,
            "type": "income",
            "jalali_date": "1405/08/01",
        }
    )
    assert created.status_code == 201
    transaction_id = created.json()["id"]

    response = other_client.patch(
        f"/transactions/{transaction_id}",
        json={
            "amount": 20000,
            "type": "expense",
            "jalali_date": "1405/09/09",
        }
    )
    assert response.status_code == 404
    response = client.get(f"/transactions/{transaction_id}")
    assert response.status_code == 200
    assert response.json()["amount"] == 10000
