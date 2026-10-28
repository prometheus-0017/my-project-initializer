"""参数校验与占位符映射测试。"""

from __future__ import annotations

from pathlib import Path

import pytest

from pytemplate.context import (
    MODE_COMPLEX,
    MODE_SIMPLE,
    ProjectConfigError,
    ProjectSpec,
    ensure_no_conflict,
    normalize_mode,
    validate_mode,
    validate_port,
    validate_project_name,
)


def _spec(mode: str) -> ProjectSpec:
    return ProjectSpec(
        name="demo-app",
        mode=mode,
        frontend_dev_port=5173,
        backend_dev_http_port=5001,
        backend_dev_ws_port=5002,
        backend_release_http_port=8001,
        backend_release_ws_port=8002,
        output_dir=Path("demo-app"),
    )


@pytest.mark.parametrize(
    ("name", "valid"),
    [
        ("app", True),
        ("my_app-2", True),
        ("", False),
        ("1app", False),
        ("bad name", False),
        ("bad/name", False),
    ],
)
def test_validate_project_name(name: str, valid: bool) -> None:
    """项目名称合法性规则。"""
    if valid:
        validate_project_name(name)
    else:
        with pytest.raises(ProjectConfigError):
            validate_project_name(name)


def test_validate_mode() -> None:
    """模式支持 simple/complex 以及单字符 s/c。"""
    validate_mode(MODE_SIMPLE)
    validate_mode(MODE_COMPLEX)
    with pytest.raises(ProjectConfigError):
        validate_mode("pro")


def test_normalize_mode() -> None:
    """单字符 s/c 应规范化为 simple/complex。"""
    assert normalize_mode("s") == MODE_SIMPLE
    assert normalize_mode("c") == MODE_COMPLEX
    assert normalize_mode("S") == MODE_SIMPLE
    assert normalize_mode("C") == MODE_COMPLEX
    assert normalize_mode("simple") == MODE_SIMPLE
    assert normalize_mode("complex") == MODE_COMPLEX
    assert normalize_mode("unknown") == "unknown"


def test_validate_port() -> None:
    """端口范围校验。"""
    validate_port(1)
    validate_port(65535)
    with pytest.raises(ProjectConfigError):
        validate_port(0)
    with pytest.raises(ProjectConfigError):
        validate_port(65536)


def test_ensure_no_conflict() -> None:
    """同一次生成内端口不允许重复。"""
    ensure_no_conflict(8000, {9000})
    with pytest.raises(ProjectConfigError):
        ensure_no_conflict(8000, {8000})


def test_render_map_simple_has_empty_snippets() -> None:
    """simple 模式条件片段全部为空。"""
    mapping = _spec(MODE_SIMPLE).to_render_map()
    assert mapping["{{PROJECT_NAME}}"] == "demo-app"
    assert mapping["{{ELEMENT_USE}}"] == ""
    assert mapping["{{SQLALCHEMY_REQUIREMENT}}"] == ""


def test_render_map_complex_has_snippets() -> None:
    """complex 模式条件片段包含 element-plus 与 SQLAlchemy。"""
    mapping = _spec(MODE_COMPLEX).to_render_map()
    assert mapping["{{ELEMENT_USE}}"] == ".use(ElementPlus)"
    assert "SQLAlchemy" in mapping["{{SQLALCHEMY_REQUIREMENT}}"]
    assert "element-plus" in mapping["{{ELEMENT_PLUS_DEP}}"]


def test_render_map_modes_share_same_keys() -> None:
    """两种模式的占位符键集合一致,防止模板残留。"""
    assert set(_spec(MODE_SIMPLE).to_render_map()) == set(_spec(MODE_COMPLEX).to_render_map())
