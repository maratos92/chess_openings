import React from 'react';
import { useChessStore } from '../store';

const clampScore = (cp: number | null) => {
  if (cp === null || Number.isNaN(cp)) return 0;
  return Math.max(-1000, Math.min(1000, cp));
};

const EvalPanel: React.FC = () => {
  const { selectedNodeId, evals } = useChessStore();
  const entries = (selectedNodeId && evals[selectedNodeId]) || [];

  return (
    <div className="eval-panel">
      <h4>Engine Evaluations</h4>
      <ul>
        {entries.map((entry) => (
          <li key={entry.multipv}>
            <span>#{entry.multipv}</span>
            <span>{entry.pv_uci}</span>
            <span>{clampScore(entry.score_cp)}</span>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default EvalPanel;
