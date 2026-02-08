import os
from flask import Flask, render_template, redirect
from dotenv import load_dotenv

from extensions import db, migrate
from models.fifo_item import FIFOItem

load_dotenv()


def create_app():
    app = Flask(__name__)

    # CONFIG
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev")

    # EXTENSIONS
    db.init_app(app)
    migrate.init_app(app, db)

    # BLUEPRINTS
    from routes.upload import upload_bp
    from models.scan import scan_bp

    app.register_blueprint(upload_bp, url_prefix="/api")
    app.register_blueprint(scan_bp, url_prefix="/api")

    # ==========================
    # ROTAS DE FRONT
    # ==========================

    @app.route("/")
    def home():
        # 🔑 REGRA PRINCIPAL DO SISTEMA
        existe_dado = db.session.query(FIFOItem.id).first()

        if existe_dado:
            return redirect("/scan")
        else:
            return redirect("/upload")

    @app.route("/upload")
    def upload_page():
        return render_template("upload.html")

    @app.route("/scan")
    def scan_page():
        return render_template("scan.html")

    # ==========================
    # HEALTH
    # ==========================

    @app.route("/health")
    def health():
        return {"status": "FIFO HUNTERS API ONLINE"}

    return app
