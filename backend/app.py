import os
from flask import Flask, render_template
from dotenv import load_dotenv
from extensions import db, migrate


load_dotenv()


def create_app():
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev")

    db.init_app(app)
    migrate.init_app(app, db)

    from routes.upload import upload_bp
    app.register_blueprint(upload_bp, url_prefix="/api")

    from models.scan import scan_bp
    app.register_blueprint(scan_bp, url_prefix="/api")


    @app.route("/")
    def index():
        return render_template("upload.html")

    @app.route("/health")
    def health():
        return {"status": "FIFO HUNTERS API ONLINE"}

    return app
