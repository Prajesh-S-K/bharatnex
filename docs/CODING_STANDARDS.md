# Coding and review standards

These rules apply to Full Stack, Agentic AI + ML/LLM, Hardware + IoT and shared QA work.

## Daily workflow

1. Pull the latest `main` before creating a branch.
2. Use the documented branch prefix for your workstream.
3. Keep one issue and one clear outcome per branch.
4. Commit small, working changes using the repository commit style.
5. Run relevant tests and contract validation before opening a pull request.
6. Request review from the owners of affected folders.
7. Merge only after checks pass and review feedback is resolved.
8. Delete the feature branch after merge.

Do not develop directly on `main` after the collaboration phase begins.

## General code rules

- Prefer small modules with one responsibility.
- Use descriptive names; avoid unexplained abbreviations.
- Keep configuration and thresholds in one documented location.
- Add types at service and workstream boundaries.
- Validate external input immediately.
- Return explicit errors; never silently convert invalid/missing data into safe values.
- Log state changes and failures without logging credentials or sensitive data.
- Remove dead/commented-out code before review.
- Document why a non-obvious decision exists, not what an obvious line does.
- Add tests for normal behaviour, boundary cases and expected failure behaviour.

## Shared-contract discipline

- Never rename or reinterpret contract fields inside one workstream.
- Contract changes require a dedicated pull request and review from all affected owners.
- Preserve backwards compatibility within v1 when practical.
- Add or update a valid example for every schema change.
- Update the recovery backup whenever a contract or architecture decision changes.

## Full Stack

- API routes handle transport; business and intelligence logic live in services/packages.
- Database access is isolated behind repositories/services.
- The frontend consumes API decisions and does not recreate Risk or Confidence logic.
- Components must show loading, error, offline and empty states.
- Never expose secrets in browser code or committed environment files.

## Agentic AI + ML/LLM

- Record feature definitions, units, model version and training-data provenance.
- Make deterministic scoring and state transitions independently testable.
- Keep Risk and Confidence separate.
- Do not describe Isolation Forest output as collapse prediction.
- LLM text cannot override measurements, scores, states or safety actions.
- Fix random seeds in repeatable tests and synthetic-data generation.

## Hardware + IoT

- Keep Node A/B firmware shared and select identity through configuration.
- Document pins, units, sampling rates and calibration constants.
- Use non-blocking timing for sensing, heartbeat and communication where practical.
- Validate sensor ranges and report health explicitly.
- Keep Wi-Fi credentials in ignored local headers or environment tooling.
- Preserve sequence numbers and the exact v1 packet structure.

## Pull-request size and review

A pull request should usually be small enough to review in one sitting. If it mixes a contract change, feature implementation and broad refactor, split it. Reviewers should check correctness, contract compatibility, failure handling, tests, security and documentation—not only whether the code runs once.

## Required local checks

```text
python -m pip install -r requirements-dev.txt
ruff check .
ruff format --check .
python scripts/validate_contracts.py
python scripts/check_whitespace.py
pytest
git diff --check
```

GitHub runs the same core checks for every pull request and push to `main`.
