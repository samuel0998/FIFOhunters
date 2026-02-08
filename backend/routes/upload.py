# routes/upload.py
import pandas as pd
from flask import Blueprint, request, jsonify
from models.fifo_item import FIFOItem
from extensions import db

upload_bp = Blueprint("upload", __name__)


def safe_date(value):
    if pd.isna(value):
        return None
    return pd.to_datetime(value, errors="coerce")


def normalize_text(value):
    if pd.isna(value):
        return None
    return str(value).strip()


def normalize_ean(value):
    if pd.isna(value):
        return None
    return str(value).split(".")[0].strip()


@upload_bp.route("/upload/excel", methods=["POST"])
def upload_excel():
    if "file" not in request.files:
        return jsonify({"error": "Arquivo não enviado"}), 400

    file = request.files["file"]

    if not file.filename.endswith(".xlsx"):
        return jsonify({"error": "Formato inválido. Envie .xlsx"}), 400

    try:
        df = pd.read_excel(file)

        # normaliza colunas
        df.columns = (
            df.columns
            .str.strip()
            .str.lower()
            .str.replace(" ", "_")
            .str.replace("-", "_")
            .str.replace("/", "_")
        )

        # LIMPA TUDO ANTES DE REINSERIR
        db.session.query(FIFOItem).delete()

        itens = []

        for _, row in df.iterrows():
            item = FIFOItem(
                nfe_id=normalize_text(row.get("nf_e_id")),
                vendor=normalize_text(row.get("vendor")),
                isa=normalize_text(row.get("isa")),
                isd=normalize_text(row.get("isd")),
                description=normalize_text(row.get("description")),
                po=normalize_text(row.get("po")),
                asin=normalize_text(row.get("asin")),
                ean=normalize_ean(row.get("ean")),
                ean_taxable=normalize_ean(row.get("ean_taxable")),
                received=int(row.get("received", 0)) if not pd.isna(row.get("received")) else 0,
                expected=int(row.get("expected", 0)) if not pd.isna(row.get("expected")) else 0,
                difference=int(row.get("overage_shortage", 0))
                if "overage_shortage" in df.columns and not pd.isna(row.get("overage_shortage"))
                else None,
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
