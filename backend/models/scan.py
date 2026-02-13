from flask import Blueprint, request, jsonify
from datetime import date
from models.fifo_item import FIFOItem
from extensions import db
from sqlalchemy import or_, func

scan_bp = Blueprint("scan", __name__)

CONE_MAP = {
    6: {"cor": "black", "nome": "Domingo"},
    0: {"cor": "blue", "nome": "Segunda"},
    1: {"cor": "yellow", "nome": "Terça"},
    2: {"cor": "green", "nome": "Quarta"},
    3: {"cor": "orange", "nome": "Quinta"},
    4: {"cor": "white", "nome": "Sexta"},
    5: {"cor": "pink", "nome": "Sábado"},
}

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

        fifo_days = 0
        cone = None

        if item.opened_since:
            fifo_days = (hoje - item.opened_since).days
            weekday = item.opened_since.weekday()
            cone = CONE_MAP.get(weekday)

        status = calc_status(fifo_days)

        resultado.append({
            "produto": item.description,
            "nfe": item.nfe_id,
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


@scan_bp.route("/dashboard/status", methods=["GET"])
def dashboard_status():
    from sqlalchemy import func

    hoje = date.today()

    itens = FIFOItem.query.all()

    resumo = {"OK": 0, "ATENCAO": 0, "CRITICO": 0}

    for item in itens:
        if item.opened_since:
            dias = (hoje - item.opened_since).days
        else:
            dias = 0

        status = calc_status(dias)
        resumo[status] += 1

    return jsonify(resumo)


@scan_bp.route("/dashboard/full", methods=["GET"])
def dashboard_full():
    from sqlalchemy import func
    hoje = date.today()

    itens = FIFOItem.query.all()

    resumo = {
        "OK": 0,
        "ATENCAO": 0,
        "CRITICO": 0,
        "cones": {
            "Domingo": 0,
            "Segunda": 0,
            "Terça": 0,
            "Quarta": 0,
            "Quinta": 0,
            "Sexta": 0,
            "Sábado": 0,
        }
    }

    for item in itens:
        if item.opened_since:
            dias = (hoje - item.opened_since).days
            weekday = item.opened_since.weekday()
            cone = CONE_MAP.get(weekday)
        else:
            dias = 0
            cone = None

        status = calc_status(dias)
        resumo[status] += 1

        if cone:
            resumo["cones"][cone["nome"]] += 1

    return jsonify(resumo)
