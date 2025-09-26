import axios from 'axios';

export const apiClient = axios.create({
  baseURL: 'http://localhost:5000/api',
});

export const fetchOpenings = async () => {
  const { data } = await apiClient.get('/openings');
  return data;
};

export const fetchLines = async (openingId: number) => {
  const { data } = await apiClient.get(`/openings/${openingId}/lines`);
  return data;
};

export const fetchNodes = async (lineId: number) => {
  const { data } = await apiClient.get(`/lines/${lineId}/nodes`);
  return data;
};

export const requestEval = async (params: { nodeId: number; depth: number; multipv: number; mode: string }) => {
  const { data } = await apiClient.get('/eval', {
    params: {
      node_id: params.nodeId,
      depth: params.depth,
      multipv: params.multipv,
      mode: params.mode,
    },
  });
  return data;
};

export const postEval = async (payload: {
  nodeId: number;
  engineMode: string;
  evals: Array<{ depth: number; multipv: number; pv_uci: string; score_cp: number; bestmove_uci: string }>;
}) => {
  const { data } = await apiClient.post('/eval', {
    node_id: payload.nodeId,
    engine_mode: payload.engineMode,
    evals: payload.evals,
  });
  return data;
};
