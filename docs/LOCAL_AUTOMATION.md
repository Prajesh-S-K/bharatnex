# Local Idea-to-Checkpoint Automation

Use the signed-in local form at <http://127.0.0.1:5678/form/smart-mine-idea> for
routine, bounded implementation tasks.

## What happens automatically

1. The task is assigned to one selected workstream.
2. Ollama selects at most four relevant files using bounded repository context.
3. Git creates an isolated `automation/<task>` branch and worktree.
4. The local model writes only within the workstream allowlist.
5. Python tests, Ruff, Git whitespace checks and applicable frontend checks run.
6. At most two local repair attempts run when checks fail.
7. A checkpoint commit is created only when every check passes.
8. Execution stops before push or merge.

Open **Executions** in n8n to see the structured result, branch, worktree, changed files,
checks and next action for a submitted production-form task.

## Workstream choices

| Choice | Writable scope |
|---|---|
| `fullstack` | `apps/api/`, `apps/dashboard/`, `tests/`, `scripts/` |
| `intelligence` | `intelligence/` |
| `hardware` | `firmware/` |
| `simulator` | `simulator/` |
| `documentation` | `docs/`, `README.md` |

Contracts, automation code, GitHub configuration, secrets and other workstreams are always
blocked. Only one local coding task runs at a time.

## Good task shape

Submit one concrete outcome with acceptance conditions:

> Add API validation tests for invalid inspection unit identifiers. Preserve the frozen
> contracts and existing response shapes. Completion requires all Python tests and Ruff checks.

Do not combine unrelated features. Use hosted review for architecture, safety-sensitive logic,
contract changes or work that requires high confidence. Local model output is a draft and cannot
guarantee zero defects.

## Review a checkpoint

Use the branch and worktree paths returned in the n8n execution. Inspect the diff and rerun the
quality gate. Push or merge only after human review. Failed tasks remain uncommitted in their
isolated worktree for diagnosis and never affect the active project checkout.
