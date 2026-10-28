"""pytest 共享夹具。"""

from __future__ import annotations

import importlib.util
from dataclasses import replace

import pytest
from flask import Flask
from flask.testing import FlaskClient

from app import create_app
from config import load_config

# complex 模式才有 app.db 模块;simple 模式下保持 None。
if importlib.util.find_spec("app.db") is not None:
    from app.db import dispose_engine
else:
    dispose_engine = None


@pytest.fixture(scope="session")
def database_url(tmp_path_factory: pytest.TempPathFactory) -> str:
    """整个测试会话共用一个临时数据库地址,结束后释放引擎。"""
    db_file = tmp_path_factory.mktemp("db") / "app.db"
    yield f"sqlite:///{db_file.as_posix()}"
    if dispose_engine is not None:
        dispose_engine()


@pytest.fixture()
def app(database_url: str) -> Flask:
    """开发配置下的应用实例。

    complex 模式下数据库被替换为会话级临时文件,避免测试写入真实数据目录;
    simple 模式下 database_url 为空,保持原配置。
    """
    config = load_config("dev")
    if config.database_url:
        config = replace(config, database_url=database_url)
    return create_app(config)


@pytest.fixture()
def client(app: Flask) -> FlaskClient:
    """Flask 测试客户端。"""
    return app.test_client()
