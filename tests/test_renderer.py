"""渲染器测试。"""

from __future__ import annotations

import pytest

from pytemplate.renderer import TemplateRenderError, render_text


def test_render_text_replaces_all_placeholders() -> None:
    """全部占位符按映射替换。"""
    rendered = render_text(
        "name={{PROJECT_NAME}}, port={{BACKEND_DEV_HTTP_PORT}}",
        {"{{PROJECT_NAME}}": "demo", "{{BACKEND_DEV_HTTP_PORT}}": "5001"},
    )
    assert rendered == "name=demo, port=5001"


def test_render_text_rejects_leftover_placeholder() -> None:
    """存在未填充占位符时显式报错。"""
    with pytest.raises(TemplateRenderError):
        render_text("port={{UNKNOWN_VAR}}", {})


def test_render_text_keeps_lowercase_braces() -> None:
    """小写双花括号(Vue 插值)不视为占位符。"""
    text = "<p>{{ message }}</p>"
    assert render_text(text, {}) == text
