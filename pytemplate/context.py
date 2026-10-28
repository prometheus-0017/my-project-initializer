"""项目参数上下文:校验输入参数并派生模板占位符映射。"""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Final

MODE_SIMPLE: Final[str] = "simple"
MODE_COMPLEX: Final[str] = "complex"
VALID_MODES: Final[tuple[str, ...]] = (MODE_SIMPLE, MODE_COMPLEX)

# 模式简写映射:支持单字符 s/c
_MODE_ALIASES: Final[dict[str, str]] = {
    "s": MODE_SIMPLE,
    "c": MODE_COMPLEX,
}

_PROJECT_NAME_PATTERN: Final[re.Pattern[str]] = re.compile(r"^[A-Za-z][A-Za-z0-9_-]*$")


class ProjectConfigError(ValueError):
    """项目参数非法。"""


def validate_project_name(name: str) -> None:
    """校验项目名称(同时用作生成目录名)。

    Raises:
        ProjectConfigError: 名称非法。
    """
    if not name:
        raise ProjectConfigError("项目名称不能为空")
    if not _PROJECT_NAME_PATTERN.match(name):
        raise ProjectConfigError("项目名称需以字母开头,且仅包含字母/数字/下划线/连字符")


def normalize_mode(mode: str) -> str:
    """将模式输入(含单字符 s/c)规范化为 simple 或 complex。"""
    normalized = mode.lower()
    return _MODE_ALIASES.get(normalized, normalized)


def validate_mode(mode: str) -> None:
    """校验项目模式。

    Raises:
        ProjectConfigError: 模式不在 simple/complex 之中。
    """
    if mode not in VALID_MODES:
        raise ProjectConfigError(f"非法模式: {mode!r}(仅支持 {list(VALID_MODES)})")


def validate_port(port: int) -> None:
    """校验端口数值范围。

    Raises:
        ProjectConfigError: 端口超出 1-65535。
    """
    if not 1 <= port <= 65535:
        raise ProjectConfigError(f"端口超出有效范围 1-65535: {port}")


def ensure_no_conflict(port: int, allocated: Iterable[int]) -> None:
    """确保端口未被其他服务占用(同一次生成内不允许重复)。

    Raises:
        ProjectConfigError: 端口重复。
    """
    if port in set(allocated):
        raise ProjectConfigError(f"端口重复分配: {port}")


@dataclass(frozen=True)
class ProjectSpec:
    """一次项目生成所需的全部参数(端口均为最终确定值)。"""

    name: str
    mode: str
    frontend_dev_port: int
    backend_dev_http_port: int
    backend_dev_ws_port: int
    backend_release_http_port: int
    backend_release_ws_port: int
    output_dir: Path

    def to_render_map(self) -> dict[str, str]:
        """派生模板渲染所需的全部占位符映射(含 simple/complex 条件片段)。"""
        mapping: dict[str, str] = {
            "{{PROJECT_NAME}}": self.name,
            "{{MODE}}": self.mode,
            "{{FRONTEND_DEV_PORT}}": str(self.frontend_dev_port),
            "{{BACKEND_DEV_HTTP_PORT}}": str(self.backend_dev_http_port),
            "{{BACKEND_DEV_WS_PORT}}": str(self.backend_dev_ws_port),
            "{{BACKEND_RELEASE_HTTP_PORT}}": str(self.backend_release_http_port),
            "{{BACKEND_RELEASE_WS_PORT}}": str(self.backend_release_ws_port),
        }
        if self.mode == MODE_COMPLEX:
            mapping.update(_COMPLEX_SNIPPETS)
        else:
            mapping.update(_SIMPLE_SNIPPETS)
        return mapping


# complex 模式才注入的代码/依赖片段;simple 模式下这些占位符一律替换为空串。
_COMPLEX_SNIPPETS: Final[Mapping[str, str]] = {
    # frontend/package.json:追加 element-plus 依赖
    "{{ELEMENT_PLUS_DEP}}": ',\n    "element-plus": "^2.7.8"',
    # frontend/src/main.ts:注册 element-plus
    "{{ELEMENT_IMPORTS}}": (
        "import ElementPlus from 'element-plus'\n"
        "import 'element-plus/dist/index.css'"
    ),
    "{{ELEMENT_USE}}": ".use(ElementPlus)",
    # frontend/vite.config.ts:external 构建时 element-plus 走 CDN
    "{{EXTERNAL_CDN_ENTRY}}": (
        "\n  'element-plus': "
        "'https://cdn.jsdelivr.net/npm/element-plus@2.7.8/dist/index.full.min.mjs',"
    ),
    "{{EXTERNAL_PACKAGES}}": '"vue", "element-plus"',
    # backend/requirements.txt:追加 SQLAlchemy
    "{{SQLALCHEMY_REQUIREMENT}}": "# 数据库\nSQLAlchemy>=2.0.30\n",
    # backend/app/ws.py:RPC 增加基于会话的查询示例
    "{{RPC_DB_IMPORTS}}": (
        "from sqlalchemy import select\n"
        "\n"
        "from .db import session_scope\n"
        "from .models import User"
    ),
    "{{RPC_DB_METHODS}}": (
        "\n"
        "\n"
        "    def list_users(self) -> list[dict[str, object]]:\n"
        "        \"\"\"查询全部用户:演示 SQLAlchemy 只读查询。\"\"\"\n"
        "        with session_scope() as session:\n"
        "            users = session.scalars(select(User)).all()\n"
        "            return [user.as_dict() for user in users]"
    ),
    # backend/app/__init__.py:应用创建时初始化数据库
    "{{DB_IMPORT}}": "from .db import init_db",
    "{{DB_INIT}}": "    init_db(config.database_url)",
    # backend/config:各环境数据库地址
    "{{DEV_DATABASE_URL}}": "sqlite:///data/dev.db",
    "{{RELEASE_DATABASE_URL}}": "sqlite:///data/app.db",
}

# simple 模式使用与 complex 相同的键集合,值为空串,保证键一致性。
_SIMPLE_SNIPPETS: Final[Mapping[str, str]] = dict.fromkeys(_COMPLEX_SNIPPETS, "")
