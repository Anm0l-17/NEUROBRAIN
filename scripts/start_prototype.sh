#!/bin/sh
# Start the chat app (port 8766, for Open WebUI) with the v2 citation selector and the shared database.
# Needs NEUROBRAIN_CHAT_KEY set; refuses to start without the v2 model in Ollama.
set -e
cd "$(dirname "$0")/.."
ROOT=/Users/anmolkumar/Documents/MINORPROJECT-NEUROBRAIN
[ -n "$NEUROBRAIN_CHAT_KEY" ] || { echo "Set NEUROBRAIN_CHAT_KEY first."; exit 1; }
ollama list | grep -q '^neurobrain-selector-v2' || { echo "Model neurobrain-selector-v2 is missing in Ollama."; exit 1; }
NEUROBRAIN_SELECTOR_MODEL=neurobrain-selector-v2 PYTHONPATH=src exec "$ROOT/.venv/bin/python" -m neurobrain.chat_api \
  --db "$ROOT/.neurobrain/observations.sqlite3" --notes-root "$ROOT/examples/notes" "$@"
