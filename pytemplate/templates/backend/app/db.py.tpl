"""SQLAlchemy 引擎与会话管理(complex 模式)。"""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Optional

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


class Base(DeclarativeBase):
    """全项目 ORM 基类。"""


_engine: Optional[Engine] = None
_session_factory: Optional[sessionmaker[Session]] = None
# 初始化时传入的原始连接串(str(Engine.url) 会做 URL 转义,不能用于比较)。
_engine_url: Optional[str] = None


def init_db(database_url: str) -> Engine:
    """初始化全局引擎并创建全部表。

    Args:
        database_url: SQLAlchemy 连接串。sqlite 相对路径以 backend 目录为基准。

    Returns:
        引擎实例(同连接串重复调用时复用现有引擎)。

    Raises:
        RuntimeError: 引擎已指向其他连接串(禁止重复初始化到不同地址)。
    """
    global _engine, _engine_url, _session_factory
    if _engine is not None:
        if _engine_url == database_url:
            return _engine
        raise RuntimeError(
            f"数据库引擎已初始化为 {_engine_url},不能重复初始化为 {database_url}"
        )

    if database_url.startswith("sqlite:///"):
        db_file = Path(database_url.removeprefix("sqlite:///"))
        if not database_url.startswith("sqlite:////") and db_file.parts:
            # 相对路径:确保父目录存在,sqlite 不会自动创建目录。
            db_file.parent.mkdir(parents=True, exist_ok=True)

    _engine = create_engine(database_url, future=True)
    _engine_url = database_url
    _session_factory = sessionmaker(bind=_engine, expire_on_commit=False)
    Base.metadata.create_all(_engine)
    return _engine


@contextmanager
def session_scope() -> Iterator[Session]:
    """提供事务边界明确的会话上下文:成功提交,失败回滚并上抛(不静默)。"""
    if _session_factory is None:
        raise RuntimeError("数据库未初始化,请先调用 init_db()")
    session = _session_factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def dispose_engine() -> None:
    """释放全局引擎(测试隔离与进程退出场景使用)。"""
    global _engine, _engine_url, _session_factory
    if _engine is not None:
        _engine.dispose()
    _engine = None
    _engine_url = None
    _session_factory = None
