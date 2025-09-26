"""Endpoints for managing lines."""
from __future__ import annotations

from flask import request, jsonify, abort

from ..db import db_session
from ..models import Line, Node
from . import api_bp


@api_bp.route("/lines/<int:line_id>", methods=["GET"])
def get_line(line_id: int):
    line = db_session.get(Line, line_id)
    if not line:
        abort(404, description="Line not found")
    return jsonify(_serialize_line(line))


@api_bp.route("/openings/<int:opening_id>/lines", methods=["GET"])
def list_lines(opening_id: int):
    lines = db_session.query(Line).filter(Line.opening_id == opening_id).order_by(Line.created_at).all()
    return jsonify([_serialize_line(line) for line in lines])


@api_bp.route("/openings/<int:opening_id>/lines", methods=["POST"])
def create_line(opening_id: int):
    data = request.get_json() or {}
    title = data.get("title") or "New line"
    line = Line(opening_id=opening_id, title=title, is_main=data.get("is_main", False))
    db_session.add(line)
    db_session.commit()
    return jsonify(_serialize_line(line)), 201


def _serialize_line(line: Line) -> dict:
    return {
        "id": line.id,
        "opening_id": line.opening_id,
        "title": line.title,
        "is_main": line.is_main,
        "created_at": line.created_at.isoformat(),
    }
