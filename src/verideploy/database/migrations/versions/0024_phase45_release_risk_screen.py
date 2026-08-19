"""Phase 45 release-risk screen source metadata.

Revision ID: 0024_phase45_release_risk_screen
Revises: 0023_phase42_long_running_workflow_durability
"""
from alembic import op
import sqlalchemy as sa
revision="0024_phase45_release_risk_screen"
down_revision="0023_phase42_long_running_workflow_durability"
branch_labels=None
depends_on=None

def upgrade()->None:
    op.add_column("release_risk_assessments",sa.Column("changed_files_json",sa.Text(),nullable=True))
    op.execute("UPDATE release_risk_assessments SET changed_files_json='[]' WHERE changed_files_json IS NULL")
    op.alter_column("release_risk_assessments","changed_files_json",nullable=False,server_default="[]")
    op.create_index("ix_phase45_release_selector","release_risk_assessments",["tenant_id","updated_at","created_at"])

def downgrade()->None:
    op.drop_index("ix_phase45_release_selector",table_name="release_risk_assessments")
    op.drop_column("release_risk_assessments","changed_files_json")
