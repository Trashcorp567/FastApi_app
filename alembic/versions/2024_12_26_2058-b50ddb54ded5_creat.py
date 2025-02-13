"""creat

Revision ID: b50ddb54ded5
Revises: 18fb526942a7
Create Date: 2024-12-26 20:58:58.905633

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "b50ddb54ded5"
down_revision: Union[str, None] = "18fb526942a7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "order_product_association",
        sa.Column("count", sa.Integer(), server_default="1", nullable=False),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("order_product_association", "count")
    # ### end Alembic commands ###
