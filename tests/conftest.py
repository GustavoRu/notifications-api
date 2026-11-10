import os
from collections.abc import AsyncGenerator

os.environ["DATABASE_URL"] = (
    "postgresql+psycopg://notif:notif@localhost:5434/test_notifications"
)

os.environ["SECRET_KEY"] = "test-secret-key-for-tests"

import pytest
from httpx import ASGITransport, AsyncClient

