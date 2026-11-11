import pytest

pytestmark = pytest.mark.anyio

USER_PAYLOAD = {
    "username": "testuser",
    "email": "test@test.com",
    "password": "@12345678",
}


# Registro válido
async def test_register_valid_user(client):
    response = await client.post("/auth/register", json=USER_PAYLOAD)
    body = response.json()
    assert body["email"] == USER_PAYLOAD["email"]
    assert "password" not in body
    assert "hashed_password" not in body
    assert response.status_code == 201


# Registro con un email repetido
async def test_register_user_email_repeated(client):
    await client.post("/auth/register", json=USER_PAYLOAD)
    response = await client.post(
        "/auth/register", json={**USER_PAYLOAD, "username": "otheruser"}
    )

    assert response.status_code == 409


# Login con la contraseña incorrecta
async def test_login_with_wrong_password(client):
    await client.post("/auth/register", json=USER_PAYLOAD)
    response = await client.post(
        "/auth/token",
        data={"username": USER_PAYLOAD["email"], "password": "wrong-password"},
    )

    assert response.status_code == 401


# GET /auth/me
async def test_auth_with_token(client, auth_headers):
    response = await client.get("/auth/me", headers=auth_headers)
    assert response.json()["email"] == "alice@test.com"
    assert response.status_code == 200
