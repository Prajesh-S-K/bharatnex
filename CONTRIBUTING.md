# Collaboration guide

## Working independently

- Work only inside your owned area unless coordinating a shared change.
- Do not rename contract fields locally. Propose changes in a dedicated contract pull request.
- Keep pull requests small and tied to one issue or integration checkpoint.
- Never commit secrets, Wi-Fi credentials, generated databases, trained model binaries, or dependency folders.
- Preserve the simulator as a fallback even after hardware integration.

## Branch names

- `fullstack/<feature>`
- `ai/<feature>`
- `iot/<feature>`
- `shared/<contract-or-doc-change>`
- `fix/<short-description>`

## Commit style

Use concise commits such as:

```text
feat(api): accept v1 sensor readings
feat(ai): calculate separate risk and confidence
feat(iot): send Node A heartbeat
test(simulator): add gradual deformation scenario
docs(shared): clarify warning transition
```

## Pull-request checklist

- Scope belongs to the branch/workstream.
- Tests or repeatable verification steps are included.
- Shared contracts remain compatible, or all three teams approved the change.
- Failure behaviour is documented.
- No unsupported safety or prediction claims were added.
- Relevant documentation is updated.

## Integration order

1. Simulator packet passes JSON Schema validation.
2. API accepts, validates, and stores the packet.
3. Intelligence consumes a stored/validated packet and returns a decision.
4. Dashboard renders contract-compatible API responses.
5. Wokwi nodes replace the simulator without backend changes.
6. Physical nodes replace Wokwi without contract changes.

