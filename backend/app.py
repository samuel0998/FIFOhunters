from flask import Flask
from dotenv import load_dotenv
import os

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# =========================
# EXTENSÕES (com SSL)
# =========================

db = SQLAlchemy(
    engine_options={
        "connect_args": {
            "sslmode": "require"
        }
    }
)

migrate = Migrate()

# =========================
# APP FACTORY
# =========================

def create_app():
    # 🔥 Carrega variáveis do .env ANTES DE TUDO
    load_dotenv()

    app = Flask(__name__)

    # =========================
    # CONFIGURAÇÕES
    # =========================
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

    # 🔎 DEBUG (pode remover depois)
    print("DATABASE_URL:", app.config["SQLALCHEMY_DATABASE_URI"])

    # =========================
    # INICIALIZA EXTENSÕES
    # =========================
    db.init_app(app)
    migrate.init_app(app, db)

    # =========================
    # IMPORTA MODELS (OBRIGATÓRIO)
    # =========================
    from models.fifo_item import FifoItem  # noqa: F401

    # =========================
    # ROTAS BÁSICAS
    # =========================
    @app.route("/")
    def health():
        return {"status": "FIFO HUNTERS API ONLINE"}

    return app
