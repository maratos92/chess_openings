from __future__ import annotations

from unittest import mock

import pytest

from ..models import Eval, Node, Line, Opening
from ..db import db_session
from ..socketio_server import emit_eval_update
from ..worker import perform_analysis


class SocketRecorder:
    def __init__(self):
        self.messages = []

    def __call__(self, node_id, payload):
        self.messages.append((node_id, payload))


def test_server_job_writes_evals(monkeypatch):
    opening = Opening(name="Test", side="white")
    db_session.add(opening)
    db_session.flush()

    line = Line(opening_id=opening.id, title="Test line", is_main=True)
    db_session.add(line)
    db_session.flush()

    node = Node(line_id=line.id, parent_id=None, san="e4", ply=1, fen="startpos")
    db_session.add(node)
    db_session.flush()

    fake_results = [
        {"multipv": 1, "pv_uci": "e2e4 e7e5", "score_cp": 20, "bestmove_uci": "e2e4"},
        {"multipv": 2, "pv_uci": "d2d4 d7d5", "score_cp": 15, "bestmove_uci": "d2d4"},
        {"multipv": 3, "pv_uci": "c2c4 e7e5", "score_cp": 10, "bestmove_uci": "c2c4"},
    ]

    recorder = SocketRecorder()
    monkeypatch.setattr("chesslab.backend.worker.emit_eval_update", recorder)
    monkeypatch.setattr("chesslab.backend.engine.pool.analyse", lambda fen, depth, multipv: fake_results)

    payload = perform_analysis(node.id, node.fen, depth=12, multipv=3)

    assert len(payload) == 3
    stored = (
        db_session.query(Eval)
        .filter(Eval.node_id == node.id)
        .order_by(Eval.multipv)
        .all()
    )
    assert len(stored) == 3
    assert recorder.messages[0][0] == node.id
    assert recorder.messages[0][1][0]["bestmove_uci"] == "e2e4"
