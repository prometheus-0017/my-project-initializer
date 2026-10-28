"""pick_free_port 单元测试。"""

from __future__ import annotations

import socket

import pytest

from pytemplate.port import MAX_DYNAMIC_PORT, PortAllocationError, pick_free_port


def test_pick_free_port_returns_bindable_port() -> None:
    """返回的端口当前可绑定。"""
    port = pick_free_port()
    assert 1024 <= port <= MAX_DYNAMIC_PORT
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", port))


def test_pick_free_port_avoids_excluded() -> None:
    """不会返回被排除的端口。"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        occupied = sock.getsockname()[1]
    for _ in range(20):
        port = pick_free_port(exclude={occupied})
        assert port != occupied


def test_pick_free_port_range() -> None:
    """返回值落在指定范围内。"""
    port = pick_free_port(lower=20000, upper=20050)
    assert 20000 <= port <= 20050


def test_pick_free_port_exhausted_raises() -> None:
    """排除所有候选端口时显式报错。"""
    with pytest.raises(PortAllocationError):
        pick_free_port(lower=30000, upper=30000, exclude={30000})


def test_pick_free_port_invalid_range_raises() -> None:
    """非法范围显式报错。"""
    with pytest.raises(ValueError):
        pick_free_port(lower=50000, upper=1024)
