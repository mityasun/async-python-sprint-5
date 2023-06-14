from io import BytesIO

import pytest
from fastapi import status
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_api(
        create_user: AsyncClient,
        client: AsyncClient,
        client_auth: AsyncClient
):

    async def test_access_time():
        """Test get services access time."""

        response = await client.get('/ping')
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert isinstance(response_data['database'], float)

    async def test_get_user_token():
        """Test get user token."""

        payload = b'password=string&username=test%40example.com'
        response = await client.post(
            '/auth/jwt/login',
            content=payload,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        assert response.status_code == status.HTTP_200_OK
        assert 'access_token' in response.json()
        token = response.json().get('access_token')
        assert response.json() == {
            "access_token": f"{token}",
            "token_type": "bearer"
        }

    async def test_send_update_file_to_server():
        """Test send and update file on server."""

        file = {
            "file": ('test.txt', BytesIO(b'Hello world!'), "text/plain")
        }
        response = await client_auth.post(
            '/files/upload', files=file, data={'path': 'new'}
        )
        assert response.status_code == status.HTTP_201_CREATED
        file_id = response.json().get('id')
        name = response.json().get('name')
        created_at = response.json().get('created_at')
        path = response.json().get('path')
        size = response.json().get('size')
        assert response.json() == {
            "id": f"{file_id}",
            "name": f"{name}",
            "created_at": f"{created_at}",
            "path": f"{path}",
            "size": size,
            "is_downloadable": True
        }
        file = {
            "file": (
                'test.txt', BytesIO(b'Hello world!' * 10), "text/plain"
            )
        }
        update_response = await client_auth.post(
            '/files/upload', files=file, data={'path': 'new'}
        )
        assert update_response.status_code == status.HTTP_201_CREATED
        updated_file_id = update_response.json().get('id')
        updated_name = update_response.json().get('name')
        updated_created_at = update_response.json().get('created_at')
        updated_path = update_response.json().get('path')
        updated_size = update_response.json().get('size')
        assert update_response.json() == {
            "id": f"{updated_file_id}",
            "name": f"{updated_name}",
            "created_at": f"{updated_created_at}",
            "path": f"{updated_path}",
            "size": updated_size,
            "is_downloadable": True
        }
        assert file_id == updated_file_id
        assert name == updated_name
        assert path == updated_path
        assert size < updated_size

    async def test_send_big_file_to_server():
        """Test try to send big file to server."""

        file = {
            "file": (
                'big_file.txt', BytesIO(b'Hello world!' * 100000),
                "text/plain"
            )
        }
        response = await client_auth.post(
            '/files/upload', files=file, data={'path': 'new'}
        )
        assert response.status_code == status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
        assert response.json() == {
            "detail": "File size cannot exceed 1048576 byte"
        }

    async def test_get_user_files_list():
        """Test get user files list."""

        response = await client_auth.get(
            '/files'
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            "user_id": f"{response.json().get('user_id')}",
            "files": [
                {
                    "id": response.json()['files'][0]['id'],
                    "name": response.json()['files'][0]['name'],
                    "created_at": response.json()['files'][0]['created_at'],
                    "path": response.json()['files'][0]['path'],
                    "size": response.json()['files'][0]['size'],
                    "is_downloadable": True
                }
            ]
        }

    async def test_download_file():
        """Test download file directly and in archive"""

        file = {
            "file": ('test.txt', BytesIO(b'Hello world!'), "text/plain")
        }
        response = await client_auth.post(
            '/files/upload', files=file, data={'path': 'new'}
        )
        assert response.status_code == status.HTTP_201_CREATED
        file_id = response.json().get('id')

        response = await client_auth.get(
            '/files/download', params={'file_id': file_id}
        )
        assert response.status_code == status.HTTP_200_OK

        response = await client_auth.get(
            '/files/download', params={'file_id': file_id, 'compression': True}
        )
        assert response.status_code == status.HTTP_200_OK

    async def test_download_dir():
        """Test download dir directly and in archive"""

        response = await client_auth.get(
            '/files/download', params={'path': 'new'}
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

        response = await client_auth.get(
            '/files/download', params={'path': 'new', 'compression': True}
        )
        assert response.status_code == status.HTTP_200_OK

    await test_access_time()
    await test_get_user_token()
    await test_send_update_file_to_server()
    await test_send_big_file_to_server()
    await test_get_user_files_list()
    await test_download_file()
    await test_download_dir()
