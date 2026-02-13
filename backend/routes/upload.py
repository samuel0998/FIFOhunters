# routes/upload.py

import pandas as pd
from flask import Blueprint, request, jsonify
from sqlalchemy import text
from models.fifo_item import FIFOItem
from extensions import db

upload_bp = Blueprint("upload", __name__)


# ---------------- HELPERS ---------------- #

def safe_str(value):
    if pd.isna(value):
        return None

    # Corrige EAN/ISA grandes que viram float
    if isinstance(value, float):
        return format(int(value), "d")

    return str(value).strip()


def safe_int(value):
    if pd.isna(value):
        return 0
    try:
        return int(value)
    except Exception:
        return 0


def safe_date(value):
    if pd.isna(value):
        return None

    dt = pd.to_datetime(value, errors="coerce")
    if pd.isna(dt):
        return None

    return dt.date()


# ---------------- ROUTE ---------------- #

@upload_bp.route("/upload/excel", methods=["POST"])
def upload_excel():

    if "file" not in request.files:
        return jsonify({"error": "Arquivo não enviado"}), 400

    file = request.files["file"]

    if not file.filename.lower().endswith(".xlsx"):
        return jsonify({"error": "Formato inválido. Envie .xlsx"}), 400

    try:
        df = pd.read_excel(file)

        # Normaliza colunas
        df.columns = (
            df.columns
            .str.strip()
            .str.lower()
            .str.replace(" ", "_")
            .str.replace("-", "_")
            .str.replace("/", "_")
        )

        # 🔥 APAGA TUDO COMPLETAMENTE
        db.session.execute(text("TRUNCATE TABLE fifo_items RESTART IDENTITY"))
        db.session.commit()

        itens = []

        for _, row in df.iterrows():

            item = FIFOItem(
                nfe_id=safe_str(row.get("nf_e_id")),
                vendor=safe_str(row.get("vendor")),

                isa=safe_str(row.get("isa")),
                isd=safe_str(row.get("isd")),

                description=safe_str(row.get("description")),
                po=safe_str(row.get("po")),
                asin=safe_str(row.get("asin")),

                ean=safe_str(row.get("ean")),
                ean_taxable=safe_str(row.get("ean_taxable")),

                received=safe_int(row.get("received")),
                expected=safe_int(row.get("expected")),

                difference=safe_int(
                    row.get("overage_shortage")
                    if "overage_shortage" in df.columns
                    else None
                ),

                opened_since=safe_date(row.get("opened_since")),
                last_receipt=safe_date(row.get("last_receipt")),
            )

            itens.append(item)

        db.session.bulk_save_objects(itens)
        db.session.commit()

        return jsonify({
            "status": "ok",
            "registros_importados": len(itens)
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
