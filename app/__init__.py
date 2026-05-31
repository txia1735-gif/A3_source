from datetime import datetime
from pathlib import Path

from flask import Flask, jsonify, request

from logger_config import setup_logging

from .blueprints import register_blueprints
from .config import Config
from .extensions import db, init_extensions


def create_app(config_class=Config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.json.ensure_ascii = False

    Path(app.config["UPLOAD_FOLDER"]).mkdir(parents=True, exist_ok=True)
    Path(app.config["GENERATED_FOLDER"]).mkdir(parents=True, exist_ok=True)
    Path(app.config["LOG_DIR"]).mkdir(parents=True, exist_ok=True)

    setup_logging(app)
    init_extensions(app)
    register_blueprints(app)

    @app.context_processor
    def inject_global_values():
        return {"current_year": datetime.now().year}

    @app.before_request
    def log_request():
        app.logger.info(
            "Request started: %s %s from %s",
            request.method,
            request.path,
            request.remote_addr,
        )

    @app.after_request
    def log_response(response):
        app.logger.info(
            "Request completed: %s %s -> %s",
            request.method,
            request.path,
            response.status_code,
        )
        return response

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"success": False, "message": "请求资源不存在"}), 404

    @app.errorhandler(500)
    def server_error(error):
        app.logger.exception("Unhandled server error: %s", error)
        return jsonify({"success": False, "message": "服务器内部错误"}), 500

    @app.get("/health")
    def health_check():
        return jsonify({"success": True, "message": "ok"})

    with app.app_context():
        if app.config.get("AUTO_CREATE_TABLES", True):
            db.create_all()

    return app
