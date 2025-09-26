"""Database helpers for the chesslab backend."""
from __future__ import annotations

from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker, DeclarativeBase


class Base(DeclarativeBase):
    pass


_engine = None
Session = sessionmaker(autocommit=False, autoflush=False)
db_session = scoped_session(Session)


def init_engine(database_uri: str) -> None:
    global _engine
    if _engine is None:
        _engine = create_engine(database_uri, future=True, echo=False)
        Session.configure(bind=_engine)


def get_engine():
    if _engine is None:
        raise RuntimeError("Database engine not initialized")
    return _engine


@contextmanager
def session_scope():
    session = db_session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
