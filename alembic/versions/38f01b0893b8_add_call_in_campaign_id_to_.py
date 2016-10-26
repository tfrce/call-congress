"""Add call_in_campaign_id to TwilioPhoneNumber

Revision ID: 38f01b0893b8
Revises: 3c34cfd19bf8
Create Date: 2016-10-21 18:59:13.190060

"""

# revision identifiers, used by Alembic.
revision = '38f01b0893b8'
down_revision = '3c34cfd19bf8'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    with op.batch_alter_table('campaign_phone') as batch_op:
        batch_op.add_column(sa.Column('call_in_campaign_id',
                                      sa.Integer(),
                                      sa.ForeignKey('campaign_campaign.id'),
                                      nullable=True))

def downgrade():
    with op.batch_alter_table('campaign_phone') as batch_op:
        batch_op.drop_column('call_in_campaign_id')
