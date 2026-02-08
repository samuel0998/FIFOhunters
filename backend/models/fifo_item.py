from datetime import datetime, date
from extensions import db

class FIFOItem(db.Model):
    __tablename__ = "fifo_items"

    id = db.Column(db.Integer, primary_key=True)

    nfe_id = db.Column(db.String(50))
    nota = db.Column(db.String(50))
    vendor = db.Column(db.String(100))

    isa = db.Column(db.String(50), index=True)
    isd = db.Column(db.String(50), index=True)

    description = db.Column(db.Text)

    po = db.Column(db.String(50), index=True)
    asin = db.Column(db.String(20), index=True)
    ean = db.Column(db.String(20), index=True)
    ean_taxable = db.Column(db.String(20))

    received = db.Column(db.Integer)
    expected = db.Column(db.Integer)

    opened_since = db.Column(db.Date)
    last_receipt = db.Column(db.Date)

    fifo_days = db.Column(db.Integer)
    fifo_status = db.Column(db.String(10))

    difference = db.Column(db.Integer)
    shortage_type = db.Column(db.String(20))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
