"""RQ worker entrypoint for server-side analysis jobs."""
from __future__ import annotations

import os

from rq import Worker, Queue, Connection
from redis import Redis

from .db import db_session
from .socketio_server import emit_eval_update
from .models import Eval
from .engine import pool


REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")


def perform_analysis(node_id: int, fen: str, depth: int, multipv: int, engine_mode: str = "server") -> list[dict]:
    results = pool.analyse(fen, depth=depth, multipv=multipv)

    eval_entries = []
    for result in results:
        eval_entry = (
            db_session.query(Eval)
            .filter(
                Eval.node_id == node_id,
                Eval.depth == depth,
                Eval.multipv == result.get("multipv", 1),
                Eval.engine_mode == engine_mode,
            )
            .one_or_none()
        )
        if not eval_entry:
            eval_entry = Eval(
                node_id=node_id,
                depth=depth,
                multipv=result.get("multipv", 1),
                engine_mode=engine_mode,
            )
            db_session.add(eval_entry)
        eval_entry.pv_uci = result.get("pv_uci")
        eval_entry.score_cp = result.get("score_cp")
        eval_entry.bestmove_uci = result.get("bestmove_uci")
        eval_entries.append(eval_entry)
    db_session.commit()

    payload = [
        {
            "multipv": ev.multipv,
            "depth": ev.depth,
            "pv_uci": ev.pv_uci,
            "score_cp": ev.score_cp,
            "bestmove_uci": ev.bestmove_uci,
        }
        for ev in eval_entries
    ]
    emit_eval_update(node_id, payload)
    return payload


def run_worker() -> None:  # pragma: no cover - entry point
    redis_conn = Redis.from_url(REDIS_URL)
    with Connection(redis_conn):
        worker = Worker([Queue("analysis")])
        worker.work()


if __name__ == "__main__":  # pragma: no cover
    run_worker()
