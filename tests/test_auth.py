def test_register_user_success(anon_client):
    response = anon_client.post(
        "/auth/register",
        json={
            "username": "newuser",
            "password": "password123"
        }
    )

    assert response.status_code == 201

    data = response.json()

    assert data["username"] == "newuser"
    assert "id" in data
    assert "hashed_password" not in data


def test_register_duplicate_username(anon_client):
    user_data = {
        "username": "duplicateuser",
        "password": "password123"
    }

    anon_client.post("/auth/register", json=user_data)

    response = anon_client.post("/auth/register", json=user_data)

    assert response.status_code == 409


def test_login_success(anon_client):
    anon_client.post(
        "/auth/register",
        json={
            "username": "loginuser",
            "password": "password123"
        }
    )

    response = anon_client.post(
        "/auth/login",
        data={
            "username": "loginuser",
            "password": "password123"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_username(anon_client):
    anon_client.post(
        "/auth/register",
        json={
            "username": "correctuser",
            "password": "password123"
        }
    )

    response = anon_client.post(
        "/auth/login",
        data={
            "username": "incorrectuser",
            "password": "password123"
        }
    )

    assert response.status_code == 401


def test_login_wrong_password(anon_client):
    anon_client.post(
        "/auth/register",
        json={
            "username": "wrongpassuser",
            "password": "password123"
        }
    )

    response = anon_client.post(
        "/auth/login",
        data={
            "username": "loginuser",
            "password": "wrongpassword"
        }
    )

    assert response.status_code == 401


def test_login_nonexistent_user(anon_client):
    response = anon_client.post(
        "/auth/login",
        data={
            "username": "unknownuser",
            "password": "wrongpassword"
        }
    )

    assert response.status_code == 401


def test_get_current_user(client):
    response = client.get("/auth/me")

    assert response.status_code == 200

    data = response.json()

    assert data["username"] == "testuser"
    assert "id" in data
    assert "hashed_password" not in data


def test_get_current_user_unauthorized(anon_client):
    response = anon_client.get("/auth/me")

    assert response.status_code == 401


def test_get_current_user_invalid_token(anon_client):
    response = anon_client.get(
        "/auth/me",
        headers={
            "Authorization": "Bearer invalid-token"
        }
    )

    assert response.status_code == 401


def test_register_username_too_short(anon_client):
    response = anon_client.post(
        "/auth/register",
        json={
            "username": "ab",
            "password": "password123"
        }
    )

    assert response.status_code == 422


def test_register_username_too_long(anon_client):
    response = anon_client.post(
        "/auth/register",
        json={
            "username": "a" * 51,
            "password": "password123"
        }
    )

    assert response.status_code == 422


def test_register_password_too_short(anon_client):
    response = anon_client.post(
        "/auth/register",
        json={
            "username": "shortpassuser",
            "password": "1234567"
        }
    )

    assert response.status_code == 422


def test_register_password_too_long(anon_client):
    response = anon_client.post(
        "/auth/register",
        json={
            "username": "longpassuser",
            "password": "a" * 129
        }
    )

    assert response.status_code == 422


def test_register_with_minimum_valid_lengths(anon_client):
    response = anon_client.post(
        "/auth/register",
        json={
            "username": "ali",
            "password": "12345678"
        }
    )

    assert response.status_code == 201
    assert response.json()["username"] == "ali"


def test_register_with_maximum_valid_lengths(anon_client):
    response = anon_client.post(
        "/auth/register",
        json={
            "username": "a" * 50,
            "password": "a" * 128
        }
    )

    assert response.status_code == 201
    assert len(response.json()["username"]) == 50


def test_register_response_fields(anon_client):
    response = anon_client.post(
        "/auth/register",
        json={
            "username": "responseuser",
            "password": "password123"
        }
    )

    assert response.status_code == 201

    data = response.json()

    assert set(data.keys()) == {"id", "username"}
