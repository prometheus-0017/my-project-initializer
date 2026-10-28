"""CLI 端到端测试(含交互输入模拟)。"""

from __future__ import annotations

from pathlib import Path

import pytest

import pytemplate.cli as cli
from pytemplate.context import ProjectConfigError


def test_cli_no_input_generates_simple(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """--no-input:仅项目名,其余按缺省行为(模式 simple、端口随机)。"""
    monkeypatch.chdir(tmp_path)
    code = cli.main(["--name", "webapp", "--no-input"])
    assert code == 0
    assert (tmp_path / "webapp" / ".gitignore").is_file()
    assert (tmp_path / "webapp" / "backend" / "pytest.ini").is_file()


def test_cli_explicit_ports(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """显式端口写入生成的配置文件。"""
    monkeypatch.chdir(tmp_path)
    code = cli.main(
        [
            "--name", "portapp",
            "--frontend-port", "5180",
            "--backend-dev-http-port", "5010",
            "--backend-dev-ws-port", "5011",
            "--backend-release-http-port", "8010",
            "--backend-release-ws-port", "8011",
            "--no-input",
        ]
    )
    assert code == 0
    vite_config = (tmp_path / "portapp" / "frontend" / "vite.config.ts").read_text(encoding="utf-8")
    assert "port: 5180" in vite_config
    dev_cfg = (tmp_path / "portapp" / "backend" / "config" / "dev.py").read_text(encoding="utf-8")
    assert "HTTP_PORT: Final[int] = 5010" in dev_cfg
    assert "WS_PORT: Final[int] = 5011" in dev_cfg


def test_cli_duplicate_ports_fail(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """显式端口重复时返回错误码 2,且不产生输出目录。"""
    monkeypatch.chdir(tmp_path)
    code = cli.main(
        [
            "--name", "dupapp",
            "--frontend-port", "5000",
            "--backend-dev-http-port", "5000",
            "--no-input",
        ]
    )
    assert code == 2
    assert not (tmp_path / "dupapp").exists()


def test_cli_interactive_generates_complex(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """交互输入:名称、模式;端口全部回车(随机)。"""
    inputs = iter(["wsapp", "complex", "", "", "", "", "", ""])
    monkeypatch.setattr("builtins.input", lambda _prompt="": next(inputs))
    monkeypatch.chdir(tmp_path)
    code = cli.main([])
    assert code == 0
    assert (tmp_path / "wsapp" / "backend" / "app" / "models.py").is_file()


def test_cli_interactive_invalid_name_retries(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """交互输入非法名称时重试,随后合法名称成功生成。"""
    # 2 次名称(1 次非法重试)+ 1 次模式 + 5 个端口(全部回车随机)
    inputs = iter(["bad name", "goodapp", "", "", "", "", "", ""])
    monkeypatch.setattr("builtins.input", lambda _prompt="": next(inputs))
    monkeypatch.chdir(tmp_path)
    assert cli.main([]) == 0
    assert (tmp_path / "goodapp" / "manage.py").is_file()


def test_cli_missing_name_without_input_raises(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """--no-input 且未提供名称:显式报错。"""
    monkeypatch.chdir(tmp_path)
    with pytest.raises(ProjectConfigError):
        cli.collect_spec(cli.build_parser().parse_args(["--no-input"]))
