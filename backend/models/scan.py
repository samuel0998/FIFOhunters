# routes/scan.py

from flask import Blueprint, request, jsonify
from datetime import date
from sqlalchemy import or_, func
from models.fifo_item import FIFOItem
from extensions import db

scan_bp = Blueprint("scan", __name__)


# 🔥 PADRONIZA DOMINGO COMO 0
CONE_MAP = {
    0: {"cor": "black", "nome": "Domingo"},
    1: {"cor": "blue", "nome": "Segunda"},
    2: {"cor": "yellow", "nome": "Terça"},
    3: {"cor": "green", "nome": "Quarta"},
    4: {"cor": "orange", "nome": "Quinta"},
    5: {"cor": "white", "nome": "Sexta"},
    6: {"cor": "pink", "nome": "Sábado"},
}


def calc_status(days):
    if days <= 3:
        return "OK"
    elif days <= 7:
        return "ATENCAO"
    return "CRITICO"


# ---------------- SCAN ---------------- #

@scan_bp.route("/scan", methods=["GET"])
def scan():

    code = request.args.get("code")
    status_filter = request.args.get("status")

    if not code and not status_filter:
        return jsonify({"error": "Código não informado"}), 400

    query = FIFOItem.query

    # 🔎 SCAN NORMAL
    if code:
        query = query.filter(
            or_(
                func.trim(FIFOItem.ean) == code,
                func.trim(FIFOItem.ean_taxable) == code,
                FIFOItem.asin == code,
                FIFOItem.isd == code
            )
        )

    itens = query.all()

    hoje = date.today()
    resultado = []

    for item in itens:

        fifo_days = 0
        cone = None

        if item.opened_since:
            fifo_days = (hoje - item.opened_since).days

            # 🔥 CONVERTE SEGUNDA=0 PARA DOMINGO=0
            weekday = (item.opened_since.weekday() + 1) % 7
            cone = CONE_MAP.get(weekday)

        status = calc_status(fifo_days)

        # 🔥 FILTRO POR STATUS
        if status_filter and status != status_filter:
            continue

        resultado.append({
            "produto": item.description,
            "isa": item.isa,
            "isd": item.isd,
            "data_abertura": item.opened_since.isoformat() if item.opened_since else None,
            "quantidade_esperada": item.expected or 0,
            "quantidade_recebida": item.received or 0,
            "falta_receber": (item.expected or 0) - (item.received or 0),
            "fifo_days": fifo_days,
            "status": status,
            "cone_cor": cone["cor"] if cone else None,
            "cone_nome": cone["nome"] if cone else None
        })

    return jsonify(resultado)


# ---------------- DASHBOARD ---------------- #

@scan_bp.route("/dashboard/full", methods=["GET"])
def dashboard_full():
    from sqlalchemy import func
    from collections import defaultdict

    hoje = date.today()

    # 🔥 AGRUPA POR ISA (1 VEZ CADA)
    isas = (
        db.session.query(
            FIFOItem.isa,
            func.min(FIFOItem.opened_since).label("opened_since")
        )
        .group_by(FIFOItem.isa)
        .all()
    )

    resumo = {
        "total_isa": 0,
        "total_asin": FIFOItem.query.count(),
        "OK": 0,
        "ATENCAO": 0,
        "CRITICO": 0,
        "cones": {
            "Domingo": {"total": 0, "cor": "black"},
            "Segunda": {"total": 0, "cor": "blue"},
            "Terça": {"total": 0, "cor": "yellow"},
            "Quarta": {"total": 0, "cor": "green"},
            "Quinta": {"total": 0, "cor": "orange"},
            "Sexta": {"total": 0, "cor": "white"},
            "Sábado": {"total": 0, "cor": "pink"},
        }
    }

    resumo["total_isa"] = len(isas)

    for isa, opened_since in isas:

        if not opened_since:
            continue

        dias = (hoje - opened_since).days
        status = calc_status(dias)

        resumo[status] += 1

        weekday = opened_since.weekday()
        cone = CONE_MAP.get(weekday)

        if cone:
            resumo["cones"][cone["nome"]]["total"] += 1

    return jsonify(resumo)

