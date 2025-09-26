"""Socket.IO configuration for the chesslab backend."""
from __future__ import annotations

from flask_socketio import SocketIO

socketio = SocketIO(async_mode="threading")


def emit_eval_update(node_id: int, evals: list[dict]) -> None:
    socketio.emit("eval_update", {"type": "eval_update", "node_id": node_id, "evals": evals})
