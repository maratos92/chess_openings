import React, { useEffect } from 'react';
import SidebarTree from './components/SidebarTree';
import BoardView from './components/BoardView';
import EvalPanel from './components/EvalPanel';
import EvalGraph from './components/EvalGraph';
import Settings from './components/Settings';
import HoverPreview from './components/HoverPreview';
import { useChessStore } from './store';

const App: React.FC = () => {
  const { loadOpenings } = useChessStore();

  useEffect(() => {
    loadOpenings();
  }, [loadOpenings]);

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <Settings />
        <SidebarTree />
      </aside>
      <main className="main-content">
        <BoardView />
        <EvalPanel />
        <EvalGraph />
      </main>
      <HoverPreview />
    </div>
  );
};

export default App;
