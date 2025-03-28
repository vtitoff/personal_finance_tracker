"""change on_delete logic in models

Revision ID: 0b8825627df6
Revises: 09b356cf5bba
Create Date: 2025-03-15 14:46:50.534854

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0b8825627df6"
down_revision: Union[str, None] = "09b356cf5bba"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint("payment_payment_method_id_fkey", "payment", type_="foreignkey")
    op.drop_constraint("payment_category_id_fkey", "payment", type_="foreignkey")
    op.create_foreign_key(
        None,
        "payment",
        "paymentmethod",
        ["payment_method_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        None, "payment", "paymentcategory", ["category_id"], ["id"], ondelete="SET NULL"
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, "payment", type_="foreignkey")
    op.drop_constraint(None, "payment", type_="foreignkey")
    op.create_foreign_key(
        "payment_category_id_fkey",
        "payment",
        "paymentcategory",
        ["category_id"],
        ["id"],
    )
    op.create_foreign_key(
        "payment_payment_method_id_fkey",
        "payment",
        "paymentmethod",
        ["payment_method_id"],
        ["id"],
    )
    # ### end Alembic commands ###
