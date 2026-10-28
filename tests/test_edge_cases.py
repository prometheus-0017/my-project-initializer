"""异常路径补充测试:交互中断、非法输入重试、端口探测失败。"""

from __future__ import annotations

import socket
from pathlib import Path

import pytest

import pytemplate.cli as cli
from pytemplate.context import ProjectConfigError
from pytemplate.port import PortAllocationError, pick_free_port


def test_cli_eof_interrupts_interaction(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """交互输入流中断(EOF)时显式报错,不静默。"""

    def _raise_eof(_prompt: str = "") -> str:
        raise EOFError

    monkeypatch.setattr("builtins.input", _raise_eof)
    monkeypatch.chdir(tmp_path)
    with pytest.raises(ProjectConfigError, match="中断"):
        cli.collect_spec(cli.build_parser().parse_args([]))


def test_cli_invalid_mode_and_port_retries(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """非法模式与非法端口输入会被拒绝并要求重试,最终成功生成。"""
    # 名称 + 模式(1 次非法重试)+ 5 个端口(第 1 个非法重试)
    inputs = iter(["retryapp", "pro", "complex", "abc", "", "", "", "", ""])
    monkeypatch.setattr("builtins.input", lambda _prompt="": next(inputs))
    monkeypatch.chdir(tmp_path)
    assert cli.main([]) == 0
    assert (tmp_path / "retryapp" / "manage.py").is_file()


def test_pick_free_port_reports_occupied_range() -> None:
    """范围内端口全部被占用时显式报错(而不是返回不可用端口)。"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        occupied = sock.getsockname()[1]
        # 调用必须位于 with 块内,保证探测期间端口仍被占用。
        with pytest.raises(PortAllocationError):
            pick_free_port(lower=occupied, upper=occupied)
