import os
from collections.abc import AsyncGenerator

os.environ["DATABASE_URL"] = (
    "postgresql+psycopg://notif:notif@localhost:5434/test_notifications"
)

os.environ["SECRET_KEY"] = "test-secret-key-for-tests"

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app import models  # noqa: F401  (registra las tablas en Base.metadata)
from app.config import settings
from app.database import Base, get_db
from app.main import app

assert "test" in settings.database_url, (
    "Los tests borran tablas: nunca deben apuntar a la base de desarrollo"
)

test_engine = create_async_engine(settings.database_url, poolclass=NullPool)
TestSessionLocal = async_sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


async def override_get_db():
    async with TestSessionLocal() as session:
        yield session


@pytest.fixture(autouse=True)
async def reset_db(anyio_backend):
    """Antes de cada test: tablas vacías y recién creadas."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield


@pytest.fixture
async def client():
    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as c:
        yield c
    app.dependency_overrides.clear()

@pytest.fixture
async def auth_headers(client):
    await client.post(
        "/auth/register",
        json={"username": "alice", "email": "alice@test.com", "password": "secret123"},
    )
    response = await client.post(
        "/auth/token",
        data={"username": "alice@test.com", "password": "secret123"},   # data=, no json=
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
async def auth_headers_user_two(client):
    await client.post(
        "/auth/register",
        json={"username": "pablo", "email": "pablo@test.com", "password": "secret123"},
    )
    response = await client.post(
        "/auth/token",
        data={"username": "pablo@test.com", "password": "secret123"},   # data=, no json=
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}