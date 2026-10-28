"""配置加载入口:按运行模式加载对应的独立配置文件。"""

from __future__ import annotations

from collections.abc import Callable
from typing import Final

from . import dev, release
from .base import AppConfig


class ConfigError(ValueError):
    """配置加载失败。"""


_BUILDERS: Final[dict[str, Callable[[], AppConfig]]] = {
    "dev": dev.build_config,
    "release": release.build_config,
}


def load_config(mode: str) -> AppConfig:
    """按运行模式加载配置。

    Raises:
        ConfigError: mode 不是 dev / release。
    """
    try:
        builder = _BUILDERS[mode]
    except KeyError as exc:
        raise ConfigError(f"未知运行模式: {mode!r}(仅支持: {sorted(_BUILDERS)})") from exc
    return builder()
