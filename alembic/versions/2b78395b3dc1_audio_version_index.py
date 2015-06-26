""" unique index on audio recording campaign / key / selected

Revision ID: 2b78395b3dc1
Revises: 50b6324aa438
Create Date: 2015-06-25 22:09:39.345793

"""

# revision identifiers, used by Alembic.
revision = '2b78395b3dc1'
down_revision = '50b6324aa438'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa

def upgrade():
    op.create_index('only_one_selected_version', 'campaign_recording', ['campaign_id', 'key', 'selected'], unique=True, postgresql_where=sa.text(u'campaign_recording.selected = 0'))
    

def downgrade():
    op.drop_index('only_one_selected_version')
