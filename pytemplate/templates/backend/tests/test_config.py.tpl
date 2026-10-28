"""配置加载测试。"""

from __future__ import annotations

import pytest

from config import ConfigError, load_config


def test_load_dev_config() -> None:
    """dev 配置:debug 开启。"""
    cfg = load_config("dev")
    assert cfg.mode == "dev"
    assert cfg.debug is True
    assert cfg.http_port > 0
    assert cfg.ws_port > 0


def test_load_release_config() -> None:
    """release 配置:debug 关闭。"""
    cfg = load_config("release")
    assert cfg.mode == "release"
    assert cfg.debug is False


def test_load_unknown_mode_raises() -> None:
    """未知模式必须显式报错。"""
    with pytest.raises(ConfigError):
        load_config("unknown")
