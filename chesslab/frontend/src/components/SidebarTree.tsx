import React from 'react';
import { useChessStore } from '../store';

const SidebarTree: React.FC = () => {
  const { openings, lines, nodes, selectedOpeningId, selectedLineId, selectOpening, selectLine, selectNode } =
    useChessStore();

  return (
    <div className="sidebar-tree">
      {openings.map((opening) => (
        <div key={opening.id} className="opening-block">
          <button type="button" className={selectedOpeningId === opening.id ? 'selected' : ''} onClick={() => selectOpening(opening.id)}>
            {opening.name}
          </button>
          <ul>
            {(lines[opening.id] || []).map((line) => (
              <li key={line.id} className={selectedLineId === line.id ? 'selected' : ''}>
                <button type="button" onClick={() => selectLine(line.id)}>
                  {line.title}
                </button>
                <ul>
                  {(nodes[line.id] || []).map((node) => (
                    <li key={node.id}>
                      <button type="button" onClick={() => selectNode(node.id)}>
                        {node.san}
                      </button>
                    </li>
                  ))}
                </ul>
              </li>
            ))}
          </ul>
        </div>
      ))}
    </div>
  );
};

export default SidebarTree;
