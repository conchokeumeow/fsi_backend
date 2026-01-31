"""add_course_display_name_field

Revision ID: fd2a4a438aac
Revises: a656e3ca1e0f
Create Date: 2026-01-27 20:51:32.505021

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = 'fd2a4a438aac'
down_revision = 'a656e3ca1e0f'
branch_labels = None
depends_on = None


def upgrade():
    # Add course_display_name column
    op.add_column('course', sa.Column('course_display_name', sa.String(length=255), nullable=True))
    op.create_index(op.f('ix_course_course_display_name'), 'course', ['course_display_name'], unique=False)


def downgrade():
    # Remove index and column
    op.drop_index(op.f('ix_course_course_display_name'), table_name='course')
    op.drop_column('course', 'course_display_name')
