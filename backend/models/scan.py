# routes/scan.py
from flask import Blueprint, request, jsonify
from datetime import date
from sqlalchemy import or_, func
from models.fifo_item import FIFOItem

scan_bp = Blueprint("scan", __name__)


def calc_status(days):
    if days <= 3:
        return "OK"
    elif days <= 7:
        return "ATENCAO"
    return "CRITICO"


@scan_bp.route("/scan", methods=["GET"])
def scan():
    code = request.args.get("code")

    if not code:
        return jsonify({"error": "Código não informado"}), 400

    code = code.strip()

    itens = FIFOItem.query.filter(
        or_(
            func.trim(FIFOItem.ean) == code,
            func.trim(FIFOItem.ean_taxable) == code,
            FIFOItem.asin == code,
            FIFOItem.isd == code
        )
    ).all()

    if not itens:
        return jsonify([])

    hoje = date.today()
    resultado = []

    for item in itens:
        fifo_days = (
            (hoje - item.opened_since).days
            if item.opened_since else 0
        )

        resultado.append({
            "produto": item.description,
            "nfe": item.nfe_id,
            "isa": item.isa or "-",
            "isd": item.isd,
            "data_abertura": item.opened_since.isoformat() if item.opened_since else None,
            "quantidade_esperada": item.expected or 0,
            "quantidade_recebida": item.received or 0,
            "falta_receber": (item.expected or 0) - (item.received or 0),
            "fifo_days": fifo_days,
            "status": calc_status(fifo_days)
        })

    return jsonify(resultado)
