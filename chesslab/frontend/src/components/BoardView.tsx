import React, { useMemo } from 'react';
import { Chessboard } from 'react-chessboard';
import { useChessStore } from '../store';

const BoardView: React.FC = () => {
  const { selectedLineId, selectedNodeId, nodes, multipv, evals } = useChessStore();

  const fen = useMemo(() => {
    if (!selectedLineId) return 'start';
    const lineNodes = nodes[selectedLineId] || [];
    if (!selectedNodeId) return 'start';
    const node = lineNodes.find((n) => n.id === selectedNodeId);
    return node?.fen || 'start';
  }, [selectedLineId, selectedNodeId, nodes]);

  const arrows = useMemo(() => {
    if (!selectedNodeId) return [] as [string, string][];
    const entries = evals[selectedNodeId] || [];
    return entries.slice(0, multipv).map((entry) => {
      if (!entry.pv_uci) return ['a1', 'a1'] as [string, string];
      const move = entry.pv_uci.split(' ')[0];
      return [move.slice(0, 2), move.slice(2, 4)] as [string, string];
    });
  }, [evals, multipv, selectedNodeId]);

  return (
    <div className="board-view">
      <Chessboard id="main-board" position={fen} customArrows={arrows} arePiecesDraggable={false} />
    </div>
  );
};

export default BoardView;
