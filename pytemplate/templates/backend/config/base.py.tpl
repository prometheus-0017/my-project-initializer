"""配置数据结构与公共常量。"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

APP_NAME: Final[str] = "{{PROJECT_NAME}}"


@dataclass(frozen=True)
class AppConfig:
    """应用配置对象(由 dev/release 配置文件构建)。"""

    app_name: str
    mode: str
    debug: bool
    http_host: str
    http_port: int
    ws_host: str
    ws_port: int
    # complex 模式使用;simple 模式为空字符串。
    database_url: str
