"""add filesize in fileupload

Revision ID: 1391392a939e
Revises: 2a2142d11156
Create Date: 2024-01-14 15:32:29.510215

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1391392a939e'
down_revision = '2a2142d11156'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('upload_file', schema=None) as batch_op:
        batch_op.add_column(sa.Column('filesize', sa.Integer(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('upload_file', schema=None) as batch_op:
        batch_op.drop_column('filesize')

    # ### end Alembic commands ###
