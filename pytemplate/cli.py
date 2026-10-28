"""命令行入口:参数解析、交互式补齐并调用生成器。"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Final

from pytemplate.context import (
    MODE_SIMPLE,
    ProjectConfigError,
    ProjectSpec,
    ensure_no_conflict,
    normalize_mode,
    validate_mode,
    validate_port,
    validate_project_name,
)
from pytemplate.generator import generate_project
from pytemplate.port import pick_free_port
from pytemplate.renderer import TemplateRenderError

_PORT_LABELS: Final[tuple[str, ...]] = (
    "前端开发端口",
    "后端开发 HTTP 端口",
    "后端开发 WS 端口",
    "后端部署 HTTP 端口",
    "后端部署 WS 端口",
)


def build_parser() -> argparse.ArgumentParser:
    """构建命令行参数解析器。"""
    parser = argparse.ArgumentParser(
        prog="pytemplate",
        description="前后端项目初始化模板生成器(支持 simple / complex 模式)",
    )
    parser.add_argument("-n", "--name", help="项目名称(同时作为生成目录名)")
    parser.add_argument("-m", "--mode", choices=("simple", "complex", "s", "c"), help="项目模式(支持 simple/complex 或 s/c)")
    parser.add_argument("--frontend-port", type=int, help="前端开发端口号(缺省随机)")
    parser.add_argument("--backend-dev-http-port", type=int, help="后端开发 HTTP 端口(缺省随机)")
    parser.add_argument("--backend-dev-ws-port", type=int, help="后端开发 WS 端口(缺省随机)")
    parser.add_argument("--backend-release-http-port", type=int, help="后端部署 HTTP 端口(缺省随机)")
    parser.add_argument("--backend-release-ws-port", type=int, help="后端部署 WS 端口(缺省随机)")
    parser.add_argument("-o", "--output", help="输出目录(缺省为当前目录/<项目名>)")
    parser.add_argument(
        "--no-input",
        action="store_true",
        help="禁用交互式输入:缺失参数按默认值/随机处理",
    )
    return parser


def _read_line(prompt: str) -> str:
    """读取一行交互输入,输入流中断时明确报错(禁止静默)。"""
    try:
        return input(prompt).strip()
    except EOFError as exc:
        raise ProjectConfigError("交互输入被中断(EOF)") from exc
    except KeyboardInterrupt as exc:
        raise ProjectConfigError("交互输入被用户中断") from exc


def _ask_project_name() -> str:
    """交互获取合法的项目名称,非法输入时循环重试。"""
    while True:
        value = _read_line("项目名称: ")
        try:
            validate_project_name(value)
        except ProjectConfigError as exc:
            print(f"  无效: {exc}")
            continue
        return value


def _ask_mode() -> str:
    """交互获取项目模式,回车默认 simple。"""
    while True:
        value = _read_line("模式 [simple/complex/s/c] (回车默认 simple): ").lower()
        if not value:
            return MODE_SIMPLE
        normalized = normalize_mode(value)
        try:
            validate_mode(normalized)
        except ProjectConfigError as exc:
            print(f"  无效: {exc}")
            continue
        return normalized


def _ask_optional_port(label: str, allocated: set[int]) -> int:
    """交互获取单个端口;留空则调用随机函数分配并避开已分配端口。"""
    while True:
        raw = _read_line(f"{label} (回车随机): ")
        if raw:
            try:
                port = int(raw)
                validate_port(port)
            except (ValueError, ProjectConfigError) as exc:
                print(f"  无效: {exc}")
                continue
        else:
            port = pick_free_port(exclude=frozenset(allocated))
        try:
            ensure_no_conflict(port, allocated)
        except ProjectConfigError as exc:
            print(f"  无效: {exc}")
            continue
        return port


def _resolve_ports(args: argparse.Namespace, interactive: bool) -> tuple[int, int, int, int, int]:
    """依次解析 5 个端口:显式参数优先,其次交互输入,最后随机分配。"""
    explicit: tuple[int | None, ...] = (
        args.frontend_port,
        args.backend_dev_http_port,
        args.backend_dev_ws_port,
        args.backend_release_http_port,
        args.backend_release_ws_port,
    )
    allocated: set[int] = set()
    resolved: list[int] = []
    for value, label in zip(explicit, _PORT_LABELS):
        if value is not None:
            validate_port(value)
            ensure_no_conflict(value, allocated)
        elif interactive:
            value = _ask_optional_port(label, allocated)
        else:
            value = pick_free_port(exclude=frozenset(allocated))
        allocated.add(value)
        resolved.append(value)
    return (
        resolved[0],
        resolved[1],
        resolved[2],
        resolved[3],
        resolved[4],
    )


def collect_spec(args: argparse.Namespace) -> ProjectSpec:
    """把命令行参数与交互输入整合为 ProjectSpec。"""
    interactive = not args.no_input
    if interactive:
        print("提示:缺失的参数将进入交互输入;端口直接回车即随机分配。")

    name = args.name or (_ask_project_name() if interactive else "")
    if not name:
        raise ProjectConfigError("缺少项目名称:请使用 --name 或允许交互输入")
    validate_project_name(name)

    mode = normalize_mode(args.mode or (_ask_mode() if interactive else MODE_SIMPLE))
    validate_mode(mode)

    ports = _resolve_ports(args, interactive)
    output_dir = Path(args.output) if args.output else Path.cwd() / name

    return ProjectSpec(
        name=name,
        mode=mode,
        frontend_dev_port=ports[0],
        backend_dev_http_port=ports[1],
        backend_dev_ws_port=ports[2],
        backend_release_http_port=ports[3],
        backend_release_ws_port=ports[4],
        output_dir=output_dir,
    )


def _print_summary(spec: ProjectSpec) -> None:
    """打印生成结果摘要与后续步骤。"""
    print()
    print("项目生成完成")
    print(f"  位置: {spec.output_dir}")
    print(f"  模式: {spec.mode}")
    print(f"  前端开发端口: {spec.frontend_dev_port}")
    print(f"  后端开发端口: http={spec.backend_dev_http_port} ws={spec.backend_dev_ws_port}")
    print(f"  后端部署端口: http={spec.backend_release_http_port} ws={spec.backend_release_ws_port}")
    print("后续步骤:")
    print(f"  cd {spec.output_dir}")
    print("  前端依赖: cd frontend && pnpm install")
    print("  后端依赖: cd backend && pip install -r requirements.txt")
    print("  一键开发启动: python manage.py dev")


def main(argv: Sequence[str] | None = None) -> int:
    """CLI 主入口,返回进程退出码。"""
    args = build_parser().parse_args(argv)
    try:
        spec = collect_spec(args)
        generate_project(spec)
    except (ProjectConfigError, TemplateRenderError) as exc:
        print(f"[错误] {exc}", file=sys.stderr)
        return 2
    _print_summary(spec)
    return 0
