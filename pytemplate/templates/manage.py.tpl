#!/usr/bin/env python3
"""统一命令入口。

用法: python manage.py <command>

命令:
    dev            并发启动前端( vite )与后端 dev( flask + ws rpc )
    build          编译前端(完整打包 vue / element-plus)
    build-copy     编译前端并把产物复制到 backend/static
    coverage       运行后端 pytest 覆盖率测试
    release        后端以 release 模式启动( waitress + ws rpc )
    build-external 无打包编译( vue / element-plus 走外部引用,不参与打包 )
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import time
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import Final

ROOT: Final[Path] = Path(__file__).resolve().parent
FRONTEND_DIR: Final[Path] = ROOT / "frontend"
BACKEND_DIR: Final[Path] = ROOT / "backend"
DIST_DIR: Final[Path] = FRONTEND_DIR / "dist"
STATIC_DIR: Final[Path] = BACKEND_DIR / "static"


class CommandError(RuntimeError):
    """命令执行失败。"""


def _ensure_pnpm() -> None:
    """确认 pnpm 可用,缺失时明确报错。"""
    if shutil.which("pnpm") is None:
        raise CommandError("未找到 pnpm 命令,请先安装: https://pnpm.io/installation")


def _run(command: Sequence[str], cwd: Path) -> None:
    """运行子进程并透传输出,非零退出码显式抛错(禁止静默失败)。"""
    printable = " ".join(command)
    print(f"[run] {printable}  (cwd={cwd})")
    completed = subprocess.run(command, cwd=cwd, check=False)
    if completed.returncode != 0:
        raise CommandError(f"命令失败(退出码 {completed.returncode}): {printable}")


def command_dev(_args: argparse.Namespace) -> None:
    """并发启动前端与后端开发服务,任一退出或 Ctrl+C 时统一收尾。"""
    _ensure_pnpm()
    backend = subprocess.Popen([sys.executable, "main.py", "dev"], cwd=BACKEND_DIR)
    frontend = subprocess.Popen(["pnpm", "dev"], cwd=FRONTEND_DIR)
    try:
        while backend.poll() is None and frontend.poll() is None:
            time.sleep(0.3)
    except KeyboardInterrupt:
        print("\n收到中断信号,正在停止子进程 ...")
    finally:
        for proc in (frontend, backend):
            if proc.poll() is None:
                proc.terminate()
        for proc in (frontend, backend):
            if proc.poll() is None:
                proc.wait()
        failed = [proc for proc in (frontend, backend) if proc.returncode not in (0, None)]
        if failed:
            codes = ", ".join(str(proc.returncode) for proc in failed)
            raise CommandError(f"子进程异常退出(退出码: {codes})")


def command_build(args: argparse.Namespace) -> None:
    """编译前端(完整打包)。"""
    _ensure_pnpm()
    _run(["pnpm", "build"], FRONTEND_DIR)
    del args


def command_build_copy(args: argparse.Namespace) -> None:
    """编译前端并复制产物到 backend/static(先清空旧产物)。"""
    command_build(args)
    if not DIST_DIR.is_dir():
        raise CommandError(f"编译产物不存在: {DIST_DIR}")
    if STATIC_DIR.exists():
        shutil.rmtree(STATIC_DIR)
    STATIC_DIR.mkdir(parents=True)
    shutil.copytree(DIST_DIR, STATIC_DIR, dirs_exist_ok=True)
    print(f"[done] 产物已复制到 {STATIC_DIR}")


def command_build_external(_args: argparse.Namespace) -> None:
    """无打包编译:vue / element-plus 不参与打包,由外部环境提供。"""
    _ensure_pnpm()
    _run(["pnpm", "build:external"], FRONTEND_DIR)


def command_coverage(_args: argparse.Namespace) -> None:
    """运行后端 pytest 覆盖率测试。"""
    _run([sys.executable, "-m", "pytest"], BACKEND_DIR)


def command_release(_args: argparse.Namespace) -> None:
    """以 release 模式启动后端(waitress + ws rpc)。"""
    _run([sys.executable, "main.py", "release"], BACKEND_DIR)


def build_parser() -> argparse.ArgumentParser:
    """构建命令分发解析器。"""
    parser = argparse.ArgumentParser(
        prog="manage.py",
        description="项目统一命令入口",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    commands: dict[str, Callable[[argparse.Namespace], None]] = {
        "dev": command_dev,
        "build": command_build,
        "build-copy": command_build_copy,
        "build-external": command_build_external,
        "coverage": command_coverage,
        "release": command_release,
    }
    parser.add_argument("command", choices=sorted(commands), help="要执行的命令")
    parser.set_defaults(_commands=commands)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """入口函数,返回进程退出码。"""
    parser = build_parser()
    args = parser.parse_args(argv)
    handler = args._commands[args.command]  # noqa: SLF001 - argparse namespace 内部属性
    try:
        handler(args)
    except CommandError as exc:
        print(f"[错误] {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\n已中断。", file=sys.stderr)
        return 130
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
