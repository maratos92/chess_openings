"""Simple engine pool that keeps a single persistent Stockfish instance."""
from __future__ import annotations

import threading
from contextlib import contextmanager
from typing import Iterator

from .uci import UCIEngine, UCIEngineError


_engine: UCIEngine | None = None
_lock = threading.Lock()


def _get_engine() -> UCIEngine:
    global _engine
    with _lock:
        if _engine is None:
            _engine = UCIEngine()
        return _engine


@contextmanager
def engine_session() -> Iterator[UCIEngine]:
    engine = _get_engine()
    try:
        yield engine
    finally:
        pass


def analyse(fen: str, *, depth: int | None = None, multipv: int = 3):
    with engine_session() as engine:
        engine.set_option("MultiPV", multipv)
        return engine.analyse(fen, depth=depth, multipv=multipv)
