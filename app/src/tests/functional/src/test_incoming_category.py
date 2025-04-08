from http import HTTPStatus
from uuid import uuid4

import pytest
from models.incoming_category import IncomingCategory
from tests.functional.fixtures.auth import access_token_user


class TestOutgoingCategory:
    def setup_method(self):
        self.endpoint = "/api/v1/categories/incoming/"

    @pytest.mark.asyncio
    async def test_get_all_categories(
        self, access_token_admin, client, create_incoming_categories
    ):
        response = await client.get(self.endpoint, headers=access_token_admin)
        assert response.status_code == HTTPStatus.OK
        assert len(response.json()["items"]) == 10

    @pytest.mark.asyncio
    async def test_get_category(
        self, access_token_admin, client, create_incoming_categories
    ):
        """Ищем существующую категорию"""
        category_id = str(create_incoming_categories[0].id)
        response = await client.get(
            self.endpoint + category_id, headers=access_token_admin
        )
        assert response.status_code == HTTPStatus.OK
        assert response.json()["id"] == category_id

    @pytest.mark.asyncio
    async def test_get_non_existing_category(
        self, access_token_admin, client, create_incoming_categories
    ):
        """Ищем несуществующую категорию"""
        category_id = str(uuid4())
        response = await client.get(
            self.endpoint + category_id, headers=access_token_admin
        )
        assert response.status_code == HTTPStatus.NOT_FOUND

    @pytest.mark.asyncio
    async def test_create_category(
        self, access_token_admin, client, create_incoming_categories
    ):
        """Создаем категорию"""
        category = IncomingCategory(
            name="Test",
            description="Test",
        )
        response = await client.post(
            self.endpoint,
            headers=access_token_admin,
            json={
                "name": category.name,
                "description": category.description,
            },
        )
        assert response.status_code == HTTPStatus.OK
        assert response.json()["name"] == category.name

    @pytest.mark.asyncio
    async def test_delete_category(
        self, access_token_admin, access_token_user, client, create_incoming_categories
    ):
        """Удаляем категорию"""
        category_id_1 = str(create_incoming_categories[0].id)
        category_id_2 = str(create_incoming_categories[1].id)
        category_id_3 = str(create_incoming_categories[2].id)

        # Удаляем админом
        response = await client.delete(
            self.endpoint + category_id_1, headers=access_token_admin
        )
        assert response.status_code == HTTPStatus.OK

        response = await client.get(
            self.endpoint + category_id_1, headers=access_token_admin
        )
        assert response.status_code == HTTPStatus.NOT_FOUND

        # Удаляем пользователем
        response = await client.delete(
            self.endpoint + category_id_2, headers=access_token_user
        )
        assert response.status_code == HTTPStatus.FORBIDDEN

        response = await client.get(
            self.endpoint + category_id_2, headers=access_token_admin
        )
        assert response.status_code == HTTPStatus.OK

        # Удаляем неавторизованным
        response = await client.delete(self.endpoint + category_id_3)
        assert response.status_code == HTTPStatus.UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_update_category(
        self, access_token_admin, access_token_user, client, create_incoming_categories
    ):
        """Обновляем категорию"""
        category = create_incoming_categories[0]
        category_id = str(category.id)
        category.name = "new_name"

        # Обновляем админом
        response = await client.patch(
            self.endpoint,
            headers=access_token_admin,
            json={
                "name": category.name,
                "description": category.description,
            },
            params={"category_id": category_id},
        )
        assert response.status_code == HTTPStatus.OK
        assert response.json()["name"] == category.name

        # Обновляем юзером
        response = await client.patch(
            self.endpoint,
            headers=access_token_user,
            json={
                "name": category.name,
                "description": category.description,
            },
            params={"category_id": category_id},
        )
        assert response.status_code == HTTPStatus.FORBIDDEN

        # Обновляем неавторизованным
        response = await client.patch(
            self.endpoint,
            json={
                "name": category.name,
                "description": category.description,
            },
            params={"category_id": category_id},
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED
