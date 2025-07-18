"""initial migration

Revision ID: 36d134af2e13
Revises: 
Create Date: 2025-07-18 18:58:25.118596

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '36d134af2e13'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('merchants',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=120), nullable=False),
    sa.Column('password', sa.String(length=120), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.create_table('admins',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=120), nullable=False),
    sa.Column('password', sa.String(length=120), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('merchant_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['merchant_id'], ['merchants.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.create_table('stores',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('merchant_id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['merchant_id'], ['merchants.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('clerks',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=120), nullable=False),
    sa.Column('password', sa.String(length=120), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('admin_id', sa.Integer(), nullable=False),
    sa.Column('store_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['admin_id'], ['admins.id'], ),
    sa.ForeignKeyConstraint(['store_id'], ['stores.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.create_table('items',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('quantity_received', sa.Integer(), nullable=False),
    sa.Column('quantity_in_stock', sa.Integer(), nullable=False),
    sa.Column('quantity_spoilt', sa.Integer(), nullable=False),
    sa.Column('buying_price', sa.Float(), nullable=False),
    sa.Column('selling_price', sa.Float(), nullable=False),
    sa.Column('payment_status', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('store_id', sa.Integer(), nullable=False),
    sa.Column('clerk_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['clerk_id'], ['clerks.id'], ),
    sa.ForeignKeyConstraint(['store_id'], ['stores.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('supply_requests',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('item_id', sa.Integer(), nullable=False),
    sa.Column('store_id', sa.Integer(), nullable=False),
    sa.Column('clerk_id', sa.Integer(), nullable=False),
    sa.Column('quantity', sa.Integer(), nullable=False),
    sa.Column('status', sa.String(length=50), nullable=True),
    sa.Column('requested_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['clerk_id'], ['clerks.id'], ),
    sa.ForeignKeyConstraint(['item_id'], ['items.id'], ),
    sa.ForeignKeyConstraint(['store_id'], ['stores.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('updates',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('action', sa.String(length=100), nullable=False),
    sa.Column('description', sa.Text(), nullable=False),
    sa.Column('merchant_id', sa.Integer(), nullable=True),
    sa.Column('admin_id', sa.Integer(), nullable=True),
    sa.Column('clerk_id', sa.Integer(), nullable=True),
    sa.Column('item_id', sa.Integer(), nullable=True),
    sa.Column('supply_request_id', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['admin_id'], ['admins.id'], ),
    sa.ForeignKeyConstraint(['clerk_id'], ['clerks.id'], ),
    sa.ForeignKeyConstraint(['item_id'], ['items.id'], ),
    sa.ForeignKeyConstraint(['merchant_id'], ['merchants.id'], ),
    sa.ForeignKeyConstraint(['supply_request_id'], ['supply_requests.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('updates')
    op.drop_table('supply_requests')
    op.drop_table('items')
    op.drop_table('clerks')
    op.drop_table('stores')
    op.drop_table('admins')
    op.drop_table('merchants')
    # ### end Alembic commands ###
