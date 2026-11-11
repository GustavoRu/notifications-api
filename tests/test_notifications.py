import pytest
from app.notification.service import NotificationNotFoundError

pytestmark = pytest.mark.anyio
SMS_PAYLOAD = {
    "title": "Hola",
    "content": "Tu vuelo sale 10:30",
    "channel": "sms",
    "recipient": "+5491112345678",
}


async def test_create_notification_requires_auth(client):
    response = await client.post("/notifications", json=SMS_PAYLOAD)

    assert response.status_code == 401


async def test_create_notification_sms_with_auth(client, auth_headers):
    response = await client.post(
        "/notifications", json=SMS_PAYLOAD, headers=auth_headers
    )

    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "sent"
    assert {key: body[key] for key in SMS_PAYLOAD} == SMS_PAYLOAD


# Arrange, Act, Assert
async def test_create_notification_sms_with_161_characters(client, auth_headers):
    response = await client.post(
        "/notifications",
        json={**SMS_PAYLOAD, "content": "x" * 161},
        headers=auth_headers,
    )

    assert response.status_code == 422
    assert "160" in response.json()["detail"]


async def test_create_notification_with_unknown_channel(client, auth_headers):
    response = await client.post(
        "/notifications", json={**SMS_PAYLOAD, "channel": "fax"}, headers=auth_headers
    )

    assert response.status_code == 422
    assert "fax" in response.json()["detail"]


async def test_list_returns_newest_first(client, auth_headers):
    await client.post("/notifications", json=SMS_PAYLOAD, headers=auth_headers)
    await client.post(
        "/notifications", json={**SMS_PAYLOAD, "title": "Hola2"}, headers=auth_headers
    )

    response = await client.get("/notifications", headers=auth_headers)

    assert response.status_code == 200
    assert [n["title"] for n in response.json()] == ["Hola2", "Hola"]


# auth_headers_user_two
async def test_user_cannot_see_other_users_notifications(
    client, auth_headers, auth_headers_user_two
):
    await client.post("/notifications", json=SMS_PAYLOAD, headers=auth_headers)

    response = await client.get("/notifications", headers=auth_headers_user_two)

    assert response.status_code == 200
    assert response.json() == []


async def test_delete_notification_removes_it_from_list(client, auth_headers):
    created = (
        await client.post("/notifications", json=SMS_PAYLOAD, headers=auth_headers)
    ).json()

    response = await client.delete(
        f"/notifications/{created['id']}", headers=auth_headers
    )

    assert response.status_code == 204
    remaining = (await client.get("/notifications", headers=auth_headers)).json()
    assert remaining == []


async def test_user_cannot_delete_other_users_notification(
    client, auth_headers, auth_headers_user_two
):
    created = (
        await client.post("/notifications", json=SMS_PAYLOAD, headers=auth_headers)
    ).json()

    response = await client.delete(
        f"/notifications/{created['id']}", headers=auth_headers_user_two
    )

    assert response.status_code == 404
    remaining = (await client.get("/notifications", headers=auth_headers)).json()
    assert [n["id"] for n in remaining] == [created["id"]]


async def test_user_cannot_update_other_users_notification(
    client, auth_headers, auth_headers_user_two
):
    created = (
        await client.post("/notifications", json=SMS_PAYLOAD, headers=auth_headers)
    ).json()

    response = await client.patch(
        f"/notifications/{created['id']}",
        json={"title": "hackeado"},
        headers=auth_headers_user_two,
    )

    assert response.status_code == 404
    remaining = (await client.get("/notifications", headers=auth_headers)).json()
    assert remaining[0]["title"] == "Hola"


async def test_patch_notification_only_changes_title(client, auth_headers):
    created = (
        await client.post("/notifications", json=SMS_PAYLOAD, headers=auth_headers)
    ).json()

    response = await client.patch(
        f"/notifications/{created['id']}",
        json={"title": "Holass"},
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert response.json() == {**created, "title": "Holass"}
