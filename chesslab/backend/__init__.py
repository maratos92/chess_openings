"""Backend package initialization for chesslab."""

from .app import create_app  # re-export for convenience

__all__ = ["create_app"]
