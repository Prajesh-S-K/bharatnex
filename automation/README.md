# Local n8n Automation

This folder provides a low-token, local-only automation layer for SMART-MINE AI.

## Safety boundary

- n8n binds to `127.0.0.1:5678` and is not exposed to the public network.
- The repository is mounted read-only inside n8n.
- n8n can call only the named operations exposed by `runner.py`.
- The runner does not accept arbitrary commands and cannot merge, force-push, delete tests,
  change contracts, or write source files.
- Local AI is used only for bounded summaries. It never calculates Risk/Confidence or issues
  safety decisions.

## Start

1. Start Docker Desktop and Ollama.
2. Copy `.env.example` to `.env` in this folder and set a strong runner token.
3. Run `./automation/start.sh` from the repository root.
4. Open <http://127.0.0.1:5678> and create the local n8n owner account.
5. Import the JSON files in `automation/n8n/workflows/`.
6. In n8n Credentials, create **Header Auth** named `SMART-MINE Runner Token`. Set the
   header name to `Authorization` and the value to `Bearer <AUTOMATION_RUNNER_TOKEN>`, using
   the token from the ignored `automation/.env` file. Assign it to both runner request nodes.

The runner is available only on `127.0.0.1:8010`. n8n reaches it through
`host.docker.internal`.

## Included workflows

- **SMART-MINE Prototype Health:** checks the FastAPI health and overview endpoints.
- **SMART-MINE Repository Quality Gate:** runs the fixed repository checks and returns a
  compact pass/fail report.
- **SMART-MINE Local Handoff Summary:** uses Ollama to summarize an already-produced quality
  report. It does not modify the repository.

Do not activate autonomous code-writing workflows until a dedicated worktree, task scope,
and stop-before-merge gate have been reviewed.
