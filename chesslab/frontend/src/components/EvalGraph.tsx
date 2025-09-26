import React, { useMemo } from 'react';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import { useChessStore } from '../store';

const EvalGraph: React.FC = () => {
  const { selectedLineId, nodes, evals } = useChessStore();

  const data = useMemo(() => {
    if (!selectedLineId) return [];
    return (nodes[selectedLineId] || []).map((node) => {
      const entry = (evals[node.id] || [])[0];
      const score = entry?.score_cp ?? 0;
      return {
        ply: node.ply,
        score,
      };
    });
  }, [selectedLineId, nodes, evals]);

  return (
    <div className="eval-graph">
      <ResponsiveContainer width="100%" height={200}>
        <LineChart data={data}>
          <XAxis dataKey="ply" />
          <YAxis domain={[-500, 500]} />
          <Tooltip />
          <Line type="monotone" dataKey="score" stroke="#8884d8" dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default EvalGraph;
