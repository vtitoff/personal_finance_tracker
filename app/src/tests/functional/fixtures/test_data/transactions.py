from random import choice, randint

import pytest_asyncio
from models import IncomingTransaction, OutgoingTransaction
from tests.functional.fixtures.postgres import db_session
from tests.functional.fixtures.test_data.categories import (
    create_incoming_categories, create_outgoing_categories)
from tests.functional.fixtures.test_data.wallets import create_wallets


@pytest_asyncio.fixture(loop_scope="session")
async def create_outgoing_transactions(
    db_session, create_outgoing_categories, create_wallets
):
    transactions = []
    for wallet in create_wallets:
        for i in range(15):
            transaction = OutgoingTransaction(
                amount=randint(1, 10),
                description="",
                category_id=choice(create_outgoing_categories).id,
                wallet_id=wallet.id,
                user_id=wallet.user_id,
            )
            transactions.append(transaction)
    db_session.add_all(transactions)
    await db_session.commit()
    return transactions


# @pytest_asyncio.fixture(loop_scope="session")
# async def create_incoming_transactions(db_session):
#     transactions = []
#     for i in range(10):
#         transaction = IncomingTransaction(
#             name=f"Test Category {i}",
#             description=f"Description {i}",
#         )
#         transactions.append(transaction)
#     db_session.add_all(transactions)
#     await db_session.commit()
#     return transactions
