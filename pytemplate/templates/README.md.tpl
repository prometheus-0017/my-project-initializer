# {{PROJECT_NAME}}

由 pytemplate 生成的 **{{MODE}}** 模式前后端项目。

## 目录结构

```
{{PROJECT_NAME}}/
├── manage.py            # 统一命令入口
├── frontend/            # Vue3 + Vite(pnpm)
│   ├── src/
│   │   ├── App.vue
│   │   ├── main.ts
│   │   └── api/         # HTTP 与 WebSocket 封装
│   ├── vite.config.ts   # dev 端口 / 代理 / external 构建
│   └── package.json
└── backend/             # Flask + Waitress + WebSocket RPC
    ├── run.py           # 后端启动入口(dev / release)
    ├── config/          # 独立配置文件(dev.py / release.py)
    ├── app/             # 应用代码(HTTP 路由 + WS RPC)
    ├── static/          # 前端构建产物复制目标
    └── tests/           # pytest 测试(含覆盖率配置)
```

## 常用命令(项目根目录)

| 命令 | 说明 |
| --- | --- |
| `python manage.py dev` | 并发启动前端 vite 与后端 dev(flask + ws rpc) |
| `python manage.py build` | 编译前端(完整打包 vue / element-plus) |
| `python manage.py build-copy` | 编译前端并把产物复制到 `backend/static` |
| `python manage.py coverage` | 运行后端 pytest 覆盖率测试 |
| `python manage.py release` | 后端以 release 模式启动(waitress + ws rpc) |
| `python manage.py build-external` | 无打包编译:vue / element-plus 不参与打包,产物经 import map 引用外部库 |

## 端口分配

| 用途 | 端口 |
| --- | --- |
| 前端开发(vite) | {{FRONTEND_DEV_PORT}} |
| 后端开发 HTTP | {{BACKEND_DEV_HTTP_PORT}} |
| 后端开发 WS | {{BACKEND_DEV_WS_PORT}} |
| 后端部署 HTTP | {{BACKEND_RELEASE_HTTP_PORT}} |
| 后端部署 WS | {{BACKEND_RELEASE_WS_PORT}} |

## 首次准备

1. 前端依赖:`cd frontend && pnpm install`
2. 后端依赖(建议先创建虚拟环境):`cd backend && pip install -r requirements.txt`

## 说明

- 后端配置位于 `backend/config`,`dev.py` 与 `release.py` 为两套独立配置文件,由 `python run.py <mode>` 选择加载。
- WebSocket RPC 基于 [xuri-rpc-websocket](https://pypi.org/project/xuri-rpc-websocket/)(CBOR 二进制协议),后端暴露方法见 `backend/app/ws.py`,前端通道封装见 `frontend/src/api/ws.ts`。
- `build-external` 产物不包含 vue / element-plus 代码,通过 import map 指向 CDN;部署到新环境时可替换为本地库文件地址。
