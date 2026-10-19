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
