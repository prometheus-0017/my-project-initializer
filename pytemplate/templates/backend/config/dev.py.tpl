"""开发环境配置文件(dev 模式)。"""

from __future__ import annotations

from typing import Final

from .base import APP_NAME, AppConfig

HTTP_HOST: Final[str] = "127.0.0.1"
HTTP_PORT: Final[int] = {{BACKEND_DEV_HTTP_PORT}}
WS_HOST: Final[str] = "127.0.0.1"
WS_PORT: Final[int] = {{BACKEND_DEV_WS_PORT}}
DEBUG: Final[bool] = True
DATABASE_URL: Final[str] = "{{DEV_DATABASE_URL}}"


def build_config() -> AppConfig:
    """构建开发环境配置对象。"""
    return AppConfig(
        app_name=APP_NAME,
        mode="dev",
        debug=DEBUG,
        http_host=HTTP_HOST,
        http_port=HTTP_PORT,
        ws_host=WS_HOST,
        ws_port=WS_PORT,
        database_url=DATABASE_URL,
    )
