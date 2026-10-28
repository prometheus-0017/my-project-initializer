"""部署环境配置(release 模式)。"""

from .base import APP_NAME

mode = "release"
debug = False

http_host = "0.0.0.0"
http_port = {{BACKEND_RELEASE_HTTP_PORT}}
ws_host = "0.0.0.0"
ws_port = {{BACKEND_RELEASE_WS_PORT}}

database_url = "{{RELEASE_DATABASE_URL}}"
