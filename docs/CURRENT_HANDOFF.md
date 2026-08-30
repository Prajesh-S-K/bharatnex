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
- The published Idea-to-Checkpoint form is available at
  `http://127.0.0.1:5678/form/smart-mine-idea` for signed-in n8n users.
- Its first documentation-only proof created isolated branch
  `automation/20260830-033046-create-docs-automation-proof-md-with` at commit `cfe493b` and
  stopped without push or merge.
- The quality gate passed: 13 Python tests, Ruff lint/format, contracts, whitespace,
  frontend lint/build and Git diff.
- Constrained code mutation and checkpoint commits are enabled only inside isolated worktrees.
  Push and merge remain disabled.

## Automation files

- `automation/docker-compose.yml`: pinned local n8n service.
- `automation/runner.py`: fixed-operation runner; no arbitrary shell interface.
- `automation/start.sh`: local startup helper.
- `automation/n8n/workflows/`: health, quality-gate and local-summary workflows.
- `automation/coding_agent.py`: bounded Ollama planner/implementer and repair loop.
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

1. Use the protected task form for one bounded task at a time.
2. Review the returned worktree diff and tests before any push.
3. Keep contracts, safety logic and cross-workstream changes under explicit human review.
