/* eslint-disable */
self.importScripts('stockfish.wasm');

self.onmessage = function (event) {
  // Placeholder worker implementation.
  // In a full implementation, this would proxy messages to the WASM engine.
  postMessage({ type: 'ready', data: event.data });
};
