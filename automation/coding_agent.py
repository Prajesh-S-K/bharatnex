"""Constrained local coding agent used by the n8n idea workflow."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import threading
import urllib.request
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKTREES = ROOT / ".automation-worktrees"
MODEL = "qwen2.5-coder:7b"
MAX_TASK_LENGTH = 2_000
MAX_MODEL_FILES = 4
MAX_FILE_BYTES = 24_000
MAX_TOTAL_CONTEXT = 60_000
PROTECTED_PREFIXES = ("contracts/", ".github/", ".git", "automation/")
WORKSTREAM_PATHS = {
    "fullstack": ("apps/api/", "apps/dashboard/", "tests/", "scripts/"),
    "intelligence": ("intelligence/",),
    "hardware": ("firmware/",),
    "simulator": ("simulator/",),
    "documentation": ("docs/", "README.md"),
}
AGENT_LOCK = threading.Lock()


class AgentError(RuntimeError):
    """Raised when an autonomous task violates a guardrail or cannot complete."""


@dataclass(frozen=True)
class AgentTask:
    idea: str
    workstream: str
    base_ref: str = "HEAD"
    max_repairs: int = 2


def _run(command: tuple[str, ...], cwd: Path, timeout: int = 300) -> subprocess.CompletedProcess:
    return subprocess.run(
        command,
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )


def _slug(text: str) -> str:
    value = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:36]
    return value or "task"


def _is_allowed(path: str, workstream: str) -> bool:
    normalized = path.replace("\\", "/").lstrip("./")
    if not normalized or normalized.startswith("/") or ".." in Path(normalized).parts:
        return False
    if normalized.startswith(PROTECTED_PREFIXES):
        return False
    return normalized == "README.md" or normalized.startswith(WORKSTREAM_PATHS[workstream])


def _extract_json(text: str) -> dict:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", cleaned, flags=re.DOTALL)
    try:
        value = json.loads(cleaned)
    except json.JSONDecodeError as error:
        start, end = cleaned.find("{"), cleaned.rfind("}")
        if start < 0 or end <= start:
            raise AgentError("Local model did not return valid JSON") from error
        value = json.loads(cleaned[start : end + 1])
    if not isinstance(value, dict):
        raise AgentError("Local model response must be a JSON object")
    return value


def _ollama(messages: list[dict], model: str = MODEL) -> dict:
    payload = json.dumps({"model": model, "stream": False, "messages": messages}).encode()
    request = urllib.request.Request(
        "http://127.0.0.1:11434/api/chat",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=300) as response:  # noqa: S310
        result = json.load(response)
    return _extract_json(result["message"]["content"])


def _repository_files(worktree: Path, workstream: str) -> list[str]:
    result = _run(("git", "ls-files"), worktree)
    if result.returncode:
        raise AgentError(result.stderr.strip() or "Could not list repository files")
    return [path for path in result.stdout.splitlines() if _is_allowed(path, workstream)]


def _plan(task: AgentTask, worktree: Path, model_call: Callable = _ollama) -> dict:
    candidates = _repository_files(worktree, task.workstream)
    response = model_call(
        [
            {
                "role": "system",
                "content": (
                    "You are a cautious repository planner. Return JSON only with keys summary, "
                    "files_to_read (existing paths only, max 4), and acceptance_checks. "
                    "Never select contracts, automation, GitHub configuration, secrets, or "
                    "another workstream."
                ),
            },
            {
                "role": "user",
                "content": json.dumps(
                    {
                        "idea": task.idea,
                        "workstream": task.workstream,
                        "allowed_files": candidates,
                    }
                ),
            },
        ]
    )
    files = response.get("files_to_read", [])
    if not isinstance(files, list) or len(files) > MAX_MODEL_FILES:
        raise AgentError("Planner selected an invalid number of files")
    for path in files:
        if path not in candidates:
            raise AgentError(f"Planner selected a forbidden or missing path: {path}")
    return response


def _implementation(
    task: AgentTask,
    worktree: Path,
    plan: dict,
    failure_report: str = "",
    model_call: Callable = _ollama,
) -> dict:
    context = []
    total = 0
    for path in plan.get("files_to_read", []):
        content = (worktree / path).read_text(errors="replace")[:MAX_FILE_BYTES]
        total += len(content)
        if total > MAX_TOTAL_CONTEXT:
            break
        context.append({"path": path, "content": content})
    response = model_call(
        [
            {
                "role": "system",
                "content": (
                    "Implement one bounded repository task. Return JSON only: summary and files, "
                    "where files is a list of {path, content} containing complete file contents. "
                    "Use at most 4 files. Do not touch contracts, automation, CI, secrets, or "
                    "other workstreams. Preserve public interfaces and do not weaken or delete "
                    "tests."
                ),
            },
            {
                "role": "user",
                "content": json.dumps(
                    {
                        "idea": task.idea,
                        "workstream": task.workstream,
                        "plan": plan,
                        "current_files": context,
                        "previous_failure": failure_report[-8_000:],
                    }
                ),
            },
        ]
    )
    files = response.get("files", [])
    if not isinstance(files, list) or not 1 <= len(files) <= MAX_MODEL_FILES:
        raise AgentError("Implementation must contain between one and four files")
    for item in files:
        if not isinstance(item, dict) or not isinstance(item.get("content"), str):
            raise AgentError("Implementation returned an invalid file entry")
        if not _is_allowed(str(item.get("path", "")), task.workstream):
            raise AgentError(f"Implementation attempted forbidden path: {item.get('path')}")
        if len(item["content"].encode()) > MAX_FILE_BYTES:
            raise AgentError(f"Implementation file is too large: {item['path']}")
    return response


def _apply_files(worktree: Path, response: dict) -> None:
    for item in response["files"]:
        destination = (worktree / item["path"]).resolve()
        if worktree.resolve() not in destination.parents:
            raise AgentError("Resolved file path escaped the worktree")
        destination.parent.mkdir(parents=True, exist_ok=True)
        content = item["content"]
        if content and not content.endswith("\n"):
            content += "\n"
        destination.write_text(content)


def _changed_files(worktree: Path) -> list[str]:
    result = _run(("git", "status", "--porcelain"), worktree)
    if result.returncode:
        raise AgentError(result.stderr.strip())
    return [line[3:] for line in result.stdout.splitlines() if len(line) > 3]


def _validate_scope(worktree: Path, workstream: str) -> list[str]:
    changed = _changed_files(worktree)
    if not changed:
        raise AgentError("Local model produced no repository change")
    forbidden = [path for path in changed if not _is_allowed(path, workstream)]
    if forbidden:
        raise AgentError(f"Guardrail rejected changed paths: {', '.join(forbidden)}")
    return changed


def _checks(worktree: Path, workstream: str) -> dict:
    commands = [
        ("tests", (str(ROOT / ".venv/bin/python"), "-m", "pytest", "-q"), worktree),
        ("ruff", (str(ROOT / ".venv/bin/ruff"), "check", "."), worktree),
        ("format", (str(ROOT / ".venv/bin/ruff"), "format", "--check", "."), worktree),
        ("diff", ("git", "diff", "--check"), worktree),
    ]
    node_modules = worktree / "apps/dashboard/node_modules"
    if workstream == "fullstack" and (ROOT / "apps/dashboard/node_modules").exists():
        node_modules.symlink_to(ROOT / "apps/dashboard/node_modules", target_is_directory=True)
        commands.extend(
            [
                ("frontend-lint", ("npm", "run", "lint"), worktree / "apps/dashboard"),
                ("frontend-build", ("npm", "run", "build"), worktree / "apps/dashboard"),
            ]
        )
    results = []
    try:
        for name, command, cwd in commands:
            completed = _run(command, cwd)
            results.append(
                {
                    "name": name,
                    "passed": completed.returncode == 0,
                    "output": (completed.stdout + completed.stderr).strip()[-8_000:],
                }
            )
    finally:
        if node_modules.is_symlink():
            node_modules.unlink()
        shutil.rmtree(worktree / "apps/dashboard/dist", ignore_errors=True)
    return {"passed": all(item["passed"] for item in results), "results": results}


def idea_to_checkpoint(task: AgentTask, model_call: Callable = _ollama) -> dict:
    if task.workstream not in WORKSTREAM_PATHS:
        raise AgentError(f"Unknown workstream: {task.workstream}")
    if not task.idea.strip() or len(task.idea) > MAX_TASK_LENGTH:
        raise AgentError("Idea must contain 1–2000 characters")
    if not 0 <= task.max_repairs <= 2:
        raise AgentError("max_repairs must be between 0 and 2")
    if not AGENT_LOCK.acquire(blocking=False):
        raise AgentError("Another local coding task is already running")
    stamp = datetime.now(UTC).strftime("%Y%m%d-%H%M%S")
    task_id = f"{stamp}-{_slug(task.idea)}"
    branch = f"automation/{task_id}"
    worktree = WORKTREES / task_id
    try:
        WORKTREES.mkdir(exist_ok=True)
        created = _run(("git", "worktree", "add", "-b", branch, str(worktree), task.base_ref), ROOT)
        if created.returncode:
            raise AgentError(created.stderr.strip() or "Could not create isolated worktree")
        plan = _plan(task, worktree, model_call)
        failure = ""
        checks = {"passed": False, "results": []}
        implementation = {}
        for _attempt in range(task.max_repairs + 1):
            implementation = _implementation(task, worktree, plan, failure, model_call)
            _apply_files(worktree, implementation)
            changed = _validate_scope(worktree, task.workstream)
            checks = _checks(worktree, task.workstream)
            if checks["passed"]:
                break
            failure = json.dumps(checks)
        if not checks["passed"]:
            return {
                "status": "NEEDS_REVIEW",
                "task_id": task_id,
                "branch": branch,
                "worktree": str(worktree),
                "plan": plan,
                "checks": checks,
                "message": "Repair limit reached; no commit or push was made.",
            }
        _run(("git", "add", "--all"), worktree)
        committed = _run(("git", "commit", "-m", f"automation: {_slug(task.idea)}"), worktree)
        if committed.returncode:
            raise AgentError(committed.stderr.strip() or "Checkpoint commit failed")
        commit = _run(("git", "rev-parse", "HEAD"), worktree).stdout.strip()
        return {
            "status": "CHECKPOINT_READY",
            "task_id": task_id,
            "branch": branch,
            "commit": commit,
            "worktree": str(worktree),
            "changed_files": changed,
            "summary": implementation.get("summary", ""),
            "checks": checks,
            "next_action": "Human review is required. Push and merge were not performed.",
        }
    finally:
        AGENT_LOCK.release()
