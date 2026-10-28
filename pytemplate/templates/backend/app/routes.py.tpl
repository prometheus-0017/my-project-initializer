"""HTTP API 路由。"""

from __future__ import annotations

from typing import Any

from flask import Blueprint, current_app, jsonify

api_bp = Blueprint("api", __name__)


@api_bp.get("/health")
def health() -> Any:
    """健康检查接口。"""
    config = current_app.config["APP_CONFIG"]
    return jsonify({"status": "ok", "app": config.app_name, "mode": config.mode})
