# extensions.py
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy(
    engine_options={
        "connect_args": {"sslmode": "require"}
    }
)

migrate = Migrate()
