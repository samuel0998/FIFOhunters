from flask import Flask, render_template
import os

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from routes.upload import upload_bp

db = SQLAlchemy(
    engine_options={
        "connect_args": {"sslmode": "require"}
    }
)
migrate = Migrate()


def create_app():
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

    db.init_app(app)
    migrate.init_app(app, db)

    app.register_blueprint(upload_bp, url_prefix="/api")

    # 👉 FRONT
    @app.route("/")
    def home():
        return render_template("upload.html")

    # 👉 HEALTH CHECK
    @app.route("/health")
    def health():
        return {"status": "FIFO HUNTERS API ONLINE"}

    return app
