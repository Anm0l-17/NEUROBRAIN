#!/bin/sh
# Start the chat app (port 8766, for Open WebUI) with the citation selector and the shared database.
# Needs NEUROBRAIN_CHAT_KEY set. The selector is NEUROBRAIN_SELECTOR_MODEL (default
# neurobrain-selector-v2); refuses to start if Ollama does not have it.
set -e
cd "$(dirname "$0")/.."
ROOT=/Users/anmolkumar/Documents/MINORPROJECT-NEUROBRAIN
[ -n "$NEUROBRAIN_CHAT_KEY" ] || { echo "Set NEUROBRAIN_CHAT_KEY first."; exit 1; }
M=${NEUROBRAIN_SELECTOR_MODEL:-neurobrain-selector-v2}
case $M in *:*) TAGGED=$M ;; *) TAGGED=$M:latest ;; esac
L=$(ollama list 2>/dev/null) || { echo "Ollama is not running. Open the Ollama app first."; exit 1; }
echo "$L" | awk 'NR>1{print $1}' | grep -qxF "$TAGGED" || { echo "Model $M is missing in Ollama."; exit 1; }
NEUROBRAIN_SELECTOR_MODEL=$M PYTHONPATH=src exec "$ROOT/.venv/bin/python" -m neurobrain.chat_api \
  --db "$ROOT/.neurobrain/observations.sqlite3" --notes-root "$ROOT/examples/notes" "$@"
