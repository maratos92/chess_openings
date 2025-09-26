from __future__ import annotations

import io

import chess.pgn
import pytest

from ..models import Opening, Line, Node
from ..db import db_session


def test_unique_san_constraint():
    opening = Opening(name="Test", side="white")
    db_session.add(opening)
    db_session.flush()

    line = Line(opening_id=opening.id, title="Main", is_main=True)
    db_session.add(line)
    db_session.flush()

    node1 = Node(line_id=line.id, parent_id=None, san="e4", ply=1, fen=chess.pgn.Game().board().fen())
    db_session.add(node1)
    db_session.flush()

    duplicate = Node(line_id=line.id, parent_id=None, san="e4", ply=1, fen=node1.fen)
    db_session.add(duplicate)
    with pytest.raises(Exception):
        db_session.flush()
    db_session.rollback()


def test_pgn_import_ply_counts():
    opening = Opening(name="Imported", side="white")
    db_session.add(opening)
    db_session.flush()

    pgn_text = """[Event "Test"]\n\n1. e4 e5 2. Nf3 Nc6 3. Bb5 a6"""
    game = chess.pgn.read_game(io.StringIO(pgn_text))
    board = game.board()
    line = Line(opening_id=opening.id, title="Ruy Lopez", is_main=False)
    db_session.add(line)
    db_session.flush()

    parent_id = None
    ply = 0
    for move in game.mainline_moves():
        san = board.san(move)
        board.push(move)
        ply += 1
        node = Node(line_id=line.id, parent_id=parent_id, san=san, ply=ply, fen=board.fen())
        db_session.add(node)
        db_session.flush()
        parent_id = node.id

    assert ply == 6
    stored = db_session.query(Node).filter(Node.line_id == line.id).count()
    assert stored == 6
