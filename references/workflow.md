# Construction and Investigation Workflow

Use with [SKILL.md](../SKILL.md) and its task-specific loading routes. These rules retain the global mutation and architectural boundaries.

Apply [Action selection](action-policy.md) before choosing execution scope or requesting input: establish existing authority, resolve material uncertainty, choose the smallest effective action, and provide concise feedback. Existing authorization remains valid; do not repeat confirmation merely because a task reaches its next implementation step.

## Runtime Role Architecture

These hard rules apply to every task:

1. The customer-facing context loads only Communication and never switches to another role for the whole session.
2. Communication starts Planning, People Operations, Scheduler and Independent Acceptance in separate subagent contexts when their work is needed. Each handoff passes only the role, its boundary or built-in default scope, the authorization, task inputs and delivery requirements; never the Communication conversation for replay.
3. Development, test, assembly and project-management worker roles are dispatched only by the Scheduler. Communication never assigns work to, authorizes, or starts a worker role. The Scheduler is the sole dispatch gateway for worker roles.
4. Never switch roles inside one context, and never let Communication bypass the Scheduler to assign work to a worker role.

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
  acceptance_condition: <criteria derived from the confirmed planning proposal version; checked by independent acceptance>
```

Rules for deriving the contract:

- Prefer specific files when the repair locus is known.
- A directory scope authorizes only changes relevant to the objective; it is not permission for opportunistic cleanup.
- Tests, fixtures, schemas, lockfiles, snapshots, and generated outputs are separate mutation targets. Include them only when the task requires them.
- Required design, feature, change, and fix documents are explicit mutation targets; include stable docs/feature/ paths and applicable dated design/change/fix paths and documentation completion in the contract.
- Reading a file, depending on a component, or discovering a defect does not add it to the write set.
- If the user explicitly names an allowed or forbidden target, preserve that boundary.

## Execute Scoped Mutation

For application code or tests, first write the relevant design, feature, change or fix document as a concrete proposal. Summarize the proposed behavior and limits in the chat, adding a small diagram/table only when it clarifies the decision. Start code changes only after the customer confirms that document and instructs implementation based on it; use an earlier same-version confirmation when one already exists. This document-level confirmation is separate from the three workflow gates and never substitutes for the role-assignment confirmation (gate 2). If material findings change the proposal, revise and present the affected part before coding. Do not treat a question about the proposal as approval.

For new product requirements, Communication records the request and first confirms its understanding of the intent with the customer (gate 0: goals, scope, priorities, non-goals, already-authorized boundaries and known constraints). Only then does it start the Planning context for the product proposal, architecture design, shared business contracts and acceptance criteria. Communication obtains the customer's proposal confirmation (gate 1). Only after that does the scheduler judge the team (keep, adjust boundaries, split, add or merge) by the [five-dimension standard and decision table](scheduler.md#五维判断与决策表) and complete the team plan — which roles, who does what, and each role's scope and write set, including the assignment when the roster stays unchanged. Communication obtains the customer's role-assignment confirmation (gate 2); role-assignment and boundary changes are confirmed at this gate. When the confirmed plan requires new or changed roles, the scheduler writes it to `docs/scheduling/`, and Communication starts the People Operations context; People Operations writes or changes role cards and boundaries only as that plan directs: the plan defines what capability is needed and what boundary it must have, and People Operations supplements the capability description and turns it into the card text. Only when the plan includes a technical-architecture worker role does that role add implementation design and technical review under the confirmed architecture. The scheduler then manages each role's task workflow and arranges authorized work with its owners; independent acceptance writes completion criteria from the same customer-confirmed planning proposal version before implementation and later judges current evidence. Only explicit customer agreement passes a gate; default checkmarks, team consensus, a finished proposal and silence are not agreement. Same-object, same-version, same-scope confirmation remains reusable, but each gate confirms its own object and version: an intent change reopens gate 0, a material proposal change reopens gate 1, and a role-assignment change reopens gate 2. Communication is the only customer channel. Keep these responsibilities in separate fixed contexts.

Implement the smallest coherent candidate that satisfies the objective and architectural contracts.

- Preserve public behavior outside the requested change unless a contract change is authorized.
- Prefer changing the failure-local artifact over changing callers, dependencies, or shared abstractions merely to accommodate the candidate.
- Do not perform unrelated cleanup, renaming, formatting, dependency upgrades, or architectural migration.
- Do not modify generated or vendored files directly when an authoritative generator or source exists.
- Preserve user changes and reconcile with them rather than overwriting them.
- Treat a newly discovered need to change an out-of-scope artifact as a scope-expansion event, not as an implementation detail.

### Scope Expansion

First check whether the user's existing authorization already covers the additional work. If it does, update the task-local contract and continue within that authority. The conditions below govern expansion beyond the established scope, not repeated approval of an already authorized outcome.

A task-local write set may grow without a new permission request only when the additional artifact is directly necessary, already covered by this role's accepted Section 1 and existing customer authorization, and introduces no changed public contract, protected artifact, governance policy or external effect. Record the narrowed assignment and changes as appropriate.

A file outside accepted Section 1 remains read-only even when its repair is reversible. Send a precise ownership/scope request to the scheduler for People Operations handling; do not use this workflow to authorize yourself. Reuse valid existing authorization rather than asking twice.

## Stop Conditions

Stop and ask for direction when:

- the smallest valid solution requires changing a protected or frozen artifact without authorization;
- two materially different scope expansions would produce different public behavior;
- required evidence would mutate an external or production system without authorization;
- the trusted baseline cannot be distinguished from conflicting user changes;
- the only apparent way to pass is to weaken a contract, test, permission, or governance rule; or
- required verification repeatedly fails for a cause outside the authorized scope.

When stopped, preserve the current candidate, state the exact failed invariant or missing authority, and propose the smallest decision needed from the user.
