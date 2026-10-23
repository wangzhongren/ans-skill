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

## Independent acceptance

The independent [acceptance role](acceptance-role.md) writes completion criteria from the confirmed planning proposal version before implementation and judges the current candidate as pass, rework, or insufficient evidence. Developers, assembly and the test role provide actual check results; an established technical-architecture worker role provides implementation-design review. The scheduler checks provenance and records/releases stages only from a matching current acceptance conclusion. It cannot accept its own dispatch, and the technical-architecture role cannot accept its own shared implementation.

A report links task/stage, criteria and design versions, candidate identity, original evidence, unresolved gaps and its reasoned conclusion. Missing or stale evidence means insufficient evidence; observed noncompliance means rework. Both remain incomplete.

Parallel evidence gathering does not change what counts as evidence. Evidence collected by an acceptance read-only evidence sub-context (E1–E4 are context numbers of the same acceptance role, not roles) counts only after the acceptance main context re-checks it against the same candidate, the same environment, the same command and the original output; a sub-context's own account is not evidence. The acceptance main context makes the sole judgment and writes the only B2; sub-contexts give no pass/fail and write nothing. Communication only relays sub-context task briefs and reports verbatim, without adding, removing or summarizing them into conclusions, and its customer summary cites only the B2 conclusion and evidence reviewed by the acceptance main context. The full rules are defined only in [acceptance parallel evidence](acceptance-parallel-evidence.md); this guide only summarizes them.

## Acceptance gates

A verified candidate requires:

- All changed paths authorized by Section 1 of the owning worker role's module boundary document, or by a built-in management role's reference default scope
- Required verification gates passed (tests, lint, type check)
- Current evidence and required documentation

Verification does not authorize commits, pushes, publication, deployment, merges, or external mutations.

## See also

- [ANS Governed Construction SKILL.md](../SKILL.md) — Governing Invariant #4, Execution Checkpoints
