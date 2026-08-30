# SMART-MINE AI — Current Handoff

For complete recovery, read [RECOVERY_BACKUP.md](RECOVERY_BACKUP.md).

## Current state

- Active branch: `fullstack/prototype-command-center`.
- Full Stack prototype is committed and pushed through `5a87afc`.
- The guarded local n8n automation checkpoint is tracked on this branch.
- n8n 2.32.7 is running locally at `http://127.0.0.1:5678` with persistent Docker data.
- Ollama is running locally with `qwen2.5-coder:7b`.
- The allowlisted runner is local-only at `127.0.0.1:8010`.
- n8n successfully executed the Repository Quality Gate and Local Handoff Summary workflows.
- The quality gate passed: 13 Python tests, Ruff lint/format, contracts, whitespace,
  frontend lint/build and Git diff.
- Autonomous code mutation, Git commits, pushes and merges remain disabled.

## Automation files

- `automation/docker-compose.yml`: pinned local n8n service.
- `automation/runner.py`: fixed-operation runner; no arbitrary shell interface.
- `automation/start.sh`: local startup helper.
- `automation/n8n/workflows/`: health, quality-gate and local-summary workflows.
- `automation/.env.example`: non-secret configuration template.
- `automation/.env`: ignored local secret/configuration file.

## Integration boundaries

- Frozen v1 sensor and decision contracts remain authoritative.
- n8n may report checks and summarize outputs; it may not calculate Risk/Confidence or make
  safety decisions.
- n8n has read-only repository access.
- No workflow may merge, force-push, delete tests, modify contracts or publish secrets.
- Jhasmitha's Intelligence branch remains independently owned and must not be overwritten.

## Next action

1. Open `http://127.0.0.1:5678` and complete the one-time local owner setup.
2. Keep the three corrected workflow files as the source of truth; remove the three earlier
   duplicate drafts from the n8n editor after login.
3. Run the quality workflow once from the editor.
4. Add an isolated worktree coding workflow later, with an explicit task scope and mandatory
   stop-before-merge gate.
