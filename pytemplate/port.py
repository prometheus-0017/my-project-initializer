"""端口分配工具。

随机端口逻辑集中在本模块的独立函数中,便于后续扩展(例如:指定候选网段、
排除保留端口、按业务复用偏好挑选等),调用方不应感知具体实现。
"""

from __future__ import annotations

import random
import socket
from typing import Final, Iterable

MIN_DYNAMIC_PORT: Final[int] = 1024
MAX_DYNAMIC_PORT: Final[int] = 65535


class PortAllocationError(RuntimeError):
    """端口分配失败(范围内无可用端口)。"""


def _probe_bindable(host: str, port: int) -> bool:
    """探测端口当前是否可绑定(可绑定即视为空闲)。"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        # Windows 默认允许重复绑定同一端口,必须显式独占才能可靠探测。
        exclusive = getattr(socket, "SO_EXCLUSIVEADDRUSE", None)
        if exclusive is not None:
            sock.setsockopt(socket.SOL_SOCKET, exclusive, 1)
        try:
            sock.bind((host, port))
        except OSError:
            return False
    return True


def pick_free_port(
    *,
    lower: int = MIN_DYNAMIC_PORT,
    upper: int = MAX_DYNAMIC_PORT,
    exclude: Iterable[int] = frozenset(),
    host: str = "127.0.0.1",
) -> int:
    """从 [lower, upper] 中随机挑选一个当前未被占用、且不在排除名单内的端口。

    本函数是端口随机策略的唯一入口,保持独立以便扩展。

    Args:
        lower: 端口下界(含)。
        upper: 端口上界(含)。
        exclude: 需要避开的端口集合(例如已分配给其他服务的端口)。
        host: 探测绑定的本机地址。

    Returns:
        可用的随机端口号。

    Raises:
        PortAllocationError: 范围内(排除后)没有任何可绑定端口。
        ValueError: 端口范围参数非法。
    """
    if not 1 <= lower <= upper <= MAX_DYNAMIC_PORT:
        raise ValueError(f"非法端口范围: [{lower}, {upper}]")

    candidates = [port for port in range(lower, upper + 1) if port not in set(exclude)]
    if not candidates:
        raise PortAllocationError(f"[{lower}, {upper}] 范围内无候选端口(排除后为空)")

    random.shuffle(candidates)
    for port in candidates:
        if _probe_bindable(host, port):
            return port
    raise PortAllocationError(f"[{lower}, {upper}] 范围内没有当前可绑定的端口")
