"""test1

Revision ID: 0e5f78c14db5
Revises:
Create Date: 2023-07-07 18:49:36.624111

"""
import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = "0e5f78c14db5"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "Users",
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint("user_id"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("Users")
    # ### end Alembic commands ###
