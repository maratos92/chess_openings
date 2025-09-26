from __future__ import annotations

import pytest
import chess

from ..models import Line, Node
from ..db import db_session


def test_san_to_fen_sequence():
    line = Line(opening_id=1, title="Test", is_main=True)
    db_session.add(line)
    db_session.flush()

    board = chess.Board()
    moves = ["d4", "d5", "e4", "dxe4", "Nc3"]
    parent_id = None
    for idx, san in enumerate(moves, start=1):
        move = board.parse_san(san)
        board.push(move)
        node = Node(line_id=line.id, parent_id=parent_id, san=san, ply=idx, fen=board.fen())
        db_session.add(node)
        db_session.flush()
        parent_id = node.id

    final_node = db_session.query(Node).order_by(Node.ply.desc()).first()
    assert final_node.fen.startswith("rnbqkb1r/ppp1pppp/8/3p4/4P3/2N5/PPPP1PPP/R1BQKBNR b KQkq - 1 3")

    with pytest.raises(ValueError):
        chess.Board().parse_san("Qh9")
