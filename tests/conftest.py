from typing import AsyncGenerator

import pytest_asyncio
from fastapi import status
from httpx import AsyncClient

from src.core.config import app_settings
from src.main import app

app_url = (f'http://{app_settings.project_host}:'
           f'{app_settings.project_port}/api/v1/')


@pytest_asyncio.fixture()
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Anonymous client"""

    async with AsyncClient(app=app, base_url=app_url) as client:
        yield client


@pytest_asyncio.fixture()
async def create_user() -> AsyncGenerator[AsyncClient, None]:
    """Create user and test."""

    async with AsyncClient(app=app, base_url=app_url) as client:
        response = await client.post(
            '/auth/register',
            json={"email": "test@example.com", "password": "string"}
        )
        if response.status_code == status.HTTP_400_BAD_REQUEST:
            yield client
        else:
            assert response.status_code == status.HTTP_201_CREATED
            assert response.json() == {
                "id": f"{response.json().get('id')}",
                "email": "test@example.com",
                "is_active": True,
                "is_superuser": False,
                "is_verified": False
            }
            yield client


@pytest_asyncio.fixture()
async def client_auth() -> AsyncGenerator[AsyncClient, None]:
    """Create token and put to client header"""

    async with AsyncClient(app=app, base_url=app_url) as client:
        payload = b'password=string&username=test%40example.com'
        response = await client.post(
            '/auth/jwt/login', content=payload,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        assert response.status_code == status.HTTP_200_OK
        assert 'access_token' in response.json()
        token = response.json().get('access_token')
        client.headers.update({'Authorization': f'Bearer {token}'})
        yield client
