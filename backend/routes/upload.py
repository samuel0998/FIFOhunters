# routes/upload.py
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

    if not file.filename.lower().endswith(".xlsx"):
        return jsonify({"error": "Formato inválido. Envie .xlsx"}), 400

    try:
        df = pd.read_excel(file)

        itens = []
        for _, row in df.iterrows():
            item = FIFOItem(
                sku=str(row["sku"]).strip(),
                descricao=str(row["descricao"]).strip()
                if "descricao" in df.columns else "",
                quantidade=int(row["quantidade"]),
                data_entrada=pd.to_datetime(
                    row["data_entrada"], errors="coerce"
                ).date()
            )
            itens.append(item)

        db.session.bulk_save_objects(itens)
        db.session.commit()

        return jsonify({
            "status": "ok",
            "registros_inseridos": len(itens)
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
