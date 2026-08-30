"""Allowlisted local automation runner for n8n.

This service intentionally exposes no arbitrary command or file-write interface.
"""

from __future__ import annotations

import json
import os
import secrets
import subprocess
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOST = "127.0.0.1"
PORT = 8010
MAX_OUTPUT = 12_000

CHECKS = (
    ("python-tests", (".venv/bin/python", "-m", "pytest", "-q"), ROOT),
    ("ruff-lint", (".venv/bin/ruff", "check", "."), ROOT),
    ("ruff-format", (".venv/bin/ruff", "format", "--check", "."), ROOT),
    ("contracts", (".venv/bin/python", "scripts/validate_contracts.py"), ROOT),
    ("whitespace", (".venv/bin/python", "scripts/check_whitespace.py"), ROOT),
    ("frontend-lint", ("npm", "run", "lint"), ROOT / "apps" / "dashboard"),
    ("frontend-build", ("npm", "run", "build"), ROOT / "apps" / "dashboard"),
    ("git-diff", ("git", "diff", "--check"), ROOT),
)


def run_quality_gate() -> dict:
    started = time.monotonic()
    results = []
    for name, command, working_directory in CHECKS:
        completed = subprocess.run(
            command,
            cwd=working_directory,
            capture_output=True,
            text=True,
            timeout=180,
            check=False,
        )
        output = (completed.stdout + completed.stderr).strip()
        results.append(
            {
                "name": name,
                "passed": completed.returncode == 0,
                "exit_code": completed.returncode,
                "output": output[-MAX_OUTPUT:],
            }
        )
    return {
        "operation": "quality-gate",
        "passed": all(item["passed"] for item in results),
        "duration_seconds": round(time.monotonic() - started, 2),
        "results": results,
    }


class Handler(BaseHTTPRequestHandler):
    def _json(self, status: int, payload: dict) -> None:
        body = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/health":
            self._json(200, {"status": "ok", "service": "bharatnex-automation-runner"})
            return
        self._json(404, {"detail": "Not found"})

    def do_POST(self) -> None:  # noqa: N802
        expected = os.getenv("AUTOMATION_RUNNER_TOKEN", "")
        supplied = self.headers.get("Authorization", "").removeprefix("Bearer ")
        if not expected or not secrets.compare_digest(supplied, expected):
            self._json(401, {"detail": "Invalid automation runner token"})
            return
        if self.path == "/v1/quality-gate":
            self._json(200, run_quality_gate())
            return
        self._json(404, {"detail": "Operation not allowlisted"})

    def log_message(self, format_string: str, *args: object) -> None:
        print(f"automation-runner: {format_string % args}")


if __name__ == "__main__":
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()
