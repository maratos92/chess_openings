"""Evaluation endpoints."""
from __future__ import annotations

from datetime import datetime

from flask import jsonify, request, current_app
from rq import Queue
from redis import Redis

from ..db import db_session
from ..models import Eval, Node
from ..socketio_server import emit_eval_update
from ..worker import perform_analysis
from . import api_bp


@api_bp.route("/eval", methods=["GET"])
def get_eval():
    node_id_raw = request.args.get("node_id")
    if not node_id_raw:
        return jsonify({"error": "node_id required"}), 400
    node_id = int(node_id_raw)
    depth = int(request.args.get("depth", 12))
    multipv = int(request.args.get("multipv", 3))
    mode = request.args.get("mode", "client")

    existing = (
        db_session.query(Eval)
        .filter(
            Eval.node_id == node_id,
            Eval.depth == depth,
            Eval.multipv <= multipv,
        )
        .order_by(Eval.multipv)
        .all()
    )
    if mode == "client":
        return jsonify({"pending": False, "evals": [_serialize_eval(ev) for ev in existing]})

    if mode == "server":
        node = db_session.get(Node, node_id)
        if not node:
            return jsonify({"pending": False, "error": "Node not found"}), 404
        redis_url = current_app.config.get("REDIS_URL", "redis://localhost:6379/0")
        redis_conn = Redis.from_url(redis_url)
        queue = Queue("analysis", connection=redis_conn)
        queue.enqueue(perform_analysis, node_id=node_id, fen=node.fen, depth=depth, multipv=multipv)
        return jsonify({"pending": True})

    return jsonify({"pending": False, "evals": [_serialize_eval(ev) for ev in existing]})


@api_bp.route("/eval", methods=["POST"])
def post_eval():
    data = request.get_json() or {}
    node_id = data.get("node_id")
    if not node_id:
        return jsonify({"error": "node_id required"}), 400

    evals_payload = data.get("evals", [])
    mode = data.get("engine_mode", "client")
    stored = []
    for payload in evals_payload:
        depth = payload.get("depth", 0)
        multipv = payload.get("multipv", 1)
        eval_entry = (
            db_session.query(Eval)
            .filter(
                Eval.node_id == node_id,
                Eval.depth == depth,
                Eval.multipv == multipv,
                Eval.engine_mode == mode,
            )
            .one_or_none()
        )
        if not eval_entry:
            eval_entry = Eval(
                node_id=node_id,
                depth=depth,
                multipv=multipv,
                engine_mode=mode,
            )
            db_session.add(eval_entry)
        eval_entry.pv_uci = payload.get("pv_uci")
        eval_entry.score_cp = payload.get("score_cp")
        eval_entry.bestmove_uci = payload.get("bestmove_uci")
        eval_entry.created_at = datetime.utcnow()
        stored.append(eval_entry)
    db_session.commit()

    serialized = [_serialize_eval(ev) for ev in stored]
    emit_eval_update(node_id, serialized)
    return jsonify({"saved": True, "evals": serialized})


def _serialize_eval(ev: Eval) -> dict:
    return {
        "id": ev.id,
        "node_id": ev.node_id,
        "depth": ev.depth,
        "multipv": ev.multipv,
        "pv_uci": ev.pv_uci,
        "score_cp": ev.score_cp,
        "bestmove_uci": ev.bestmove_uci,
        "engine_mode": ev.engine_mode,
        "created_at": ev.created_at.isoformat() if ev.created_at else None,
    }
