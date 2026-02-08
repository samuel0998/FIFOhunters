# routes/scan.py
from flask import Blueprint, request, jsonify
from models.fifo_item import FIFOItem
from datetime import date

scan_bp = Blueprint("scan", __name__)


@scan_bp.route("/scan", methods=["GET"])
def scan():
    q = request.args.get("q")

    if not q:
        return jsonify({"error": "Valor de scan não informado"}), 400

    hoje = date.today()

    # 🔵 TENTA COMO ISD PRIMEIRO
    itens = FIFOItem.query.filter(FIFOItem.isd == q).all()
    tipo_scan = "ISD"

    # 🟢 SE NÃO FOR ISD, TENTA EAN / ASIN
    if not itens:
        itens = FIFOItem.query.filter(
            (FIFOItem.ean == q) | (FIFOItem.asin == q)
        ).order_by(FIFOItem.opened_since.asc()).all()
        tipo_scan = "PRODUTO"

    if not itens:
        return jsonify({"error": "Nenhum registro encontrado"}), 404

    resposta = []

    for item in itens:
        # FIFO DAYS
        fifo_days = (
            (hoje - item.opened_since).days
            if item.opened_since
            else None
        )

        # DIFERENÇA
        falta = (
            item.expected - item.received
            if item.expected is not None and item.received is not None
            else None
        )

        # STATUS
        if fifo_days is None:
            status = "SEM DATA"
        elif fifo_days <= 7:
            status = "OK"
        elif fifo_days <= 14:
            status = "ATENÇÃO"
        else:
            status = "CRÍTICO"

        resposta.append({
            "tipo_scan": tipo_scan,

            "descricao": item.description,
            "isd": item.isd,

            "ean": item.ean,
            "asin": item.asin,

            "nfe_id": item.nfe_id,
            "opened_since": item.opened_since.isoformat() if item.opened_since else None,

            "expected": item.expected,
            "received": item.received,
            "falta_receber": falta,

            "fifo_days": fifo_days,
            "status": status
        })

    return jsonify(resposta), 200
