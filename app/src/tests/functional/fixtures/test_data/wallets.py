from random import randint

import pytest_asyncio
from models import CurrencyEnum, Wallet
from tests.functional.fixtures.postgres import db_session
from tests.functional.fixtures.test_data.users import create_users


@pytest_asyncio.fixture(loop_scope="session")
async def create_wallets(db_session, create_users):
    wallets = []
    for user in create_users:
        for i in range(10):
            wallet = Wallet(
                name=user.last_name + f" wallet {i}",
                description="",
                amount=randint(1, 100),
                currency=CurrencyEnum.USD,
                user_id=user.id,
            )
            wallets.append(wallet)
    db_session.add_all(wallets)
    await db_session.commit()
    return wallets
