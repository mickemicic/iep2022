"""dodat korisnik u Order

Revision ID: 3865b2a09cf4
Revises: b2fcede82d52
Create Date: 2023-01-17 14:12:55.341811

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '3865b2a09cf4'
down_revision = 'b2fcede82d52'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('orders', sa.Column('buyer', sa.String(length=256), nullable=False))
    op.drop_column('orders', 'userEmail')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('orders', sa.Column('userEmail', mysql.VARCHAR(length=256), nullable=False))
    op.drop_column('orders', 'buyer')
    # ### end Alembic commands ###