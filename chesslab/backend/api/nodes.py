"""Node management endpoints."""
from __future__ import annotations

from typing import List

from flask import request, jsonify, abort
import chess

from ..db import db_session
from ..models import Line, Node
from . import api_bp


@api_bp.route("/lines/<int:line_id>/nodes", methods=["GET"])
def list_nodes(line_id: int):
    nodes = (
        db_session.query(Node)
        .filter(Node.line_id == line_id)
        .order_by(Node.ply, Node.id)
        .all()
    )
    return jsonify([_serialize_node(node) for node in nodes])


@api_bp.route("/lines/<int:line_id>/nodes", methods=["POST"])
def add_node(line_id: int):
    line = db_session.get(Line, line_id)
    if not line:
        abort(404, description="Line not found")

    data = request.get_json() or {}
    parent_id = data.get("parent_id")
    san = data.get("san")
    comment = data.get("comment")

    if not san:
        abort(400, description="SAN move required")

    board = chess.Board()
    ply = 0

    if parent_id:
        parent = db_session.get(Node, parent_id)
        if not parent or parent.line_id != line_id:
            abort(404, description="Parent node not in line")
        path: List[Node] = []
        current = parent
        while current is not None:
            path.append(current)
            current = current.parent
        for node in reversed(path):
            board.push_san(node.san)
            ply = node.ply

    try:
        move = board.parse_san(san)
    except ValueError as exc:  # invalid san
        abort(400, description=str(exc))

    board.push(move)
    new_node = Node(
        line_id=line_id,
        parent_id=parent_id,
        san=san,
        ply=ply + 1,
        fen=board.fen(),
        comment=comment,
    )
    db_session.add(new_node)
    db_session.commit()
    return jsonify(_serialize_node(new_node)), 201


def _serialize_node(node: Node) -> dict:
    return {
        "id": node.id,
        "line_id": node.line_id,
        "parent_id": node.parent_id,
        "san": node.san,
        "ply": node.ply,
        "fen": node.fen,
        "comment": node.comment,
    }
