"""生成流程端到端测试(渲染真实模板)。"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from pytemplate.context import MODE_COMPLEX, MODE_SIMPLE, ProjectConfigError, ProjectSpec
from pytemplate.generator import generate_project

LEFTOVER_PATTERN: re.Pattern[str] = re.compile(r"\{\{[A-Z][A-Z0-9_]*\}\}")


def _spec(mode: str, tmp_path: Path) -> ProjectSpec:
    return ProjectSpec(
        name="demo-app",
        mode=mode,
        frontend_dev_port=5173,
        backend_dev_http_port=5001,
        backend_dev_ws_port=5002,
        backend_release_http_port=8001,
        backend_release_ws_port=8002,
        output_dir=tmp_path / "demo-app",
    )


def _assert_no_leftover(output_dir: Path) -> None:
    """生成目录内不允许残留未填充占位符。"""
    for file_path in output_dir.rglob("*"):
        if file_path.is_file():
            text = file_path.read_text(encoding="utf-8")
            assert not LEFTOVER_PATTERN.findall(text), f"残留占位符: {file_path}"


def test_generate_simple_project(tmp_path: Path) -> None:
    """simple 模式:核心文件齐全,无 element-plus/SQLAlchemy 痕迹。"""
    spec = _spec(MODE_SIMPLE, tmp_path)
    written = generate_project(spec)

    rel_names = {path.relative_to(spec.output_dir).as_posix() for path in written}
    assert {".gitignore", "manage.py", "README.md"} <= rel_names
    assert "frontend/package.json" in rel_names
    assert "backend/app/ws.py" in rel_names
    assert "backend/static/.gitkeep" in rel_names
    # simple 模式不生成 complex 专属文件
    assert "backend/app/db.py" not in rel_names
    assert "backend/app/models.py" not in rel_names
    assert "backend/tests/test_models.py" not in rel_names

    package_json = (spec.output_dir / "frontend" / "package.json").read_text(encoding="utf-8")
    assert "element-plus" not in package_json
    assert '"vue": "^3.4.31"' in package_json
    assert "5173" in package_json

    requirements = (spec.output_dir / "backend" / "requirements.txt").read_text(encoding="utf-8")
    assert "SQLAlchemy" not in requirements
    assert "xuri-rpc-websocket" in requirements

    _assert_no_leftover(spec.output_dir)


def test_generate_complex_project(tmp_path: Path) -> None:
    """complex 模式:额外生成 db/models 及对应测试,并注入依赖。"""
    spec = _spec(MODE_COMPLEX, tmp_path)
    written = generate_project(spec)

    rel_names = {path.relative_to(spec.output_dir).as_posix() for path in written}
    assert "backend/app/db.py" in rel_names
    assert "backend/app/models.py" in rel_names
    assert "backend/tests/test_models.py" in rel_names

    package_json = (spec.output_dir / "frontend" / "package.json").read_text(encoding="utf-8")
    assert '"element-plus": "^2.7.8"' in package_json

    main_ts = (spec.output_dir / "frontend" / "src" / "main.ts").read_text(encoding="utf-8")
    assert "ElementPlus" in main_ts
    assert ".use(ElementPlus)" in main_ts

    requirements = (spec.output_dir / "backend" / "requirements.txt").read_text(encoding="utf-8")
    assert "SQLAlchemy>=2.0.30" in requirements

    ws_py = (spec.output_dir / "backend" / "app" / "ws.py").read_text(encoding="utf-8")
    assert "list_users" in ws_py

    _assert_no_leftover(spec.output_dir)


def test_generated_backend_config_has_modes(tmp_path: Path) -> None:
    """后端配置文件含 dev/release 两套独立配置与端口。"""
    spec = _spec(MODE_SIMPLE, tmp_path)
    generate_project(spec)
    dev_cfg = (spec.output_dir / "backend" / "config" / "dev.py").read_text(encoding="utf-8")
    release_cfg = (spec.output_dir / "backend" / "config" / "release.py").read_text(encoding="utf-8")
    assert "HTTP_PORT: Final[int] = 5001" in dev_cfg
    assert "WS_PORT: Final[int] = 5002" in dev_cfg
    assert "HTTP_PORT: Final[int] = 8001" in release_cfg
    assert "WS_PORT: Final[int] = 8002" in release_cfg


def test_generate_rejects_existing_output(tmp_path: Path) -> None:
    """输出目录已存在时拒绝覆盖。"""
    spec = _spec(MODE_SIMPLE, tmp_path)
    spec.output_dir.mkdir()
    with pytest.raises(ProjectConfigError):
        generate_project(spec)
