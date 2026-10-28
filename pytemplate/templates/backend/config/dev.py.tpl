"""开发环境配置(dev 模式)。"""

from .base import APP_NAME

mode = "dev"
debug = True

http_host = "127.0.0.1"
http_port = {{BACKEND_DEV_HTTP_PORT}}
ws_host = "127.0.0.1"
ws_port = {{BACKEND_DEV_WS_PORT}}

database_url = "{{DEV_DATABASE_URL}}"
