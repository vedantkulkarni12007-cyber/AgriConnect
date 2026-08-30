"""add_missing_indexes

Revision ID: 6442a44b1f27
Revises: 0111b944a435
Create Date: 2026-08-28 18:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '6442a44b1f27'
down_revision: Union[str, Sequence[str], None] = '0111b944a435'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute('CREATE INDEX IF NOT EXISTS ix_lots_public_id_status ON lots USING btree (public_id, status)')
        op.execute('CREATE INDEX IF NOT EXISTS ix_price_obs_date_brin ON price_observations USING brin (price_date)')
        op.execute('CREATE INDEX IF NOT EXISTS ix_notifications_user_read ON notifications USING btree (user_id, is_read)')
    else:
        op.execute('CREATE INDEX IF NOT EXISTS ix_lots_public_id_status ON lots (public_id, status)')
        op.execute('CREATE INDEX IF NOT EXISTS ix_price_obs_date_brin ON price_observations (price_date)')
        op.execute('CREATE INDEX IF NOT EXISTS ix_notifications_user_read ON notifications (user_id, is_read)')


def downgrade() -> None:
    op.execute('DROP INDEX IF EXISTS ix_lots_public_id_status')
    op.execute('DROP INDEX IF EXISTS ix_price_obs_date_brin')
    op.execute('DROP INDEX IF EXISTS ix_notifications_user_read')