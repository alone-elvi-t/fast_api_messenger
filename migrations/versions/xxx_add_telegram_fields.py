"""add telegram fields

Revision ID: xxx
Revises: previous_revision
Create Date: 2024-03-23 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.add_column('users', sa.Column('telegram_id', sa.BigInteger(), nullable=True))
    op.add_column('users', sa.Column('is_online', sa.Boolean(), server_default='false'))

def downgrade():
    op.drop_column('users', 'telegram_id')
    op.drop_column('users', 'is_online')
