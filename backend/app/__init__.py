from __future__ import annotations

import logging

from flask import Flask

from .config import Config
from .db import close_db, init_db, seed_default_user
from .routes import auth_bp


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

    logging.basicConfig(
        level=getattr(logging, app.config["LOG_LEVEL"].upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    app.logger.setLevel(getattr(logging, app.config["LOG_LEVEL"].upper(), logging.INFO))

    app.teardown_appcontext(close_db)
    app.register_blueprint(auth_bp)

    with app.app_context():
        try:
            init_db()
            seed_default_user("Agenda@123")
        except Exception:
            app.logger.exception("Falha ao preparar o banco inicial.")

    return app