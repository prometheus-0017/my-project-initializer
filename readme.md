# pytemplate

前后端项目初始化模板生成器。按用户参数生成一套可运行的项目骨架:

- **simple 模式**:`pnpm` + `vue3` + `vite` / `flask` + `waitress` + `xuri-rpc-websocket`
- **complex 模式**:在 simple 基础上额外支持 `element-plus` 与 `SQLAlchemy`
- 顶层自带 `.gitignore`(不初始化 git 仓库),目录划分为 `frontend` / `backend`
- 后端含独立配置文件 `config/dev.py` 与 `config/release.py`,按 dev / release 模式加载
- 生成的后端已配置 `pytest` + 覆盖率测试(`pytest-cov`)

## 用法

```bash
# 纯参数(缺失端口随机分配)
python -m pytemplate --name demo --mode complex \
    --frontend-port 5173 \
    --backend-dev-http-port 5001 \
    --backend-dev-ws-port 5002 \
    --backend-release-http-port 8001 \
    --backend-release-ws-port 8002

# 交互式(缺省参数逐项询问,端口回车即随机)
python -m pytemplate
```

### 参数

| 参数 | 说明 | 缺省行为 |
| --- | --- | --- |
| `--name / -n` | 项目名称(同时作为目录名) | 交互询问;`--no-input` 时报错 |
| `--mode / -m` | `simple` / `complex` | 交互询问;`--no-input` 时取 `simple` |
| `--frontend-port` | 前端开发端口 | 随机 |
| `--backend-dev-http-port` | 后端开发 HTTP 端口 | 随机 |
| `--backend-dev-ws-port` | 后端开发 WS 端口 | 随机 |
| `--backend-release-http-port` | 后端部署 HTTP 端口 | 随机 |
| `--backend-release-ws-port` | 后端部署 WS 端口 | 随机 |
| `--output / -o` | 输出目录 | `当前目录/<项目名>` |
| `--no-input` | 禁用交互 | 缺失参数按缺省行为处理 |

随机端口由独立函数 `pytemplate.port.pick_free_port` 分配(探测绑定 + 随机挑
选 + 排除已分配端口),后续扩展(指定网段、保留端口等)只需修改该函数。

## 生成项目的命令(项目根目录 `manage.py`)

| 命令 | 说明 |
| --- | --- |
| `python manage.py dev` | 并发启动前端 vite 与后端 dev(flask + ws rpc) |
| `python manage.py build` | 编译前端(完整打包) |
| `python manage.py build-copy` | 编译前端并把产物复制到 `backend/static` |
| `python manage.py coverage` | 后端 pytest 覆盖率测试 |
| `python manage.py release` | 后端 release 模式启动(waitress) |
| `python manage.py build-external` | 无打包编译:vue / element-plus 不参与打包,产物经 import map 引用外部库 |

## 开发(本生成器)

```bash
pip install -e .[dev]
pytest          # 运行测试(自动输出覆盖率)
```

## 目录说明

```
pytemplate/
├── pytemplate/          # 生成器实现(cli/context/port/renderer/generator)
│   └── templates/       # 模板文件(*.tpl,{{占位符}} 渲染)
└── tests/               # 生成器自身测试(pytest + 覆盖率)
```
