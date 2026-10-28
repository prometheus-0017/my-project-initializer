"""从已生成的项目中提取配置信息。"""

from __future__ import annotations

import re
from pathlib import Path


def extract_project_info(project_dir: str | Path) -> dict[str, str | int]:
    """从已生成的项目中提取项目名称及各端口配置。

    Args:
        project_dir: 项目根目录路径。

    Returns:
        包含以下键的字典:
        - project_name: 项目名称
        - frontend_dev_port: 前端开发端口
        - backend_dev_http_port: 后端开发 HTTP 端口
        - backend_dev_ws_port: 后端开发 WS 端口
        - backend_release_http_port: 后端部署 HTTP 端口
        - backend_release_ws_port: 后端部署 WS 端口

    Raises:
        FileNotFoundError: 项目目录或必要文件不存在。
        ValueError: 无法从配置文件中解析出所需值。
    """
    root = Path(project_dir)
    if not root.is_dir():
        raise FileNotFoundError(f"项目目录不存在: {root}")

    # 1. 项目名称: backend/config/base.py → APP_NAME = "xxx"
    base_cfg = root / "backend" / "config" / "base.py"
    project_name = _extract_value(base_cfg, r'APP_NAME\s*=\s*["\']([^"\']+)["\']', "APP_NAME")

    # 2. 前端开发端口: frontend/vite.config.ts → port: 1234
    vite_cfg = root / "frontend" / "vite.config.ts"
    frontend_dev_port = _extract_int(vite_cfg, r"port:\s*(\d+)", "server.port")

    # 3. 后端 dev 端口: backend/config/dev.py → http_port / ws_port
    dev_cfg = root / "backend" / "config" / "dev.py"
    backend_dev_http_port = _extract_int(dev_cfg, r"http_port\s*=\s*(\d+)", "http_port")
    backend_dev_ws_port = _extract_int(dev_cfg, r"ws_port\s*=\s*(\d+)", "ws_port")

    # 4. 后端 release 端口: backend/config/release.py → http_port / ws_port
    release_cfg = root / "backend" / "config" / "release.py"
    backend_release_http_port = _extract_int(release_cfg, r"http_port\s*=\s*(\d+)", "http_port")
    backend_release_ws_port = _extract_int(release_cfg, r"ws_port\s*=\s*(\d+)", "ws_port")

    return {
        "project_name": project_name,
        "frontend_dev_port": frontend_dev_port,
        "backend_dev_http_port": backend_dev_http_port,
        "backend_dev_ws_port": backend_dev_ws_port,
        "backend_release_http_port": backend_release_http_port,
        "backend_release_ws_port": backend_release_ws_port,
    }


def _extract_value(file_path: Path, pattern: str, label: str) -> str:
    """从文件中用正则提取单个字符串值。"""
    text = _read_file(file_path)
    match = re.search(pattern, text)
    if not match:
        raise ValueError(f"无法在 {file_path} 中解析出 {label}")
    return match.group(1)


def _extract_int(file_path: Path, pattern: str, label: str) -> int:
    """从文件中用正则提取单个整数值。"""
    return int(_extract_value(file_path, pattern, label))


def _read_file(file_path: Path) -> str:
    """读取文件内容,文件不存在时抛出 FileNotFoundError。"""
    if not file_path.is_file():
        raise FileNotFoundError(f"配置文件不存在: {file_path}")
    return file_path.read_text(encoding="utf-8")


if __name__ == "__main__":
    # 演示:提取 demo 项目的配置信息
    demo_dir = Path(__file__).parent / "demo"

    try:
        info = extract_project_info(demo_dir)
        print(f"项目目录: {demo_dir}")
        print()
        print(f"  项目名称:          {info['project_name']}")
        print(f"  前端开发端口:      {info['frontend_dev_port']}")
        print(f"  后端开发 HTTP 端口: {info['backend_dev_http_port']}")
        print(f"  后端开发 WS 端口:  {info['backend_dev_ws_port']}")
        print(f"  后端部署 HTTP 端口: {info['backend_release_http_port']}")
        print(f"  后端部署 WS 端口:  {info['backend_release_ws_port']}")
    except (FileNotFoundError, ValueError) as e:
        print(f"[错误] {e}")