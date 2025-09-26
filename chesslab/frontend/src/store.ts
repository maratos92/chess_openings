import create from 'zustand';
import { io, Socket } from 'socket.io-client';
import { fetchOpenings, fetchLines, fetchNodes, requestEval } from './api';

type EngineMode = 'client' | 'server' | 'auto';

type EvalEntry = {
  depth: number;
  multipv: number;
  pv_uci: string | null;
  score_cp: number | null;
  bestmove_uci: string | null;
};

type Node = {
  id: number;
  line_id: number;
  parent_id: number | null;
  san: string;
  ply: number;
  fen: string;
  comment?: string;
};

type Line = {
  id: number;
  opening_id: number;
  title: string;
  is_main: boolean;
};

type Opening = {
  id: number;
  name: string;
  side: string;
};

type ChessState = {
  openings: Opening[];
  lines: Record<number, Line[]>;
  nodes: Record<number, Node[]>;
  selectedOpeningId: number | null;
  selectedLineId: number | null;
  selectedNodeId: number | null;
  evals: Record<number, EvalEntry[]>;
  engineMode: EngineMode;
  depth: number;
  multipv: number;
  socket: Socket | null;
  loadOpenings: () => Promise<void>;
  selectOpening: (openingId: number) => Promise<void>;
  selectLine: (lineId: number) => Promise<void>;
  selectNode: (nodeId: number) => void;
  ensureSocket: () => void;
  receiveEvalUpdate: (nodeId: number, entries: EvalEntry[]) => void;
  requestServerEval: (nodeId: number) => Promise<void>;
};

export const useChessStore = create<ChessState>((set, get) => ({
  openings: [],
  lines: {},
  nodes: {},
  selectedOpeningId: null,
  selectedLineId: null,
  selectedNodeId: null,
  evals: {},
  engineMode: 'client',
  depth: 12,
  multipv: 3,
  socket: null,
  loadOpenings: async () => {
    const openings = await fetchOpenings();
    set({ openings });
    if (openings.length > 0) {
      await get().selectOpening(openings[0].id);
    }
  },
  selectOpening: async (openingId: number) => {
    const openingLines = await fetchLines(openingId);
    set((state) => ({
      selectedOpeningId: openingId,
      lines: { ...state.lines, [openingId]: openingLines },
    }));
    if (openingLines.length > 0) {
      await get().selectLine(openingLines[0].id);
    }
  },
  selectLine: async (lineId: number) => {
    const lineNodes = await fetchNodes(lineId);
    set((state) => ({
      nodes: { ...state.nodes, [lineId]: lineNodes },
      selectedLineId: lineId,
      selectedNodeId: lineNodes.length ? lineNodes[lineNodes.length - 1].id : null,
    }));
  },
  selectNode: (nodeId: number) => {
    set({ selectedNodeId: nodeId });
  },
  ensureSocket: () => {
    const { socket, receiveEvalUpdate } = get();
    if (socket) {
      return;
    }
    const newSocket = io('http://localhost:5000');
    newSocket.on('eval_update', (payload: { node_id: number; evals: EvalEntry[] }) => {
      receiveEvalUpdate(payload.node_id, payload.evals);
    });
    set({ socket: newSocket });
  },
  receiveEvalUpdate: (nodeId: number, entries: EvalEntry[]) => {
    set((state) => ({
      evals: { ...state.evals, [nodeId]: entries },
    }));
  },
  requestServerEval: async (nodeId: number) => {
    const { depth, multipv, engineMode } = get();
    await requestEval({ nodeId, depth, multipv, mode: engineMode });
  },
}));
