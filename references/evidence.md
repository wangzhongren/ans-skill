# Evidence and Acceptance

## What counts as evidence

Evidence is the key code or key configuration that supports a conclusion.

In practice:

| Claim | Evidence |
|---|---|
| A bug is fixed | The diff that fixes it + the test that would have caught it |
| A module is safe to refactor | Existing test coverage + interface contract definitions |
| A boundary document's Section 1 is complete | A project file tree listing confirming no file is omitted |
| A dependency upgrade is backward-compatible | The changed import paths + passing downstream tests |
| A design decision is validated | The decision record + the specific runtime observation that motivated it |

## Evidence provenance (Governing Invariant #4)

Validation evidence is meaningful only for the exact candidate, environment, inputs, and policy that produced it. If any of these changes, the evidence becomes stale and must be re-collected.

## Acceptance gates

A verified candidate requires:

- All changed paths authorized by Section 1 of the relevant module boundary document
- Required verification gates passed (tests, lint, type check)
- Current evidence and required documentation

Verification does not authorize commits, pushes, publication, deployment, merges, or external mutations.

## See also

- [ANS Governed Construction SKILL.md](../SKILL.md) — Governing Invariant #4, Execution Checkpoints
