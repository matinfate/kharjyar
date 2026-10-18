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
