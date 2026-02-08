import pandas as pd
from flask import Blueprint, request, jsonify
from models.fifo_item import FIFOItem
from extensions import db

upload_bp = Blueprint("upload", __name__)


@upload_bp.route("/upload/excel", methods=["POST"])
def upload_excel():
    if "file" not in request.files:
        return jsonify({"error": "Arquivo não enviado"}), 400

    file = request.files["file"]

    if not file.filename.endswith(".xlsx"):
        return jsonify({"error": "Formato inválido. Envie .xlsx"}), 400

    try:
        df = pd.read_excel(file)

        # 🔥 normaliza colunas
        df.columns = (
            df.columns
            .str.strip()
            .str.lower()
            .str.replace(" ", "_")
            .str.replace("-", "_")
        )

        # 🔥 limpa tudo antes de inserir
        db.session.query(FIFOItem).delete()

        itens = []

        for _, row in df.iterrows():
            item = FIFOItem(
                nfe_id=str(row.get("nf_e_id", "")),
                vendor=str(row.get("vendor", "")),
                isa=str(row.get("isa", "")),
                isd=str(row.get("isd", "")),
                description=str(row.get("description", "")),
                po=str(row.get("po", "")),
                asin=str(row.get("asin", "")),
                ean=str(row.get("ean", "")),
                ean_taxable=str(row.get("ean_taxable", "")),
                received=int(row.get("received", 0)) if not pd.isna(row.get("received")) else 0,
                expected=int(row.get("expected", 0)) if not pd.isna(row.get("expected")) else 0,
                opened_since=pd.to_datetime(row.get("opened_since"), errors="coerce"),
                last_receipt=pd.to_datetime(row.get("last_receipt"), errors="coerce"),
                difference=int(row.get("overage/shortage", 0))
                if "overage/shortage" in df.columns and not pd.isna(row.get("overage/shortage"))
                else None
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
