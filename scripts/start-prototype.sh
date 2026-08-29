#!/usr/bin/env bash
set -euo pipefail

repo_dir="$(cd "$(dirname "$0")/.." && pwd)"

cd "$repo_dir"
.venv/bin/uvicorn apps.api.main:app --host 127.0.0.1 --port 8000 &
api_pid=$!
trap 'kill "$api_pid" 2>/dev/null || true' EXIT INT TERM

cd "$repo_dir/apps/dashboard"
npm run dev -- --host 127.0.0.1
