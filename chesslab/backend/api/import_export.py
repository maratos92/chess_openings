"""Import and export utilities."""
from __future__ import annotations

import io
from datetime import datetime

from flask import jsonify, request, abort, send_file
import chess.pgn

from ..db import db_session
from ..models import Line, Node, Opening
from . import api_bp


@api_bp.route("/import/pgn", methods=["POST"])
def import_pgn():
    data = request.get_json() or {}
    pgn_text = data.get("pgn")
    opening_id = data.get("opening_id")
    if not pgn_text or not opening_id:
        abort(400, description="pgn and opening_id required")
    line = Line(opening_id=opening_id, title=data.get("title", "Imported line"), is_main=False)
    db_session.add(line)
    db_session.flush()

    game = chess.pgn.read_game(io.StringIO(pgn_text))
    board = game.board()
    parent_id = None
    ply = 0
    for move in game.mainline_moves():
        san = board.san(move)
        board.push(move)
        ply += 1
        node = Node(
            line_id=line.id,
            parent_id=parent_id,
            san=san,
            ply=ply,
            fen=board.fen(),
            comment=None,
        )
        db_session.add(node)
        db_session.flush()
        parent_id = node.id

    db_session.commit()
    return jsonify({"line_id": line.id, "ply_count": ply})


@api_bp.route("/export/pgn/<int:line_id>", methods=["GET"])
def export_pgn(line_id: int):
    line = db_session.get(Line, line_id)
    if not line:
        abort(404, description="Line not found")

    game = chess.pgn.Game()
    game.headers["Event"] = line.title
    board = game.board()

    nodes = (
        db_session.query(Node)
        .filter(Node.line_id == line_id)
        .order_by(Node.ply)
        .all()
    )
    node_lookup = {node.id: node for node in nodes}

    sequence = []
    current = next((node for node in nodes if node.parent_id is None), None)
    while current:
        move = board.parse_san(current.san)
        board.push(move)
        sequence.append(move)
        children = [node for node in nodes if node.parent_id == current.id]
        current = children[0] if children else None

    for move in sequence:
        game.add_main_variation(move)

    export_io = io.StringIO()
    print(game, file=export_io)
    export_io.seek(0)
    return send_file(io.BytesIO(export_io.getvalue().encode("utf-8")), mimetype="application/x-chess-pgn", as_attachment=True, download_name=f"line_{line_id}.pgn")
