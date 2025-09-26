"""Endpoints for managing openings."""
from __future__ import annotations

from flask import request, jsonify

from ..db import db_session
from ..models import Opening, Line
from . import api_bp


@api_bp.route("/openings", methods=["GET"])
def list_openings():
    openings = db_session.query(Opening).order_by(Opening.created_at.desc()).all()
    return jsonify([_serialize_opening(op) for op in openings])


@api_bp.route("/openings", methods=["POST"])
def create_opening():
    data = request.get_json() or {}
    name = data.get("name") or "New Opening"
    side = data.get("side") or "white"
    opening = Opening(name=name, side=side, tags=data.get("tags"))
    db_session.add(opening)
    db_session.flush()

    if data.get("create_main_line", True):
        line = Line(opening_id=opening.id, title="Main line", is_main=True)
        db_session.add(line)

    db_session.commit()
    return jsonify(_serialize_opening(opening)), 201


def _serialize_opening(opening: Opening) -> dict:
    return {
        "id": opening.id,
        "name": opening.name,
        "side": opening.side,
        "tags": opening.tags,
        "created_at": opening.created_at.isoformat(),
    }
