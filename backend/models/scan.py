from flask import Blueprint, request, jsonify
from datetime import date
from models.fifo_item import FIFOItem

scan_bp = Blueprint("scan", __name__)


@scan_bp.route("/scan", methods=["GET"])
def scan_item():
    code = request.args.get("code")

    if not code:
        return jsonify({"error": "Código não informado"}), 400

    query = FIFOItem.query.filter(
        (FIFOItem.ean == code) |
        (FIFOItem.asin == code) |
        (FIFOItem.isd == code)
    ).all()

    if not query:
        return jsonify({"error": "Nenhum dado encontrado"}), 404

    hoje = date.today()
    resultado = []

    for item in query:
        fifo_days = (hoje - item.opened_since).days if item.opened_since else None
        falta = (item.expected or 0) - (item.received or 0)

        # STATUS VISUAL
        if fifo_days is None:
            status = "OK"
        elif fifo_days <= 7:
            status = "OK"
        elif fifo_days <= 14:
            status = "ATENÇÃO"
        else:
            status = "CRÍTICO"

        resultado.append({
            "descricao": item.description,
            "nfe": item.nfe_id,
            "isd": item.isd,
            "opened_since": item.opened_since.isoformat() if item.opened_since else None,
            "expected": item.expected,
            "received": item.received,
            "falta": falta,
            "fifo_days": fifo_days,
            "status": status
        })

    return jsonify(resultado)
