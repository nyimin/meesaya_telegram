"""init_schema_with_knowledge_base

Revision ID: 7304d3eebf55
Revises: 
Create Date: 2025-12-24 14:18:14.396819

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7304d3eebf55'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 1. Chat History
    op.create_table(
        'chat_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(length=50), nullable=True),
        sa.Column('role', sa.String(length=20), nullable=True),
        sa.Column('message_text', sa.Text(), nullable=True),
        sa.Column('timestamp', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # 2. Market Packages
    op.create_table(
        'market_packages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tier_code', sa.String(length=10), nullable=True),
        sa.Column('name', sa.String(length=100), nullable=True),
        sa.Column('system_voltage', sa.Integer(), nullable=True),
        sa.Column('inverter_kw', sa.Float(), nullable=True),
        sa.Column('battery_kwh', sa.Float(), nullable=True),
        sa.Column('est_price_low', sa.Integer(), nullable=True),
        sa.Column('est_price_high', sa.Integer(), nullable=True),
        sa.Column('install_cost', sa.Integer(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_portable', sa.Boolean(), server_default='False', nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # 3. Products Inventory
    op.create_table(
        'products_inventory',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=True),
        sa.Column('brand', sa.String(length=50), nullable=True),
        sa.Column('model', sa.String(length=50), nullable=True),
        sa.Column('specs', sa.String(length=50), nullable=True),
        sa.Column('price', sa.Integer(), nullable=True),
        sa.Column('warranty_years', sa.Integer(), nullable=True),
        sa.Column('tags', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # 4. Knowledge Base (New RAG Table)
    op.create_table(
        'knowledge_base',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('knowledge_base')
    op.drop_table('products_inventory')
    op.drop_table('market_packages')
    op.drop_table('chat_history')
