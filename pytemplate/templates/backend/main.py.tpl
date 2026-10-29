"""后端启动入口。

用法:
    python main.py dev      # 开发模式:flask 内置服务器 + ws rpc
    python main.py release  # 部署模式:waitress + ws rpc

两种模式均会先在守护线程中启动 WebSocket RPC 服务,再启动 HTTP 服务。
"""

from __future__ import annotations

import argparse
import asyncio
import threading
from collections.abc import Sequence

import waitress

from types import ModuleType

from app import create_app
from app.ws import run_ws_server
from config import ConfigError, load_config


def _start_ws_server(host: str, port: int) -> threading.Thread:
    """在守护线程中运行 asyncio WebSocket RPC 服务。"""

    def _run() -> None:
        asyncio.run(run_ws_server(host, port))

    thread = threading.Thread(target=_run, name="ws-rpc", daemon=True)
    thread.start()
    return thread


def _serve_http(config: ModuleType) -> None:
    """按模式选择 HTTP 服务器并阻塞运行。"""
    app = create_app(config)
    if config.mode == "dev":
        # 关闭 reloader:避免子进程重复启动 ws 服务。
        app.run(
            host=config.http_host,
            port=config.http_port,
            debug=config.debug,
            use_reloader=False,
        )
    else:
        waitress.serve(app, host=config.http_host, port=config.http_port, threads=4)


def main(argv: Sequence[str] | None = None) -> int:
    """后端启动入口,返回进程退出码。"""
    parser = argparse.ArgumentParser(description="后端启动入口")
    parser.add_argument("mode", choices=("dev", "release"), help="运行模式")
    args = parser.parse_args(argv)

    try:
        config = load_config(args.mode)
    except ConfigError as exc:
        parser.error(str(exc))
        return 2  # parser.error 会抛 SystemExit,此行仅为类型完整。

    _start_ws_server(config.ws_host, config.ws_port)
    try:
        _serve_http(config)
    except KeyboardInterrupt:
        print("\n后端已停止。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
