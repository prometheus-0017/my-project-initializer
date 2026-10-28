"""配置加载入口:按运行模式加载对应的独立配置文件。"""

from types import ModuleType

from . import dev, release


class ConfigError(ValueError):
    """配置加载失败。"""


_MODULES: dict[str, ModuleType] = {
    "dev": dev,
    "release": release,
}


def load_config(mode: str) -> ModuleType:
    """按运行模式加载配置。

    Raises:
        ConfigError: mode 不是 dev / release。
    """
    try:
        return _MODULES[mode]
    except KeyError as exc:
        raise ConfigError(f"未知运行模式: {mode!r}(仅支持: {sorted(_MODULES)})") from exc
