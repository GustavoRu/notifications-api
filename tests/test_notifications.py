import pytest
from datetime import datetime
from app.notification.service import NotificationNotFoundError

pytestmark = pytest.mark.anyio
SMS_PAYLOAD = {
    "title": "Hola",
    "content": "Tu vuelo sale 10:30",
    "channel": "sms",
    "recipient": "+5491112345678",
}


async def test_create_notification_requires_auth(client):
    response = await client.post(
        "/notifications",
        json={
            "title": "Hola",
            "content": "Tu vuelo sale 10:30",
            "channel": "sms",
            "recipient": "+5491112345678",
        },
    )
    assert response.status_code == 401


async def test_create_notification_sms_with_auth(client, auth_headers):
    response = await client.post(
        "/notifications",
        json={
            "title": "Hola",
            "content": "Tu vuelo sale 10:30",
            "channel": "sms",
            "recipient": "+5491112345678",
        },
        headers=auth_headers,
    )
    body = response.json()

    assert response.status_code == 201
    assert body["channel"] == "sms"
    assert body["status"] == "sent"
    assert "id" in body


# Arrange, Act, Assert
async def test_create_notification_sms_with_161_characters(client, auth_headers):
    response = await client.post(
        "/notifications",
        json={
            "title": "Hola",
            "content": "x" * 161,
            "channel": "sms",
            "recipient": "+5491112345678",
        },
        headers=auth_headers,
    )

    assert response.status_code == 422


async def test_create_notification_sms_with_invalid_channel(client, auth_headers):
    response = await client.post(
        "/notifications",
        json={
            "title": "Hola",
            "content": "content",
            "channel": "fax",
            "recipient": "+5491112345678",
        },
        headers=auth_headers,
    )

    assert response.status_code == 422


async def test_get_two_notifications(client, auth_headers):
    await client.post(
        "/notifications",
        json={
            "title": "Hola",
            "content": "Tu vuelo sale 10:30",
            "channel": "sms",
            "recipient": "+5491112345678",
        },
        headers=auth_headers,
    )
    await client.post(
        "/notifications",
        json={
            "title": "Hola2",
            "content": "Tu vuelo sale 11:30",
            "channel": "sms",
            "recipient": "+5491112345679",
        },
        headers=auth_headers,
    )

    response = await client.get(
        "/notifications",
        headers=auth_headers,
    )

    notifications_list = response.json()

    date_one = datetime.fromisoformat(notifications_list[0]["created_at"])
    date_two = datetime.fromisoformat(notifications_list[1]["created_at"])

    assert isinstance(notifications_list, list)
    assert date_one > date_two


# auth_headers_user_two
async def test_notifications_empty_list(client, auth_headers_user_two, auth_headers):
    await client.post(
        "/notifications",
        json={
            "title": "Hola",
            "content": "Tu vuelo sale 10:30",
            "channel": "sms",
            "recipient": "+5491112345678",
        },
        headers=auth_headers,
    )

    response = await client.get(
        "/notifications",
        headers=auth_headers_user_two,
    )
    notifications_list = response.json()

    assert isinstance(notifications_list, list)
    assert len(notifications_list) == 0


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


async def test_delete_notification_with_another_user_id(
    client, auth_headers, auth_headers_user_two
):
    await client.post(
        "/notifications",
        json={
            "title": "Hola",
            "content": "Tu vuelo sale 10:30",
            "channel": "sms",
            "recipient": "+5491112345678",
        },
        headers=auth_headers,
    )
    await client.post(
        "/notifications",
        json={
            "title": "Hola2",
            "content": "Tu vuelo sale 11:30",
            "channel": "sms",
            "recipient": "+5491112345679",
        },
        headers=auth_headers_user_two,
    )

    response = await client.delete(
        "/notifications/1",
        headers=auth_headers_user_two,
    )

    assert response.status_code == 404


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
