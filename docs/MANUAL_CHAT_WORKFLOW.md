# Manual chat-guided workflow

This is the default operating mode while the team develops manually with guidance from the planning chats.

The repository remains the source of truth, but contributors do not need to manage a heavy process for every small edit. Work in short checkpoints, show the result, get it reviewed, then commit.

## The simple loop

```text
Ask what to do
    ↓
Receive one small task
    ↓
Make the change manually
    ↓
Run the requested check
    ↓
Paste code/output into the relevant chat
    ↓
Correct mistakes
    ↓
Commit and push the completed checkpoint
    ↓
Update recovery backup/handoff
```

Do not start several modules at once. Finish one clean boundary before requesting the next task.

## Where each conversation is used

- **Analyze Full Stack Work:** Full Stack questions, commands, errors and progress.
- **Recall Full Stack Chat:** Intelligence/AI review, team-wide planning and recovered decisions.
- **Implementation/Codex task:** synchronization, repository audit, difficult corrections, integration and recovery-document updates.

When planning chats disagree, stop and use `sync and continue` here. Repository contracts and approved user decisions win over older chat suggestions.

## What contributors send for review

Use this compact format:

```text
Name:
Workstream:
Branch:
Checkpoint:

Changed files:
- ...

What now works:
- ...

Commands/tests run:
- command → PASS/FAIL

Problems or assumptions:
- ...

Commit/PR link (if available):
```

Attach only the files that were changed. Do not send copied contracts unless the task is specifically a contract change.

## Git made simple

Each workstream keeps one active branch until its current checkpoint is complete:

- Full Stack: `fullstack/checkpoint-2-ingestion`
- Intelligence: `ai/feature-extraction`
- Hardware/IoT: `iot/node-gateway-baseline`

Use additional branches only when two people would otherwise edit the same files. Contributors should never push directly to `main`.

At a checkpoint:

1. Confirm tests/checks pass.
2. Commit with a clear message.
3. Push the branch.
4. Open one pull request for the completed checkpoint.
5. Merge only after review and GitHub checks pass.

## Required checks—not process overhead

Automated quality checks stay enabled because they prevent silent integration problems. A contributor does not need to understand every tool immediately; they only need to paste the failure output into the appropriate chat and correct it before merging.

Minimum check before a Python commit:

```text
.venv/bin/ruff check .
.venv/bin/ruff format --check .
.venv/bin/python -m pytest
```

Hardware/Wokwi work must additionally show the emitted JSON packet and confirm that it matches the frozen sensor schema.

## Backup rule

The backup is updated after:

- `sync and continue`;
- an accepted architecture or contract decision;
- a completed or blocked checkpoint;
- a merged pull request;
- a workstream handoff;
- a discovered mistake that affects recovery or the next step.

Casual questions and temporary debugging attempts do not each need a backup entry. Their accepted outcome does.

Files to keep current:

- `docs/RECOVERY_BACKUP.md` — complete recovery context and history.
- `docs/CURRENT_HANDOFF.md` — concise current state and exact next action.

## Current manual sequence

1. Review and merge Full Stack FS-01.
2. Full Stack builds FS-02: frozen Pydantic input model and `POST /api/v1/readings` validation.
3. Jhasmitha finishes feature extraction with the root schema and proper tests.
4. Simulator produces valid, invalid and gradual-deformation packets.
5. Hardware produces the same packet from Wokwi Node A/B.
6. Integrate only after each boundary passes independently.

