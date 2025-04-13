from http import HTTPStatus
from random import choice, randint
from uuid import uuid4

import pytest
from models.outgoing_transaction import OutgoingTransaction
from tests.functional.fixtures.auth import access_token_user, auth_header


class TestOutgoingTransactions:
    def setup_method(self):
        self.endpoint = "/api/v1/transactions/outgoing/"

    @pytest.mark.asyncio
    async def test_get_user_transactions(
        self, access_token_admin, client, create_outgoing_transactions
    ):
        """Проверяем транзакции пользователя"""
        endpoint = "/api/v1/transactions/outgoing/users/"
        user_id = str(create_outgoing_transactions[0].user_id)

        # Проверяем админом
        response = await client.get(endpoint + user_id, headers=access_token_admin)
        assert response.status_code == HTTPStatus.OK
        assert len(response.json()["items"]) == 50

        # Проверяем тем же пользователем
        headers = auth_header([], user_id)
        response = await client.get(endpoint + user_id, headers=headers)
        assert response.status_code == HTTPStatus.OK
        assert response.json()["items"][0]["user_id"] == user_id

        # Проверяем пользователем транзакции чужого пользователя
        user_id_2 = str(uuid4())
        headers = auth_header([], user_id_2)
        response = await client.get(endpoint + user_id, headers=headers)
        assert response.status_code == HTTPStatus.FORBIDDEN
        assert response.json() == {"detail": "Forbidden"}

        # Проверяем неавторизованным пользователем
        response = await client.get(endpoint + user_id)
        assert response.status_code == HTTPStatus.UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_get_transaction(
        self, access_token_admin, client, create_outgoing_transactions
    ):
        """Ищем существующую транзакцию"""
        transaction_id = str(create_outgoing_transactions[0].id)
        response = await client.get(
            self.endpoint + transaction_id, headers=access_token_admin
        )
        assert response.status_code == HTTPStatus.OK
        assert response.json()["id"] == transaction_id

    @pytest.mark.asyncio
    async def test_get_non_existing_transaction(
        self, access_token_admin, client, create_outgoing_transactions
    ):
        """Ищем несуществующую транзакцию"""
        transaction_id = str(uuid4())
        response = await client.get(
            self.endpoint + transaction_id, headers=access_token_admin
        )
        assert response.status_code == HTTPStatus.NOT_FOUND

    @pytest.mark.asyncio
    async def test_create_transaction(
        self,
        access_token_admin,
        client,
        create_outgoing_transactions,
        create_wallets,
        create_outgoing_categories,
    ):
        """Создаем категорию"""

        wallet = create_wallets[0]

        transaction = OutgoingTransaction(
            amount=randint(1, 10),
            description="",
            category_id=choice(create_outgoing_categories).id,
            wallet_id=wallet.id,
            user_id=wallet.user_id,
        )

        # Создаем админом
        response = await client.post(
            self.endpoint,
            headers=access_token_admin,
            json={
                "amount": transaction.amount,
                "description": transaction.description,
                "category_id": str(transaction.category_id),
                "wallet_id": str(transaction.wallet_id),
                "user_id": str(transaction.user_id),
            },
        )
        assert response.status_code == HTTPStatus.OK
        assert response.json()["wallet_id"] == str(transaction.wallet_id)
        assert response.json()["amount"] == transaction.amount

        # Создаем тем же пользователем
        headers = auth_header([], str(wallet.user_id))
        response = await client.post(
            self.endpoint,
            headers=headers,
            json={
                "amount": transaction.amount,
                "description": transaction.description,
                "category_id": str(transaction.category_id),
                "wallet_id": str(transaction.wallet_id),
                "user_id": str(transaction.user_id),
            },
        )
        assert response.status_code == HTTPStatus.OK
        assert response.json()["wallet_id"] == str(transaction.wallet_id)
        assert response.json()["amount"] == transaction.amount

        # Создаем чужим пользователем
        headers = auth_header([], str(uuid4()))
        response = await client.post(
            self.endpoint,
            headers=headers,
            json={
                "amount": transaction.amount,
                "description": transaction.description,
                "category_id": str(transaction.category_id),
                "wallet_id": str(transaction.wallet_id),
                "user_id": str(transaction.user_id),
            },
        )
        assert response.status_code == HTTPStatus.FORBIDDEN
        assert response.json() == {"detail": "Forbidden"}

    @pytest.mark.asyncio
    async def test_delete_transaction(
        self,
        access_token_admin,
        access_token_user,
        client,
        create_outgoing_transactions,
    ):
        """Удаляем транзакцию"""
        transaction_id_1 = str(create_outgoing_transactions[0].id)
        transaction_id_2 = str(create_outgoing_transactions[1].id)
        transaction_id_3 = str(create_outgoing_transactions[2].id)

        # Удаляем админом
        response = await client.delete(
            self.endpoint + transaction_id_1, headers=access_token_admin
        )
        assert response.status_code == HTTPStatus.OK

        response = await client.get(
            self.endpoint + transaction_id_1, headers=access_token_admin
        )
        assert response.status_code == HTTPStatus.NOT_FOUND

        # Удаляем пользователем
        response = await client.delete(
            self.endpoint + transaction_id_2, headers=access_token_user
        )
        assert response.status_code == HTTPStatus.OK

        response = await client.get(
            self.endpoint + transaction_id_2, headers=access_token_admin
        )
        assert response.status_code == HTTPStatus.NOT_FOUND

        # Удаляем неавторизованным
        response = await client.delete(self.endpoint + transaction_id_3)
        assert response.status_code == HTTPStatus.UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_update_transaction(
        self,
        access_token_admin,
        access_token_user,
        client,
        create_outgoing_transactions,
    ):
        """Обновляем транзакцию"""

        transaction = create_outgoing_transactions[0]
        transaction_id = str(transaction.id)
        transaction.amount += 100

        # Обновляем админом
        response = await client.patch(
            self.endpoint + transaction_id,
            headers=access_token_admin,
            json={
                "amount": transaction.amount,
                "description": transaction.description,
                "category_id": str(transaction.category_id),
                "wallet_id": str(transaction.wallet_id),
                "user_id": str(transaction.user_id),
            },
        )
        assert response.status_code == HTTPStatus.OK
        assert response.json()["amount"] == transaction.amount

        # Обновляем тем же пользователем
        transaction = create_outgoing_transactions[1]
        transaction_id = str(transaction.id)
        transaction.amount += 100
        user_id = str(transaction.user_id)

        headers = auth_header([], user_id)

        response = await client.patch(
            self.endpoint + transaction_id,
            headers=headers,
            json={
                "amount": transaction.amount,
                "description": transaction.description,
                "category_id": str(transaction.category_id),
                "wallet_id": str(transaction.wallet_id),
                "user_id": str(transaction.user_id),
                "date": str(transaction.date)
            },
        )
        assert response.status_code == HTTPStatus.OK
        assert response.json()["amount"] == transaction.amount

        # Обновляем неавторизованным
        response = await client.patch(
            self.endpoint + transaction_id,
            json={
                "amount": transaction.amount,
                "description": transaction.description,
                "category_id": str(transaction.category_id),
                "wallet_id": str(transaction.wallet_id),
                "user_id": str(transaction.user_id),
                "date": str(transaction.date)
            },
            params={"transaction_id": transaction_id},
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED
