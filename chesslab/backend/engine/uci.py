"""Basic UCI wrapper for Stockfish."""
from __future__ import annotations

import os
import shutil
import subprocess
import threading
from queue import Queue, Empty


class UCIEngineError(RuntimeError):
    """Raised when the UCI engine encounters an error."""


class UCIEngine:
    def __init__(self, command: str | None = None) -> None:
        self.command = command or os.getenv("STOCKFISH_PATH", "stockfish")
        if not shutil.which(self.command):
            raise UCIEngineError(f"Stockfish binary not found: {self.command}")
        self.process = subprocess.Popen(
            [self.command],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )
        self.stdout_queue: Queue[str] = Queue()
        self.listener = threading.Thread(target=self._enqueue_output, daemon=True)
        self.listener.start()
        self._send("uci")
        self._wait_for("uciok")

    def close(self) -> None:
        if self.process.poll() is None:
            self._send("quit")
            self.process.wait(timeout=2)

    def _enqueue_output(self) -> None:
        assert self.process.stdout is not None
        for line in self.process.stdout:
            self.stdout_queue.put(line.strip())

    def _send(self, command: str) -> None:
        if not self.process.stdin:
            raise UCIEngineError("Engine stdin closed")
        self.process.stdin.write(command + "\n")
        self.process.stdin.flush()

    def _wait_for(self, token: str, timeout: float = 5.0) -> None:
        while True:
            try:
                line = self.stdout_queue.get(timeout=timeout)
            except Empty as exc:  # pragma: no cover - defensive
                raise UCIEngineError(f"Timeout waiting for {token}") from exc
            if token in line:
                return

    def set_option(self, name: str, value: str | int) -> None:
        self._send(f"setoption name {name} value {value}")

    def analyse(self, fen: str, *, depth: int | None = None, movetime: int | None = None, multipv: int = 3):
        if depth is None and movetime is None:
            depth = 12
        self._send("ucinewgame")
        self._send(f"position fen {fen}")
        self._send(f"setoption name MultiPV value {multipv}")
        if depth is not None:
            self._send(f"go depth {depth}")
        elif movetime is not None:
            self._send(f"go movetime {movetime}")

        results: list[dict] = []
        while True:
            try:
                line = self.stdout_queue.get(timeout=10)
            except Empty as exc:  # pragma: no cover
                raise UCIEngineError("Engine timed out") from exc
            if line.startswith("info") and "pv" in line:
                results = self._parse_info(line, results)
            elif line.startswith("bestmove"):
                break
        return sorted(results, key=lambda r: r["multipv"])

    def _parse_info(self, line: str, results: list[dict]) -> list[dict]:
        parts = line.split()
        info: dict[str, int | str] = {}
        if "multipv" in parts:
            info["multipv"] = int(parts[parts.index("multipv") + 1])
        if "depth" in parts:
            info["depth"] = int(parts[parts.index("depth") + 1])
        if "score" in parts:
            idx = parts.index("score")
            score_type = parts[idx + 1]
            score_value = int(parts[idx + 2])
            if score_type == "cp":
                info["score_cp"] = score_value
            elif score_type == "mate":
                info["score_mate"] = score_value
        if "pv" in parts:
            pv_index = parts.index("pv") + 1
            pv_moves = parts[pv_index:]
            info["pv_uci"] = " ".join(pv_moves)
            info["bestmove_uci"] = pv_moves[0] if pv_moves else None
        multipv = int(info.get("multipv", 1))
        while len(results) < multipv:
            results.append({"multipv": len(results) + 1})
        results[multipv - 1].update(info)
        return results


def analyse(fen: str, *, depth: int | None = None, movetime: int | None = None, multipv: int = 3):
    engine = UCIEngine()
    try:
        return engine.analyse(fen, depth=depth, movetime=movetime, multipv=multipv)
    finally:
        engine.close()
