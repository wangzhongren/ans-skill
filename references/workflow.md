# Construction and Investigation Workflow

Use with [SKILL.md](../SKILL.md) and its task-specific loading routes. These rules retain the global mutation and architectural boundaries.

Apply [Action selection](action-policy.md) before choosing execution scope or requesting input: establish existing authority, resolve material uncertainty, choose the smallest effective action, and provide concise feedback. Existing authorization remains valid; do not repeat confirmation merely because a task reaches its next implementation step.

### Design Bottom-Up; Investigate Top-Down

For construction, reason about contracts and implement the required capabilities in this order:

```text
Model -> Provider -> Service -> Pipeline -> Interface
```

Start from the requested outcome, then define or reuse Model concepts and invariants, Provider capabilities, and Service operations before composing them in Pipeline and adapting them in Interface. At each of Model, Provider, and Service, explicitly assess the abstraction boundary before writing concrete code: what stable concept or contract is shared, what varies, whether an existing abstraction fits, and whether composition or a narrow contract is enough. Use the relevant layer reference for this decision. Abstract thinking does not require inheritance, multiple current implementations, or a new abstract class for every file; avoid speculative generalization. For non-obvious choices, briefly record the rationale in the task update or existing design notes rather than creating mandatory metadata.

Apply this order only to the affected work. Inspect and reuse satisfactory lower layers without editing them. Discoveries may require revisiting an earlier design decision within the Mutation Contract; the order neither authorizes a full-stack rewrite nor makes frozen dependencies editable. This is a construction order, not a runtime call direction; Model remains globally shared.

For investigation, start from the reported user-visible entry or highest relevant failing boundary and trace downward:

```text
Interface -> Pipeline -> Service -> Provider -> external infrastructure
```

Follow the actual failing path one boundary at a time, comparing inputs, outputs, errors, and contract expectations to locate the first divergence. Inspect the relevant shared Model contract wherever data validity is in question; Model is not a mandatory final step. If the report starts at Service or Provider, begin at that boundary and inspect callers as needed for context. Do not guess a lower-layer cause or patch dependencies merely because an upper layer reports an error. Once localized, repair only the authorized locus, construct changed dependencies before their callers where needed, and verify the original failing path plus affected dependents.

## Establish the Trusted Baseline

Before editing:

1. Read repository instructions and inspect the current version-control state.
2. Treat pre-existing user changes as part of the working baseline unless the user says otherwise.
3. Identify the target requirement or failure, the smallest plausible repair locus, direct callers and dependencies, relevant contracts, and available validation commands.
   Search existing shared capabilities for a compatible implementation before planning new helpers or abstractions.
   Apply the [responsibility decision table](architecture.md) to each requested behavior: identify existing capabilities to invoke unchanged, existing responsibilities to modify, and new responsibilities needing their own owner. Then check the connecting call edges against layer rules. Keep these two assessments separate; they may remain concise and internal when obvious.
4. Identify artifacts that are explicitly protected, frozen, generated, vendored, signed, or owned by another workflow.
5. Distinguish observations from assumptions. Resolve material uncertainty through read-only inspection. Ask the user only when a wrong assumption would materially alter the authorized change.

Global inspection does not imply global write permission.

## Create a Mutation Contract

Before the first edit, establish a task-local Mutation Contract. It may be stated in a concise progress update or maintained internally when the scope is obvious. Make it explicit to the user when the task is risky, spans architectural boundaries, or requires a non-obvious assumption.

Use this logical form:

```yaml
mutation_contract:
  objective: <observable requested outcome>
  baseline: <current working state or revision when known>
  allowed_write_set:
    - <specific files or the narrowest justified directories>
  protected_set:
    - <frozen, unrelated, generated, vendored, or user-owned artifacts>
  permitted_capabilities:
    - <providers, tools, effects, or architectural dependencies allowed>
  forbidden_operations:
    - <scope-relevant destructive or policy-weakening actions>
  static_gate:
    - <structural checks that must pass>
  dynamic_gate:
    - <tests or execution evidence required>
  acceptance_condition: <what makes the candidate acceptable>
```

Rules for deriving the contract:

- Prefer specific files when the repair locus is known.
- A directory scope authorizes only changes relevant to the objective; it is not permission for opportunistic cleanup.
- Tests, fixtures, schemas, lockfiles, snapshots, and generated outputs are separate mutation targets. Include them only when the task requires them.
- Required design, feature, change, and fix documents are explicit mutation targets; include their dated `docs/` paths and documentation completion in the contract.
- Reading a file, depending on a component, or discovering a defect does not add it to the write set.
- If the user explicitly names an allowed or forbidden target, preserve that boundary.

## Execute Scoped Mutation

Implement the smallest coherent candidate that satisfies the objective and architectural contracts.

- Preserve public behavior outside the requested change unless a contract change is authorized.
- Prefer changing the failure-local artifact over changing callers, dependencies, or shared abstractions merely to accommodate the candidate.
- Do not perform unrelated cleanup, renaming, formatting, dependency upgrades, or architectural migration.
- Do not modify generated or vendored files directly when an authoritative generator or source exists.
- Preserve user changes and reconcile with them rather than overwriting them.
- Treat a newly discovered need to change an out-of-scope artifact as a scope-expansion event, not as an implementation detail.

### Scope Expansion

First check whether the user's existing authorization already covers the additional work. If it does, update the task-local contract and continue within that authority. The conditions below govern expansion beyond the established scope, not repeated approval of an already authorized outcome.

Expand the allowed write set without pausing only when all of the following are true:

1. the additional artifact is directly necessary for the requested outcome;
2. the change is reversible and within the user's existing authority;
3. it does not alter a public contract, governance policy, frozen artifact, external system, or unrelated subsystem; and
4. the expansion is reported to the user.

Otherwise stop before editing that artifact and request authorization. Explain the dependency, the smallest additional scope, and the consequence of declining it.

## Stop Conditions

Stop and ask for direction when:

- the smallest valid solution requires changing a protected or frozen artifact without authorization;
- two materially different scope expansions would produce different public behavior;
- required evidence would mutate an external or production system without authorization;
- the trusted baseline cannot be distinguished from conflicting user changes;
- the only apparent way to pass is to weaken a contract, test, permission, or governance rule; or
- required verification repeatedly fails for a cause outside the authorized scope.

When stopped, preserve the current candidate, state the exact failed invariant or missing authority, and propose the smallest decision needed from the user.
