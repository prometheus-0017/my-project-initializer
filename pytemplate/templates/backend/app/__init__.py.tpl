"""Flask 应用工厂。"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Final

from types import ModuleType

from flask import Flask, jsonify, send_from_directory

from .routes import api_bp
{{DB_IMPORT}}

_STATIC_DIR: Final[Path] = Path(__file__).resolve().parent.parent / "static"


def create_app(config: ModuleType) -> Flask:
    """创建并装配 Flask 应用实例。"""
    app = Flask(
        __name__,
        static_folder=str(_STATIC_DIR),
        static_url_path="/static",
    )
    app.config["APP_CONFIG"] = config
{{DB_INIT}}
    app.register_blueprint(api_bp, url_prefix="/api")

    @app.route("/")
    @app.route("/<path:spa_path>")
    def spa(spa_path: str = "") -> Any:
        """SPA 兜底路由:非 /api 请求统一返回前端产物 index.html。"""
        del spa_path
        index_file = _STATIC_DIR / "index.html"
        if not index_file.is_file():
            return jsonify(
                {"error": "前端产物未构建,请先在项目根目录执行: python manage.py build-copy"}
            ), 503
        return send_from_directory(_STATIC_DIR, "index.html")

    return app
