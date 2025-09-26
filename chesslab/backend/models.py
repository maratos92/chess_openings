"""SQLAlchemy models for the chesslab application."""
from __future__ import annotations

from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Index, Integer, String, Boolean, Text, UniqueConstraint
from sqlalchemy.orm import relationship, Mapped, mapped_column

from .db import Base


class Opening(Base):
    __tablename__ = "openings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    side: Mapped[str] = mapped_column(String(5), nullable=False, default="white")
    tags: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    lines: Mapped[list["Line"]] = relationship("Line", back_populates="opening", cascade="all, delete-orphan")


class Line(Base):
    __tablename__ = "lines"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    opening_id: Mapped[int] = mapped_column(ForeignKey("openings.id", ondelete="CASCADE"), nullable=False)
    title: Mapped[str] = mapped_column(String(120), nullable=False)
    is_main: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    opening: Mapped[Opening] = relationship("Opening", back_populates="lines")
    nodes: Mapped[list["Node"]] = relationship("Node", back_populates="line", cascade="all, delete-orphan")

    __table_args__ = (Index("ix_lines_opening_id", "opening_id"),)


class Node(Base):
    __tablename__ = "nodes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    line_id: Mapped[int] = mapped_column(ForeignKey("lines.id", ondelete="CASCADE"), nullable=False)
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("nodes.id", ondelete="CASCADE"), nullable=True)
    san: Mapped[str] = mapped_column(String(20), nullable=False)
    ply: Mapped[int] = mapped_column(Integer, nullable=False)
    fen: Mapped[str] = mapped_column(Text, nullable=False)
    comment: Mapped[str | None] = mapped_column(Text)

    parent: Mapped["Node" | None] = relationship("Node", remote_side="Node.id")
    line: Mapped[Line] = relationship("Line", back_populates="nodes")
    evals: Mapped[list["Eval"]] = relationship("Eval", back_populates="node", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("line_id", "parent_id", "san", name="uq_node_san"),
        Index("ix_nodes_line_ply", "line_id", "ply"),
    )


class Eval(Base):
    __tablename__ = "evals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    node_id: Mapped[int] = mapped_column(ForeignKey("nodes.id", ondelete="CASCADE"), nullable=False)
    depth: Mapped[int] = mapped_column(Integer, nullable=False)
    multipv: Mapped[int] = mapped_column(Integer, nullable=False)
    pv_uci: Mapped[str | None] = mapped_column(Text)
    score_cp: Mapped[int | None] = mapped_column(Integer)
    score_mate: Mapped[int | None] = mapped_column(Integer)
    bestmove_uci: Mapped[str | None] = mapped_column(String(10))
    engine_mode: Mapped[str] = mapped_column(String(10), nullable=False, default="client")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    node: Mapped[Node] = relationship("Node", back_populates="evals")

    __table_args__ = (
        Index("ix_eval_node_depth", "node_id", "depth", "multipv", "engine_mode"),
    )
