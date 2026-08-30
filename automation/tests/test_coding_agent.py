"""Guardrail tests for the constrained local coding agent."""

import pytest

from automation.coding_agent import (
    AgentError,
    AgentTask,
    _apply_files,
    _extract_json,
    _is_allowed,
    _slug,
)


@pytest.mark.parametrize(
    ("path", "workstream", "expected"),
    [
        ("apps/api/routes.py", "fullstack", True),
        ("tests/test_health.py", "fullstack", True),
        ("intelligence/features.py", "intelligence", True),
        ("firmware/gateway/main.cpp", "hardware", True),
        ("contracts/decision.schema.json", "fullstack", False),
        ("automation/runner.py", "fullstack", False),
        ("../outside.txt", "documentation", False),
        ("apps/api/routes.py", "intelligence", False),
    ],
)
def test_workstream_path_guard(path, workstream, expected):
    assert _is_allowed(path, workstream) is expected


def test_extract_json_accepts_fenced_object():
    assert _extract_json('```json\n{"summary": "ok"}\n```') == {"summary": "ok"}


def test_extract_json_rejects_non_object():
    with pytest.raises(AgentError):
        _extract_json("[]")


def test_task_is_immutable():
    task = AgentTask("Add a focused test", "fullstack")
    with pytest.raises(AttributeError):
        task.idea = "changed"


def test_slug_is_branch_safe_and_bounded():
    assert _slug("Add API health: fast & safe!") == "add-api-health-fast-safe"
    assert len(_slug("x" * 100)) == 36


def test_apply_files_normalizes_final_newline(tmp_path):
    _apply_files(tmp_path, {"files": [{"path": "docs/proof.md", "content": "proof"}]})
    assert (tmp_path / "docs/proof.md").read_text() == "proof\n"
