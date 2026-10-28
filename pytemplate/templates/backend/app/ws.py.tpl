"""WebSocket RPC 服务:基于 xuri-rpc-websocket(CBOR 二进制协议)。

通过 :func:`createServer` 注册的 mainObject 的公开方法,即可被前端远程调用。
"""

from __future__ import annotations

from typing import Final

from xuri_rpc_websocket import createServer
{{RPC_DB_IMPORTS}}

SERVER_ID: Final[str] = "{{PROJECT_NAME}}-backend"


class RpcApi:
    """通过 WebSocket RPC 暴露给前端的方法集合。"""

    def ping(self, message: str) -> str:
        """回声方法:前端连接后远程调用即可验证链路。"""
        return f"pong: {message}"
{{RPC_DB_METHODS}}


async def run_ws_server(host: str, port: int) -> None:
    """启动 WebSocket RPC 服务器并阻塞直至关闭。"""
    serve, _ws_server = await createServer(SERVER_ID, host, port)
    await serve(RpcApi())
