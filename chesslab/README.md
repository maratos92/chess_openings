# ChessLab

ChessLab is a hybrid chess opening study application that combines a Flask backend
with a React + TypeScript frontend. The backend manages openings, lines, nodes,
and evaluation data while providing both REST APIs and Socket.IO events. The
frontend presents a tree of opening lines, an interactive board, evaluation
panels, and charts.

## Getting Started

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r ../requirements.txt
python -m chesslab.backend.app
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Stockfish WASM Asset

The repository cannot ship the Stockfish WASM binary directly. Download an
official build (for example from [stockfishchess.org](https://stockfishchess.org/download/))
and place the `stockfish.wasm` file inside `frontend/src/assets/`, replacing the
placeholder file. The Vite build will bundle this local asset so the client
engine can operate without contacting external CDNs.

## Tests

Run the Python unit tests with pytest:

```bash
pytest
```
