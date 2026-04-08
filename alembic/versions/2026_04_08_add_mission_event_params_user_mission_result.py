"""add mission event parameters and user_mission result + constraints

Revision ID: f0a1b2c3d4e5
Revises: f1f2cee972cb
Create Date: 2026-04-08 15:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'f0a1b2c3d4e5'
down_revision = 'f1f2cee972cb'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # add parameters (json) and order to mission_events
    op.add_column('mission_events', sa.Column('parameters', sa.JSON(), nullable=True))
    op.add_column('mission_events', sa.Column('order', sa.Integer(), nullable=False, server_default='0'))

    # add result json to user_missions
    op.add_column('user_missions', sa.Column('result', sa.JSON(), nullable=True))

    # add index on user_missions(ends_at, status)
    op.create_index('ix_user_missions_ends_at_status', 'user_missions', ['ends_at', 'status'])

    # add unique constraint to mission_characters (user_mission_id, character_id)
    op.create_unique_constraint('uq_mission_char_user_mission_character', 'mission_characters', ['user_mission_id', 'character_id'])


def downgrade() -> None:
    op.drop_constraint('uq_mission_char_user_mission_character', 'mission_characters', type_='unique')
    op.drop_index('ix_user_missions_ends_at_status', table_name='user_missions')
    op.drop_column('user_missions', 'result')
    op.drop_column('mission_events', 'order')
    op.drop_column('mission_events', 'parameters')
