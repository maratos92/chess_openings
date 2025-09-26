"""Flask application factory for the chesslab backend."""
from __future__ import annotations

import os
from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO

from .api import api_bp
from .db import db_session, init_engine, Base
from .socketio_server import socketio


def create_app(test_config: dict | None = None) -> Flask:
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config.setdefault("SQLALCHEMY_DATABASE_URI", os.getenv("DATABASE_URL", "sqlite:///chesslab.db"))
    app.config.setdefault("REDIS_URL", os.getenv("REDIS_URL", "redis://localhost:6379/0"))
    app.config.setdefault("ENGINE_MAX_DEPTH", int(os.getenv("ENGINE_MAX_DEPTH", "20")))
    app.config.setdefault("ENGINE_MULTIPV", int(os.getenv("ENGINE_MULTIPV", "3")))

    if test_config:
        app.config.update(test_config)

    init_engine(app.config["SQLALCHEMY_DATABASE_URI"])

    CORS(app, resources={r"/api/*": {"origins": "http://localhost:5173"}})

    app.register_blueprint(api_bp, url_prefix="/api")

    @app.teardown_appcontext
    def shutdown_session(exception: Exception | None = None) -> None:  # pragma: no cover
        if exception:
            db_session.rollback()
        db_session.remove()

    socketio.init_app(app, cors_allowed_origins="http://localhost:5173")

    @app.route("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


__all__ = ["create_app", "socketio", "Base"]
