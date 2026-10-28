"""模板渲染:占位符替换与残留校验。

渲染采用纯字符串替换,不引入模板引擎依赖;渲染完成后校验不允许残留
任何未填充的占位符,避免把半成品写进生成的项目。
"""

from __future__ import annotations

import re
from typing import Final, Mapping

PLACEHOLDER_PATTERN: Final[re.Pattern[str]] = re.compile(r"\{\{[A-Z][A-Z0-9_]*\}\}")


class TemplateRenderError(RuntimeError):
    """模板渲染失败(存在未填充的占位符)。"""


def render_text(text: str, mapping: Mapping[str, str]) -> str:
    """将模板文本中的占位符逐一替换为映射值。

    Args:
        text: 模板原始文本。
        mapping: 占位符(形如 {{NAME}})到替换值的映射。

    Returns:
        渲染后的完整文本。

    Raises:
        TemplateRenderError: 渲染后仍残留未填充的占位符。
    """
    rendered = text
    for key, value in mapping.items():
        rendered = rendered.replace(key, value)

    leftover = sorted(set(PLACEHOLDER_PATTERN.findall(rendered)))
    if leftover:
        raise TemplateRenderError(f"模板渲染后仍存在未填充的占位符: {leftover}")
    return rendered
