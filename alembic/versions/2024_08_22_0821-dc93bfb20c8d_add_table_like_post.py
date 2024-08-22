"""add table like_post

Revision ID: dc93bfb20c8d
Revises: 29d47921db2e
Create Date: 2024-08-22 08:21:13.317464

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "dc93bfb20c8d"
down_revision: Union[str, None] = "29d47921db2e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "likes_post",
        sa.Column("post_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["post_id"],
            ["posts.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("post_id", "user_id"),
        sa.UniqueConstraint(
            "user_id", "post_id", name="idx_unique_user_tweet"
        ),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("likes_post")
    # ### end Alembic commands ###
