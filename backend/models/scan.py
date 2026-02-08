# routes/scan.py
from flask import Blueprint, request, jsonify
from datetime import date
from models.fifo_item import FIFOItem
from extensions import db

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

    # busca por EAN, ASIN ou ISD
    itens = FIFOItem.query.filter(
        (FIFOItem.ean == code) |
        (FIFOItem.asin == code) |
        (FIFOItem.isd == code)
    ).all()

    if not itens:
        return jsonify([])

    hoje = date.today()
    resultado = []

    for item in itens:
        if item.opened_since:
            fifo_days = (hoje - item.opened_since).days
        else:
            fifo_days = 0

        status = calc_status(fifo_days)

        resultado.append({
            "produto": item.description,
            "nfe": item.nfe_id,
            "isd": item.isd,
            "data_abertura": item.opened_since.isoformat() if item.opened_since else None,
            "quantidade_esperada": item.expected or 0,
            "quantidade_recebida": item.received or 0,
            "falta_receber": (item.expected or 0) - (item.received or 0),
            "fifo_days": fifo_days,
            "status": status
        })

    return jsonify(resultado)
