"""SQLAlchemy 模型与会话测试(complex 模式)。"""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.db import dispose_engine, init_db, session_scope
from app.models import User


@pytest.fixture()
def database(tmp_path: Path) -> Iterator[Path]:
    """每个测试使用独立的临时数据库文件,测试间互不影响。"""
    dispose_engine()
    db_file = tmp_path / "test.db"
    init_db(f"sqlite:///{db_file.as_posix()}")
    yield db_file
    dispose_engine()


def test_user_roundtrip(database: Path) -> None:
    """写入与读取 User 均正常。"""
    with session_scope() as session:
        session.add(User(name="alice", email="alice@example.com"))

    with session_scope() as session:
        users = session.scalars(select(User)).all()
        assert len(users) == 1
        assert users[0].as_dict()["name"] == "alice"


def test_unique_name_constraint(database: Path) -> None:
    """重复用户名触发唯一约束并回滚上抛(不静默)。"""
    with pytest.raises(IntegrityError):
        with session_scope() as session:
            session.add(User(name="bob", email="bob1@example.com"))
            session.add(User(name="bob", email="bob2@example.com"))
