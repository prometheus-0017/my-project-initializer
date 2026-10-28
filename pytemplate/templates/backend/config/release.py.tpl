"""部署环境配置文件(release 模式)。"""

from __future__ import annotations

from typing import Final

from .base import APP_NAME, AppConfig

HTTP_HOST: Final[str] = "0.0.0.0"
HTTP_PORT: Final[int] = {{BACKEND_RELEASE_HTTP_PORT}}
WS_HOST: Final[str] = "0.0.0.0"
WS_PORT: Final[int] = {{BACKEND_RELEASE_WS_PORT}}
DEBUG: Final[bool] = False
DATABASE_URL: Final[str] = "{{RELEASE_DATABASE_URL}}"


def build_config() -> AppConfig:
    """构建部署环境配置对象。"""
    return AppConfig(
        app_name=APP_NAME,
        mode="release",
        debug=DEBUG,
        http_host=HTTP_HOST,
        http_port=HTTP_PORT,
        ws_host=WS_HOST,
        ws_port=WS_PORT,
        database_url=DATABASE_URL,
    )
