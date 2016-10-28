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

    connection = op.get_bind()
    campaign_call_in_numbers = connection.execute(
        """SELECT campaign_phone_numbers.campaign_id, campaign_phone_numbers.phone_id
           FROM   campaign_phone_numbers
           INNER JOIN campaign_phone ON campaign_phone_numbers.phone_id = campaign_phone.id
           WHERE campaign_phone.call_in_allowed"""
    )

    for (campaign_id, phone_id) in campaign_call_in_numbers:
        connection.execute("""UPDATE campaign_phone
                              SET    call_in_campaign_id = """+str(campaign_id)+"""
                              WHERE  campaign_phone.id = """+str(phone_id))

def downgrade():
    with op.batch_alter_table('campaign_phone') as batch_op:
        batch_op.drop_column('call_in_campaign_id')
