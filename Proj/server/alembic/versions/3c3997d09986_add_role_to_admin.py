"""add role to admin

Revision ID: 3c3997d09986
Revises: c049ee67a17d
Create Date: 2025-10-24 12:47:59.938679

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3c3997d09986'
down_revision: Union[str, Sequence[str], None] = 'c049ee67a17d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    bind = op.get_bind()
    insp = sa.inspect(bind)

    # 1) 列是否已存在？
    cols = [c["name"] for c in insp.get_columns("admin")]
    if "role" not in cols:
        op.add_column(
            "admin",
            sa.Column("role", sa.String(length=20), nullable=False, server_default="admin"),
        )
        # 建完列后去掉 server_default（可选）
        op.alter_column("admin", "role", server_default=None)

    # 2) 索引是否已存在？（可选）
    idx_names = [ix["name"] for ix in insp.get_indexes("admin")]
    if "ix_admin_role" not in idx_names:
        op.create_index("ix_admin_role", "admin", ["role"])