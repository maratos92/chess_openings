"""API blueprint registration for chesslab backend."""
from flask import Blueprint

api_bp = Blueprint("api", __name__)

# Explicitly import modules to ensure routes are registered when blueprint is used.
from . import openings, lines, nodes, evals, import_export  # noqa: E402,F401
