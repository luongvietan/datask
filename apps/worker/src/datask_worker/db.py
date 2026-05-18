# -*- coding: utf-8 -*-
"""
Sync SQLAlchemy session factory cho worker process.
Worker dùng sync engine vì RQ tasks là sync functions.
"""
import os
from contextlib import contextmanager
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

_engine = None
_session_factory = None


def _get_sync_url() -> str:
    """Chuyển asyncpg URL sang psycopg2 sync URL cho worker."""
    url = os.environ.get("DATABASE_URL", "postgresql://datask:datask@localhost:5432/datask")
    return url.replace("postgresql+asyncpg://", "postgresql://").replace("+asyncpg", "")


def get_session_factory():
    global _engine, _session_factory
    if _engine is None:
        _engine = create_engine(_get_sync_url(), pool_pre_ping=True, pool_size=2)
        _session_factory = sessionmaker(bind=_engine, expire_on_commit=False)
    return _session_factory


@contextmanager
def get_session() -> Generator[Session, None, None]:
    factory = get_session_factory()
    session = factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
