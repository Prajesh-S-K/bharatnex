#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
AUTOMATION_DIR="$ROOT_DIR/automation"
ENV_FILE="$AUTOMATION_DIR/.env"

if [[ ! -f "$ENV_FILE" ]]; then
  cp "$AUTOMATION_DIR/.env.example" "$ENV_FILE"
  TOKEN="$(openssl rand -hex 32)"
  sed -i '' "s/replace-with-a-long-random-value/$TOKEN/" "$ENV_FILE"
fi

set -a
source "$ENV_FILE"
set +a

if ! curl -fsS http://127.0.0.1:11434/api/tags >/dev/null; then
  echo "Ollama is not running. Start the Ollama app, then run this script again."
  exit 1
fi

if ! ollama list | awk 'NR > 1 {print $1}' | grep -Fxq "$OLLAMA_MODEL"; then
  echo "Ollama model $OLLAMA_MODEL is not installed. Run: ollama pull $OLLAMA_MODEL"
  exit 1
fi

if ! curl -fsS http://127.0.0.1:8010/health >/dev/null; then
  nohup "$ROOT_DIR/.venv/bin/python" -m automation.runner \
    >"$AUTOMATION_DIR/runner.log" 2>&1 &
  echo $! >"$AUTOMATION_DIR/runner.pid"
fi

docker compose --env-file "$ENV_FILE" -f "$AUTOMATION_DIR/docker-compose.yml" up -d
echo "n8n: http://127.0.0.1:5678"
echo "Runner: http://127.0.0.1:8010/health"
