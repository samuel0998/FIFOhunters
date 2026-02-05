from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "b1a2c3d4"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "fifo_items",
        sa.Column("id", sa.Integer, primary_key=True),

        sa.Column("nfe_id", sa.String(50)),
        sa.Column("nota", sa.String(50)),
        sa.Column("vendor", sa.String(100)),

        sa.Column("isa", sa.String(50)),
        sa.Column("isd", sa.String(50)),

        sa.Column("description", sa.Text),

        sa.Column("po", sa.String(50)),
        sa.Column("asin", sa.String(20)),
        sa.Column("ean", sa.String(20)),
        sa.Column("ean_taxable", sa.String(20)),

        sa.Column("received", sa.Integer),
        sa.Column("expected", sa.Integer),

        sa.Column("opened_since", sa.Date),
        sa.Column("last_receipt", sa.Date),

        sa.Column("fifo_days", sa.Integer),
        sa.Column("fifo_status", sa.String(10)),

        sa.Column("difference", sa.Integer),
        sa.Column("shortage_type", sa.String(20)),

        sa.Column("created_at", sa.DateTime),
        sa.Column("updated_at", sa.DateTime),
    )


def downgrade():
    op.drop_table("fifo_items")
