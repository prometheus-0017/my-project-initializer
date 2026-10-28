"""项目生成流程:遍历模板树,按模式筛选文件并渲染到目标目录。"""

from __future__ import annotations

from pathlib import Path
from typing import Final, Mapping

from pytemplate.context import MODE_COMPLEX, ProjectConfigError, ProjectSpec
from pytemplate.renderer import render_text

DEFAULT_TEMPLATES_ROOT: Final[Path] = Path(__file__).resolve().parent / "templates"

# 仅 complex 模式才会生成的文件(相对 templates 根目录,含 .tpl 后缀)。
COMPLEX_ONLY_FILES: Final[frozenset[Path]] = frozenset(
    {
        Path("backend/app/db.py.tpl"),
        Path("backend/app/models.py.tpl"),
        Path("backend/tests/test_models.py.tpl"),
    }
)

# 模板文件名到目标文件名的特殊映射(用于以点开头的目标文件)。
NAME_MAP: Final[Mapping[str, str]] = {
    "gitignore": ".gitignore",
}


def _resolve_dest_name(rel_path: Path) -> Path:
    """把模板相对路径转换为生成目标的相对路径(去掉 .tpl 后缀并应用名称映射)。"""
    dest_rel = rel_path.with_suffix("")
    dest_rel = dest_rel.with_name(NAME_MAP.get(dest_rel.name, dest_rel.name))
    return dest_rel


def generate_project(
    spec: ProjectSpec,
    templates_root: Path | None = None,
) -> list[Path]:
    """按参数渲染全部模板到输出目录,返回写入的文件路径列表。

    Args:
        spec: 项目生成参数(名称/模式/端口/输出目录)。
        templates_root: 模板根目录;缺省使用包内置 templates 目录。

    Returns:
        写入的文件路径列表(相对输出目录之外为绝对路径)。

    Raises:
        ProjectConfigError: 输出目录已存在,拒绝覆盖。
        TemplateRenderError: 任一模板存在未填充的占位符。
    """
    root = templates_root if templates_root is not None else DEFAULT_TEMPLATES_ROOT
    output_dir = spec.output_dir
    if output_dir.exists():
        raise ProjectConfigError(f"目标目录已存在,拒绝覆盖: {output_dir}")

    mapping = spec.to_render_map()
    written: list[Path] = []
    for template_file in sorted(root.rglob("*.tpl")):
        rel_path = template_file.relative_to(root)
        if spec.mode != MODE_COMPLEX and rel_path in COMPLEX_ONLY_FILES:
            continue

        dest = output_dir / _resolve_dest_name(rel_path)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(
            render_text(template_file.read_text(encoding="utf-8"), mapping),
            encoding="utf-8",
        )
        written.append(dest)

    # backend/static 为构建产物复制目标,写入空占位文件保证目录随项目存在。
    static_dir = output_dir / "backend" / "static"
    static_dir.mkdir(parents=True, exist_ok=True)
    keep_file = static_dir / ".gitkeep"
    keep_file.write_text("", encoding="utf-8")
    written.append(keep_file)

    return written
