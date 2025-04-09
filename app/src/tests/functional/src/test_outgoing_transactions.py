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
        """Ищем несуществующую категорию"""
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
