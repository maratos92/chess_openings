import React from 'react';
import { useChessStore } from '../store';

const Settings: React.FC = () => {
  const { engineMode, depth, multipv } = useChessStore();

  return (
    <div className="settings-panel">
      <h4>Engine Settings</h4>
      <div>Mode: {engineMode}</div>
      <div>Depth: {depth}</div>
      <div>MultiPV: {multipv}</div>
    </div>
  );
};

export default Settings;
