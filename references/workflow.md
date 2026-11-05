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

For application code or tests, first write the relevant design, feature, change or fix document as a concrete proposal. Summarize the proposed behavior and limits in the chat, adding a small diagram/table only when it clarifies the decision. Start code changes only after the customer confirms that document and instructs implementation based on it; use an earlier same-version confirmation when one already exists. This document-level confirmation is separate from the two customer gates (intent and proposal) and never substitutes for them; under [the fix narrow fast path](#fix-the-narrow-fast-path-inside-confirmed-behavior), the customer's fix instruction covers the fix record while owner, scope and write set stay unchanged, so no new proposal object and no role-assignment confirmation object arises. If material findings change the proposal, revise and present the affected part before coding. Do not treat a question about the proposal as approval.

For new product requirements, Communication records the request and first confirms its understanding of the intent with the customer (gate 0: goals, scope, priorities, non-goals, already-authorized boundaries and known constraints). Only then does it start the Planning context for the product proposal, architecture design, shared business contracts and acceptance criteria. Communication obtains the customer's proposal confirmation (gate 1). Only after that does the scheduler judge the team (keep, adjust boundaries, split, add or merge) by the [five-dimension standard and decision table](scheduler.md#五维判断与决策表) and complete the team plan — which roles, who does what, and each role's scope and write set, including the assignment when the roster stays unchanged. The scheduler writes the team plan to `docs/scheduling/` and directly dispatches or starts the worker roles once the customer implementation authorization is in place; Communication records the team plan and the dispatch and notifies the customer. Role-assignment and boundary changes go through the team plan and People Operations, with no customer role-assignment confirmation card or wait. When the written plan requires new or changed roles, Communication starts the People Operations context; People Operations writes or changes role cards and boundaries only as that plan directs: the plan defines what capability is needed and what boundary it must have, and People Operations supplements the capability description and turns it into the card text. Only when the plan includes a technical-architecture worker role does that role add implementation design and technical review under the confirmed architecture. The scheduler then manages each role's task workflow and arranges authorized work with its owners; independent acceptance writes completion criteria from the same customer-confirmed planning proposal version before implementation and later judges current evidence. Only explicit customer agreement passes a gate; default checkmarks, team consensus, a finished proposal, tool success and silence are not agreement. Same-object, same-version, same-scope confirmation remains reusable, but each gate confirms its own object and version: an intent change reopens gate 0, and a material proposal change reopens gate 1. Communication is the only customer channel. Keep these responsibilities in separate fixed contexts. This is the normal new-work path; [the fix narrow fast path](#fix-the-narrow-fast-path-inside-confirmed-behavior) is the only bounded exception because it creates no new proposal object and no new role-assignment confirmation object.

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

Within an active fix, a newly discovered need to change confirmed behavior, a shared contract or the structural scope is a type-conversion event, not a scope expansion; stop and follow [Reclassification When Fix Conditions Fail](#reclassification-when-fix-conditions-fail) and the five conversions below.

## Work Types: New, Fix, Change, and Refactor

Classify the work item before choosing the construction or investigation flow. Every work item has exactly one current type: **new**, **fix**, **change**, or **refactor**. The type decides which customer gates apply and what evidence is required. This section is the single detailed source for the four types, the fix narrow fast path and the five required conversions; other skill files summarize it and link here.

### Shared Concepts

| Concept | Definition |
| --- | --- |
| **Confirmed baseline** | The proposal version the customer confirmed at gate 1 (product proposal, architecture design, shared business contracts and checkable acceptance criteria), plus the existing behavior and contracts that version explicitly requires to stay. A fix may also use an accepted current-behavior document, an existing contract or an existing test as the source of expected behavior. Drafts, unconfirmed proposals, team plans, default checkmarks, team consensus and silence are not a baseline. |
| **Defect** | The actual result departs from the confirmed baseline, the expected behavior already exists and is confirmed, and restoring it needs no new behavior, public-contract change or acceptance-criteria change. |
| **Behavior change** | User-visible behavior, public contracts, acceptance criteria or scope change, including modifying or deleting confirmed behavior, or the customer changing the original requirement. |
| **Structural change** | Internal layers, module boundaries, shared abstractions, data flow or implementation organization change while confirmed external behavior and contracts stay unchanged. |
| **New capability** | A goal, behavior or contract the confirmed baseline does not contain; it needs a new proposal, architecture, contract, file or role capability. |
| **Extension foundation** | Internal structure a completed refactor leaves in place to support later capabilities. It only says later work can be easier; it grants no new capability. |
| **Work item** | One piece of work with an explicit type, baseline, authorization, owner, scope/write set, risk tier, evidence and acceptance conclusion. A work item has one current type at a time. |
| **Type conversion** | The work item moves from one type to another. It must stop explicitly, record the trigger, reclassify and obtain the customer authorization for the new type; the old authorization does not carry over. |

### Type Definitions and Conditions

| Type | Conditions | Typical triggers | If the conditions do not hold |
| --- | --- | --- | --- |
| **New** | The customer requests a goal, behavior or contract outside the confirmed baseline; a new proposal, architecture, contract, capability or files are needed; it is not only correcting a deviation and not only restructuring internals. | Customer new requirement; a new capability proposed after a refactor; acceptance finds the original proposal never covered the customer's goal (a requirement gap, not an implementation defect). | Only existing behavior deviates → fix; modifying confirmed behavior/contract → change; only internal structure → refactor. |
| **Fix** | Expected behavior already exists in the confirmed baseline; the actual result deviates; no new behavior, public contract, architecture, role, boundary, governance or permission change; one existing owner; every affected file and test sits inside that owner's accepted Section 1; risk tier T0/T1; the customer gives an explicit fix instruction; the defect report is clear. | Customer reports a defect; acceptance finds delivery does not meet a confirmed criterion; a test finds a regression; the owner finds a defect inside confirmed behavior; a safety/data issue inside confirmed behavior. | If any condition fails → stop and reclassify by the table below; do not "fix until it passes" or widen scope while fixing. |
| **Change** | The original requirement is judged unreasonable, insufficient or outdated, or the customer asks to change/delete confirmed behavior, contracts, acceptance criteria or scope; a fix cannot solve the problem without changing the confirmed baseline. | A fix finds the original requirement unreasonable; the customer asks to change confirmed behavior; acceptance failure shows the criteria or requirement are wrong; an external contract needs adjustment. | Only an implementation defect → fix; only a structural carrying problem → refactor; an entirely new capability → new. |
| **Refactor** | The existing structure (product/process or implementation) cannot carry confirmed or proposed-to-change requirements; structural design is needed; confirmed external behavior and contracts stay unchanged by default; confirmed behavior is never changed silently. | Repeated fixes in one area remain unstable; a change proposal finds the structure cannot carry it; cross-role duplication or coupling blocks a confirmed requirement; an extension foundation is needed. | A local defect → fix; external behavior change → change; new capability → new; both behavior and structure → confirm the behavior as change/new first, then refactor the structure. |

### Decision Order

Ask in this order; the first "yes" wins:

1. **Q1: Is the work only restoring the actual result to confirmed expected behavior, without changing expected behavior, contracts, acceptance criteria or scope?** Yes → fix candidate; check the F1–F9 conditions below. All conditions hold → fix. Any condition fails → reclassify by the table below; do not continue to Q2–Q4 by guessing. No → Q2.
2. **Q2: Does the work change or delete confirmed behavior, contracts, acceptance criteria or scope, or is the original requirement judged unreasonable?** Yes → change. No → Q3.
3. **Q3: Does the work add a capability outside the confirmed baseline without changing confirmed behavior?** Yes → new. No → Q4.
4. **Q4: Does the work change only internal structure to carry confirmed or proposed-to-change requirements while keeping confirmed external behavior unchanged?** Yes → refactor. No → stop; do read-only investigation and take the question to Communication and Planning; do not implement under a guessed type.

### Who Judges What

| Judgment | Judge | Limits |
| --- | --- | --- |
| **Technical nature**: is it a defect, where is the root cause, is it inside confirmed behavior | **The owner of the affected files** | The owner reproduces read-only and judges the root cause; acceptance, tests and the customer report facts; the scheduler does not judge technical nature. Disagreement goes to Planning and the scheduler for coordination, and to the customer through Communication when needed. |
| **Whether the original requirement is reasonable** | **Planning** | The owner or acceptance supplies findings and evidence; Planning judges and writes the change proposal with reasons, impact and options; the customer decides at gate 1. Planning never declares the requirement invalid for the customer. |
| **Whether the existing structure cannot carry the work** | **Planning** for product/process structure; **project management** for implementation-level structure when the team plan established that role | Planning writes the structure proposal; project management judges implementation structure and technical contracts under the confirmed architecture; the customer confirms the structure proposal. When the project-management role does not exist, do not invent it. |
| **Ownership, routing and gate applicability** | **The scheduler** | The scheduler checks Section 1, single or cross-role ownership, the fix conditions and which gates apply; when unsure, default to the stricter normal flow and record why. It does not judge technical nature or requirement reasonableness. |
| **Problem reporting** | **Acceptance** reports failed criteria and evidence; **owner/test** report defect facts; **the customer** reports through Communication | Acceptance only reports which criterion failed and the evidence; it does not classify, expand requirements or change criteria. |
| **Customer authorization** | **The customer, recorded by Communication** | Gate 0/1 or an explicit fix instruction; no role substitutes for the customer. Default checkmarks, team consensus, a finished proposal, tool success and silence are not agreement. |
| **Records** | **Communication** records customer authorization; **the scheduler** records stop/classification/dependencies/evidence state; **owner/Planning/acceptance** write their own work records | Each role writes only inside its own Section 1; never write another role's records or fabricate authorization or conclusions. |

**Judgment boundaries:** Communication only records and relays customer intent; it does not judge technical nature or decide "is it a defect", and never dispatches a work role directly. Acceptance only judges whether the current result meets confirmed criteria; when it finds a problem it reports the trigger facts and does not reclassify, expand requirements or change criteria. The scheduler judges ownership, routing, gate applicability and the team plan; it does not judge the product or technical proposal. Planning judges requirement reasonableness and structural carrying and writes the matching proposal; it does not write implementation design, code, role definitions or scheduling records. The customer confirms gates and conversions; no role substitutes for customer agreement. No role silently changes the classification inside one task; every conversion follows the rules below.

### Triggers

A trigger only starts the judgment; it does not make the type valid. The type is valid only when its conditions hold and the judge above confirms it.

| Type | Trigger (any one starts judgment) |
| --- | --- |
| **New** | The customer proposes a new goal/behavior/contract; new capability after a refactor; a change proposal actually replaces the original product scope; acceptance finds the original proposal never covered the customer's goal (a requirement gap, not an implementation deviation). |
| **Fix** | The customer reports a defect; acceptance fails a confirmed criterion; a test finds a regression; the owner finds a defect inside confirmed behavior; confirmed behavior deviates from expectation in real use. |
| **Change** | A fix finds the original requirement unreasonable, insufficient or outdated; the customer asks to change confirmed behavior; acceptance failure shows the criteria or requirement are wrong; external contracts, regulations or dependencies require changing confirmed behavior. |
| **Refactor** | Repeated fixes in one area remain unstable (for example the same defect fails twice); a change proposal finds the existing structure cannot carry it; cross-role coupling or duplication blocks a confirmed requirement; an extension foundation is needed; maintenance cost already harms the reliability of confirmed behavior. |

### Anti-Patterns

| ID | Wrong classification | Scenario | Why it is wrong | Correct handling |
| --- | --- | --- | --- | --- |
| X1 | Treating a fix as new work | A small defect inside confirmed behavior is sent through the full gates 0/1 with a new proposal | No new behavior or contract exists; the proposal round slows the fix and can change the baseline. | If the owner confirms confirmed behavior and F1–F9 hold → fix; otherwise reclassify. |
| X2 | Treating new work as a fix | "Fix login and add SSO on the way" | The new capability is outside the baseline; the narrow fix path allows no new behavior, contract or file | Split into separate new work with gates 0/1; the original defect stays a fix. |
| X3 | Treating a change as a fix | Loosening an acceptance criterion to match the actual result, or changing code because the original requirement is wrong | Confirmed behavior or criteria changed; a fix cannot change the baseline | Stop the fix; Planning writes the change proposal; reopen gate 1. |
| X4 | Treating a fix as a change | A clear regression is sent straight to a change because it "looks complex" | No behavior change; a change proposal hides the defect and adds unnecessary process | Investigate read-only first; if it is a defect and the conditions hold → fix; otherwise change/refactor. |
| X5 | Treating a refactor as a change | Internal-only restructuring is labeled a behavior change to skip structure design and regression proof | External behavior is unchanged; a change flow is not a substitute for structure design and behavior-preservation evidence | Refactor with structure design, confirmation and regression; if behavior really changes, state it in a change proposal. |
| X6 | Treating a change as a refactor | Confirmed external behavior changes quietly inside "refactoring" | Refactoring must preserve confirmed external behavior; behavior changes need gate 1 | Stop; reclassify as change; do the refactor part separately. |
| X7 | Treating a refactor as a fix | A cross-owner or shared-contract restructuring is dispatched as a "bug fix" through the fast path | Violates single owner, no shared contract/architecture change, and T0/T1 | Stop; go through the normal change/refactor flow. |
| X8 | Treating new work as a refactor | "Do the new feature while refactoring" | A refactor only forms an extension foundation; it grants no new capability | After the refactor is accepted, do the new work through gates 0/1. |
| X9 | Treating every acceptance failure as a fix | Acceptance fails and a fix is dispatched immediately | The failure may be the requirement, the criteria or a missing capability; acceptance only reports facts | The owner judges technical nature; Planning judges requirement reasonableness; the scheduler routes by the actual type. |
| X10 | Treating "the customer said fix it" as unlimited authorization | Cleaning adjacent code, changing interfaces or adding compatibility while fixing | The fix instruction covers only the reported defect and confirmed behavior | Fix only the reported defect; adjacent work is separate and authorized by type. |

### Reclassification When Fix Conditions Fail

When the fix condition check fails, stop the fix and reclassify in this order:

| Failed condition | Reclassification |
| --- | --- |
| Needs to change confirmed behavior, contracts, acceptance criteria or scope | Change (Planning proposal, reopen gate 1) |
| Needs multiple owners, shared contracts or architecture, files outside Section 1, role/boundary/governance/permission changes, or risk T2/T3 | Refactor or change: external behavior unchanged and only structure carrying is the problem → refactor; external behavior must change → change; both → confirm behavior as change first, then refactor the structure |
| Needs a capability outside the baseline | New (full gates 0/1; the scheduler then completes the team plan; People Operations writes cards first for role/boundary changes; after customer implementation authorization the scheduler dispatches directly) |
| Only the report is unclear or the expected-behavior source is unknown | Read-only investigation first; if still unclear, ask Communication to clarify; do not implement |
| The type is genuinely disputed | Stop and record the dispute; the owner, Planning and the scheduler each give their judgment; Communication asks the customer; do not implement by guess |

Keep the current candidate, record the trigger facts and evidence, explain why the original classification fails, let the responsible judge confirm the new type, obtain the customer authorization the new type requires, keep the old authorization only for its original object/version/scope, and handle old evidence by [Evidence Invalidation Across Conversions](#evidence-invalidation-across-conversions).

### New Work

1. Communication receives the request, writes it down and obtains gate 0 intent confirmation: goals, scope, priorities, non-goals, authorized boundaries and known constraints.
2. Planning writes the product proposal, implementation plan (the same confirmed version), research plan (when needed), architecture design, shared business contracts and checkable acceptance criteria.
3. Communication starts an independent read-only review by the same Planning role; the author handles each finding and updates the version.
4. Communication presents gate 1; the confirmed version is the acceptance baseline.
5. The scheduler judges the team by the five-dimension standard and decision table and writes the team plan: roles, who does what, scope and write set, including the assignment when the roster stays unchanged. The plan is written to `docs/scheduling/`.
6. Role or boundary changes go to People Operations under the written team plan; there is no customer role-assignment confirmation card.
7. The customer gives an explicit implementation instruction; the scheduler authorizes, reserves and directly dispatches or starts the worker roles. Communication records the team plan and the dispatch and notifies the customer.
8. Owners implement, test and update feature documents and history; the fixed test role runs cross-role and full-flow tests when established.
9. Acceptance writes B1 from the same confirmed version before implementation, then B2 after it, and judges pass, rework or insufficient evidence; the scheduler releases only from a matching current pass.
10. Acceptance findings enter the new → fix conversion: first judge whether this is a defect inside confirmed behavior or a requirement/structure problem; not every failure is a fix.

**Gates:** gate 0 → gate 1, complete. After gate 1 the scheduler completes the team plan; role or boundary changes first go to People Operations under the plan; after customer implementation authorization is in place, the scheduler directly dispatches or starts the worker roles.

**Failure path:** a gate does not pass → stop at that stage; revise or terminate per the customer. A problem during implementation → convert under the conversion rules. Acceptance failure → rework or convert; never write a failure as a pass.

### Fix: the Narrow Fast Path Inside Confirmed Behavior

#### F1–F9 Conditions

All conditions must hold to use the fast path:

| ID | Condition | Checker |
| --- | --- | --- |
| F1 | Expected behavior already exists in the confirmed baseline and is traceable: a gate-1 confirmed proposal/contract, an accepted current-behavior document, an existing test or the customer's explicit defect statement. It is not new behavior and not an "add it while here" item. | Owner judges; acceptance checks the B1 source |
| F2 | The actual result deviates from the expectation, with an observable symptom or reproduction/evidence; the report is clear (see below). | Owner/reporter; acceptance checks |
| F3 | One existing owner: every affected file and test sits inside exactly one role's accepted Section 1; there is no second owner. | Scheduler checks Section 1 |
| F4 | No new or changed public contract, shared abstraction, data model, cross-role interface, architecture layer or module boundary. | Owner judges; scheduler checks |
| F5 | No new files outside Section 1; no change to roles, boundaries, governance rules or program permissions; no change to acceptance criteria. | Scheduler checks; People Operations is not involved unless a record path must be added |
| F6 | Risk tier T0 or T1 under the single definition in [testing](testing.md); no T2/T3 cross-role, contract, shared or governance/permission change. | Scheduler marks; acceptance checks |
| F7 | Communication records the defect and the customer's explicit fix instruction; the fix record or proposal is written before code changes and the customer instruction covers it (if the proposal is not yet clear, investigate read-only first, write a draft, confirm it, then change code). When the report is clear, gate 0 is satisfied in the same round. | Communication records; customer confirms; owner writes the fix record |
| F8 | The owner, scope and write set already have a written team plan assignment for the same object/version/scope, or the customer's fix instruction explicitly confirms this existing owner and range. | Scheduler checks; Communication records |
| F9 | Independent acceptance is available, writes B1 before implementation from the existing confirmed behavior/contract plus the defect record, and writes B2 afterward from the same B1; evidence, fix record, T0–T3 and optional-item rules are kept. If the project has no acceptance authorization or path, the fast path does not hold unless the customer explicitly waives it and the gap is recorded (only "implemented, not independently accepted" may be claimed). | Acceptance writes B1/B2; scheduler submits the change package; Communication records any waiver |

**If any condition fails: stop the fix, reclassify by the table above, and use the normal flow.** Do not keep fixing because work has already started.

**F8 in practice:** Communication writes the intended owner, scope and write set into the fix-intent record; the customer confirming that record and instructing the fix in the same round counts as confirming that existing owner and range. If the customer only says "fix it" without the record naming owner/scope, or the range exceeds the confirmed assignment, F8 fails; use the normal flow or ask the customer to clarify.

**Fix-record path precondition:** F7 requires the owner to be able to write a fix record or proposal. If the owner has no authorized fix-record path, the fast path does not hold. A separate boundary-governance step first adds an exact path or bounded directory under the team plan, or the record is written into an existing authorized owner document with the gap disclosed; never change code first and backfill the record, and never write an unauthorized path.

#### Clear Report and Same-Round Gate 0

The report must state:

1. **Symptom**: what the user or system actually sees, at which entry or path.
2. **Expected behavior and source**: what should happen and which confirmed proposal/contract, current-behavior document, existing test or explicit customer statement it comes from.
3. **Actual result**: the difference from the expectation, preferably with reproduction steps, inputs, logs or evidence.
4. **Known impact**: affected files/modules/roles; if unknown, say "owner to investigate read-only".
5. **Scope and non-goals**: what this fix covers and what it does not; no new behavior, interface change or adjacent cleanup.
6. **Explicit customer fix instruction**: "please fix" or "fix it this way", not "take a look" or "investigate".

Communication writes these into the fix-intent record. **Clear report + explicit customer fix instruction → gate 0 is satisfied in the same round**; no separate intent-confirmation round is needed. If the report is unclear, the customer only asks for investigation, or the expected-behavior source is unknown, gate 0 is not satisfied; read-only investigation may proceed, but the fix may not.

#### Process

1. **Report and record.** The customer reports through Communication; acceptance/tests/owners report facts to the scheduler, which sends customer decisions through Communication. Communication writes the fix-intent record (the six items above) and confirms the explicit fix instruction.
2. **Scheduler verification.** Communication has checked F7 (explicit instruction, clear report); the owner checks F1/F2 (expected behavior is in the baseline, actual result deviates); acceptance checks F9 (independent acceptance is available); the scheduler checks F3–F6 and F8 against Section 1: single owner, all files/tests in boundary, no shared contract/architecture/role/boundary/governance/permission change, risk T0/T1, existing assignment or customer instruction covering this owner and range.
3. **Triage.** All F1–F9 hold → the scheduler records the task in `docs/scheduling/` (defect, owner, scope, risk tier, customer instruction, acceptance requirement) and dispatches the original owner directly. Any condition fails → stop, record, reclassify by the table above, use the normal flow.
4. **Fix and record.** The owner reproduces read-only, confirms the root cause and writes the fix record or proposal before changing code: symptoms, expected behavior and source, root cause, planned fix behavior, scope and regression scenarios. If the customer's fix instruction already covers that record/proposal, document-level confirmation is complete in the same round; if the proposal is not yet clear, investigate read-only, write a draft, have Communication confirm it with the customer, then change code. Then fix inside Section 1, run the affected tests and submit raw evidence: candidate, command, environment, exit code, results and untested items.
5. **Independent acceptance.** Acceptance writes B1 before implementation (or at fix start) from the existing confirmed behavior/contract plus the defect record. After the fix, it judges each B1 line as pass, fail, insufficient evidence or not applicable (with a basis for not applicable) and gives the B2 overall conclusion: pass, rework or insufficient evidence. Acceptance does not treat the defect record as a new requirement and does not expand the criteria.
6. **Release or rework.** The scheduler releases only from a matching current pass conclusion. Rework goes back to the original owner. If the same defect fails two fixes, or the fix discovers an unreasonable requirement, a structural problem or a cross-boundary need, stop, record and convert under the five conversions; do not blindly try a third time.
7. **Documentation.** The owner updates feature documents and history from the actual result; the fix record links the defect, root cause, fix and regression evidence.

**The fast path does not:** write a Planning proposal, write a team plan, use gate 1, or create a new role-assignment confirmation object; it also does not involve People Operations (unless a fix-record path must be added). It still requires the customer instruction, the owner's boundary, a fix record, evidence, risk tier, optional-item rules and independent acceptance.

#### Why Gate 1 Is Skipped and No New Assignment Object Arises

- **Gate 1's object is a new product proposal, architecture or acceptance standard.** A fix produces no new proposal: expected behavior is already in the confirmed baseline, and the fix only restores the actual result to it. There is no new gate 1 object. If a fix needed new behavior, contracts or criteria, it would not be a fix; reclassify as change/new.
- **Role assignment is no longer a customer gate.** After gate 1 the scheduler completes the team plan; People Operations writes cards first when roles or boundaries change; after customer implementation authorization is in place, the scheduler directly dispatches or starts the worker roles, and Communication records the plan and dispatch and notifies the customer. A fix reuses one existing owner, and all files/tests are inside that owner's accepted Section 1; the owner, scope and write set are not new or changed, so no new assignment object arises and nothing waits for a customer confirmation. The customer's fix instruction confirms this fix. If a fix needed a new owner, scope, file or role/boundary change, it would not be a narrow fix; use the normal flow.
- **This does not delete gates.** New work, changes and refactors still use their gates; a fix only reuses existing confirmations when there is no new object. Gate 0 remains, satisfied in the same round by the defect record plus the explicit fix instruction.

#### Acceptance and Rework

- **B1 source**: existing confirmed behavior/contract plus the defect record; not a new gate-1 proposal. B1 states the defect, expectation, actual result, reproduction, fix scope, regression scenarios and evidence requirements.
- **Document-level confirmation**: the fix record or proposal is written before code; if the customer's fix instruction covers it, document-level confirmation is complete in the same round. If the proposal is unclear, investigate read-only, write a draft, ask the customer, then change code. Document-level confirmation is not gate 1; the narrow fix path creates no new proposal object and no new role-assignment confirmation object.
- **B1 line judgment**: pass / fail / insufficient evidence / not applicable (with a basis for not applicable).
- **B2 overall conclusion**: pass, rework or insufficient evidence; the three-value standard does not change.
- **Evidence**: candidate hash/version, changed paths, command, environment, exit code, test results and untested items; same candidate, inputs/dependencies and command may reuse evidence; candidate, dependency or contract changes invalidate affected evidence.
- **Rework**: back to the original owner. Two failed fixes → stop and reclassify. Never delete tests, loosen assertions, hide errors or widen scope to "fix until it passes". "Two failures" means two different fix candidates for the same defect are both judged rework by B2, or two consecutive insufficient-evidence conclusions under the same B1 with no way to complete the evidence; the scheduler records it and hands the question of change/refactor to Planning/the owner.
- **Optional items**: extra compatibility, fallbacks or extensions during a fix stay separate from the necessary fix, with an ID, benefit, cost and pending status; a default checkmark is not approval; unselected items are not implemented.
- **Acceptance gap**: if the project has no independent acceptance authorization or path, continue only after the customer explicitly waives it and the gap is recorded; the fix may only be marked "implemented, not independently accepted", never "acceptance passed".

### Change

1. **Stop the current channel explicitly.** If the change comes from a fix, an acceptance failure or a refactor, stop the current work, keep the candidate and record the trigger facts: what was found, which criterion/evidence, the current candidate and why the original classification fails.
2. **Reopen gate 0 when needed.** When intent or scope materially changes, Communication rewrites the intent understanding and obtains customer confirmation; if the customer already explicitly requested this change, record it in the same round but still state goals, scope, non-goals, boundaries and constraints.
3. **Planning writes the change proposal**: why the original requirement is unreasonable, insufficient or outdated; which confirmed behavior, contracts, acceptance criteria or scope change; affected roles/files/evidence; migration/rollback; options and risks; the new checkable completion criteria. A research plan comes first when investigation is needed.
4. **The same Planning role performs an independent read-only review; the author handles each finding.**
5. **Gate 1.** Communication presents the change-proposal version; the customer confirms it; the confirmed version becomes the new acceptance baseline.
6. **Scheduler team plan, then People Operations.** The scheduler writes the new team plan (roles, scope, write set) to `docs/scheduling/`; role/boundary changes first go to People Operations under the written plan. An existing confirmation for the exact same object/version/scope may be reused, but a change proposal usually changes scope/write set, so the old plan does not automatically carry over.
7. **Implementation authorization and dispatch.** The customer gives an explicit implementation instruction; after that authorization is in place, the scheduler authorizes and reserves each role's scope and directly dispatches or starts the worker roles. Communication records the team plan and dispatch and notifies the customer.
8. **Implement, test, update documents; acceptance writes B1 from the new version before implementation and B2 from the same version afterward.**
9. **Old evidence is invalidated.** Old evidence related to the changed behavior/contracts/candidate is invalid; unaffected evidence that still matches the current candidate may be reused under [testing](testing.md).
10. **A structural problem found during the change** → enter the change → refactor conversion; do not change and refactor at the same time.

**Gates:** gate 0 (reopen when intent/scope changes) → gate 1 (must reopen) → the scheduler's new team plan → People Operations for role/boundary changes → customer implementation authorization → the scheduler's direct dispatch or start.

**Key constraint:** a change returns to the Planning proposal and reopens gate 1; it is never written as a fix record, and a fix is never used to change acceptance criteria.

### Refactor

1. **Stop the current channel explicitly.** Record the trigger facts: where the existing structure cannot carry the work, which confirmed or proposed-to-change requirements are affected, the current candidate and why fix/change is insufficient.
2. **Structural design.** Planning writes the product/process structure proposal: current structural problem, target structure, layers/modules/calls/data flow, preserved confirmed external behavior and contracts, migration/rollback, verification points and affected roles. Project management, when established, writes implementation-level structure design, technical contracts and shared-code impact under the confirmed architecture; when not established, do not invent the role. The structure proposal must state that confirmed external behavior and contracts do not change by default; any behavior that will change is listed separately and handled as change/new, never hidden inside a refactor.
3. **Independent review.** The Planning structure proposal is reviewed under [planning proposal review](planning-proposal-review.md); implementation-level proposals are reviewed under [proposal review](proposal-review.md) (project management when established; otherwise the scheduler checks against the confirmed proposal).
4. **Customer confirmation, layered.** R1: the structure proposal changes the Planning architecture, shared contracts or acceptance criteria (while preserving confirmed external behavior) → reopen gate 1 (reopen gate 0 first if intent/scope changes). R2: only implementation structure changes inside the confirmed architecture/contracts, with no change to confirmed external behavior, contracts, acceptance criteria or role/boundary → document-level confirmation: the owner/project management presents the structure design to the customer and obtains the instruction to implement; this is not gate 1. R3: role, boundary or write-set changes → the scheduler's team plan and People Operations; adding or widening role authority still needs the customer's explicit agreement recorded by Communication. R4: the structure proposal would change confirmed external behavior → this is not a pure refactor; reclassify as change/new and do the refactor part separately.
5. **Team plan, then People Operations.** The scheduler writes the team plan (roles, scope, write set) to `docs/scheduling/`; role/boundary changes first go to People Operations under the written plan.
6. **Implementation authorization and dispatch.** The customer gives an explicit implementation instruction; after that authorization is in place, the scheduler authorizes and reserves each role and directly dispatches or starts the worker roles. Communication records the team plan and dispatch and notifies the customer.
7. **Implementation and regression.** Implement per the structure proposal; run affected tests and regression to prove confirmed external behavior/contracts are preserved; retest affected callers; shared structure or cross-role changes use T3 full regression.
8. **Acceptance.** Acceptance writes B1 from the confirmed structure proposal plus the confirmed external behavior/contracts it must preserve, and B2 afterward from the same version; evidence covers structure constraints, regression and valid reuse of unaffected evidence.
9. **A hidden defect exposed during the refactor** → enter refactor → fix; **an extension foundation formed** → record it as a foundation only, with no new-capability authorization.
10. **The structure proposal cannot preserve external behavior** → stop and reclassify as change/new; never change behavior silently.

**Gates:** structure-proposal confirmation (R1 gate 1; R2 document-level confirmation) + the scheduler's team plan → People Operations for role/boundary changes → customer implementation authorization → the scheduler's direct dispatch or start; preserving confirmed external behavior is the default constraint.

### Gates by Work Type

| Type | Gate 0 | Gate 1 | People Operations | Independent acceptance |
| --- | --- | --- | --- | --- |
| **New** | Required | Required | On role/boundary change; after gate 1 the scheduler writes the team plan, People Operations writes cards first for role/boundary changes, and after customer implementation authorization the scheduler dispatches directly | Required (B1/B2) |
| **Fix** | Same-round defect record + explicit customer fix instruction | Skipped (no new proposal object) | Not involved (unless a fix-record path is added); no new assignment object arises | Required (B1 from existing baseline + defect record) |
| **Change** | Reopened when intent/scope materially changes | Must reopen | On role/boundary change; the scheduler then writes the new team plan, People Operations writes cards first for role/boundary changes, and after customer implementation authorization the scheduler dispatches directly (same object/version/scope may be reused) | Required (new version) |
| **Refactor** | Reopened when intent/scope changes | Required when the structure proposal changes Planning architecture/contracts/acceptance criteria; pure implementation structure uses document-level confirmation; changing confirmed external behavior reclassifies as change/new | On role/boundary change; the scheduler then writes the team plan, People Operations writes cards first for role/boundary changes, and after customer implementation authorization the scheduler dispatches directly | Required (structure proposal + preserved external behavior) |

**Note:** "Skipped" applies only to the fix narrow path with all conditions met; it does not mean "all small edits skip". New work, changes and refactors still confirm under the normal rules; after gate 1 the scheduler completes the team plan; People Operations writes cards first when roles or boundaries change, and after customer implementation authorization the scheduler dispatches directly, with no customer role-assignment confirmation. The fix path is the only bounded exception.

### Risk, Evidence, and Rework

| Type | Risk tier | Acceptance baseline | Rework and re-verification |
| --- | --- | --- | --- |
| **New** | T0–T3 under [testing](testing.md); governance/permission or shared abstraction is T3 | The same gate-1 confirmed proposal version (product + architecture + contracts + criteria) | Acceptance failure goes to the original owner; a material proposal change reopens gate 1; affected evidence is invalid |
| **Fix** | **Only T0/T1**; pure documentation without governance/permission is T0; local implementation is T1; T2/T3 does not use the fast path | Existing confirmed behavior/contract plus the defect record; not a new gate-1 proposal | Fix by the same owner; re-verify affected paths; same candidate/inputs/dependencies/command evidence may be reused; two failures or a requirement/structure problem → reclassify |
| **Change** | T0–T3; behavior/contract changes are usually T2; governance/permission is T3 | The new gate-1 confirmed change-proposal version | Rework under the new proposal; old behavior evidence is invalid; unaffected parts may be reused |
| **Refactor** | T2/T3; shared structure, cross-role or governance change is T3 | The customer-confirmed structure proposal + the confirmed external behavior/contracts preserved by default | Regression proves external behavior is preserved; hidden defects are fixes; scope growth reclassifies; affected caller evidence is invalid |

**Unified rules:**

- Risk tiers add no second definition; the single T0–T3 definition remains in [testing](testing.md). The four types only map to it.
- Evidence invalidation follows whether the candidate, inputs, dependencies, contracts or confirmed version changed; affected evidence must rerun, unaffected evidence may be reused under [testing](testing.md).
- Independent acceptance judges only the same customer-confirmed proposal/defect baseline; it never invents criteria, adds requirements or turns rework into a pass.
- Optional-item rules are not relaxed by the fix fast path: necessary fixes stay separate from recommended optional items; a default checkmark is only a recommendation; unselected items are not implemented.

## The Five Required Conversions

### General Rules

1. **Stop explicitly.** Every conversion first stops the current channel and keeps the current candidate; never rename the type while continuing, and never widen scope silently inside one task.
2. **Record the trigger facts.** State what was found, which criterion/evidence, the current candidate and why the original classification fails.
3. **Reclassify.** The judge from "Who Judges What" confirms the new type; the executor does not declare it alone.
4. **Obtain the matching customer authorization.** A fix's defect instruction, a change's gate 1, a refactor's structure confirmation, the team plan and People Operations for role/boundary changes, or the full gates 0/1 for new work. Old authorization never covers a new type.
5. **Two records.** Communication records customer authorization in `docs/communication/`; the scheduler records the stop, trigger facts, old/new type, dependencies and evidence state in `docs/scheduling/`. Neither record alone is enough to continue.
6. **Old authorization stays with its object.** It remains valid only for its original object/version/scope; a new type needs new authorization. Same-object, same-version, same-scope confirmation may be reused, but one type's confirmation is never treated as another's.
7. **Old evidence is invalidated or reused by impact.** See [Evidence Invalidation Across Conversions](#evidence-invalidation-across-conversions).
8. **No silent expansion.** The new type must not bring in unauthorized new behavior, contracts, files, roles, boundaries or permissions.
9. **No "do it first and record later".** Conversion records and customer authorization are complete before continuing implementation.
10. **The five conversions are the customer-required chain, not an exhaustive list.** Other type changes follow the same general rules; an unlisted conversion is not permission for a silent conversion.

### New to Fix

| Item | Content |
| --- | --- |
| **Trigger** | Acceptance fails a gate-1 confirmed criterion, or tests/owner find the delivery does not meet confirmed behavior; expected behavior is already in the baseline and needs no new behavior. |
| **Stop point** | Stop the "new work complete" conclusion and further functional work on affected paths; keep the current candidate; the new work item stays incomplete. |
| **Proposer/judge** | Acceptance reports the failed criterion and evidence; the owner judges technical nature (inside confirmed behavior?); the scheduler verifies ownership and fix conditions and records the conversion; if conditions fail, Planning judges change/refactor/new. |
| **Customer authorization** | Explicit customer fix instruction; a clear report satisfies gate 0 in the same round. All narrow conditions hold → gate 1 skipped and no new role-assignment object arises; any condition fails → normal flow for the new type. |
| **Records** | Communication fix record + conversion record; scheduler stop/reclassification/task record; acceptance B1/B2; owner fix record. |
| **Old authorization/evidence** | The original gate-1 proposal is still the expected-behavior baseline; the original team plan remains valid for the same owner/scope; affected-path old evidence is invalid, unaffected evidence may be reused; the new work is not complete until the fix passes. |
| **No silent expansion** | Do not treat "acceptance failed" as "we may add new features"; do not treat missing requirement coverage as a fix; do not change acceptance criteria or widen scope during the fix. |

### Fix to Change

| Item | Content |
| --- | --- |
| **Trigger** | A fix finds the original requirement unreasonable, insufficient or outdated; or the only feasible fix changes confirmed behavior/contracts/acceptance criteria; or the customer asks to change behavior. |
| **Stop point** | Stop the fix immediately, keep the fix candidate, write nothing further as a fix, and record the trigger facts and evidence. |
| **Proposer/judge** | The owner presents findings and evidence; Planning judges whether this is a requirement/architecture change and writes the change proposal; the scheduler stops the channel and records it; Communication obtains customer authorization. |
| **Customer authorization** | Reopen gate 0 when intent/scope changes; reopen gate 1 for the change proposal; the scheduler then writes the new team plan; role/boundary changes first go to People Operations under the plan; after customer implementation authorization is in place, the scheduler directly dispatches or starts the worker roles. |
| **Records** | Communication trigger facts + gate records; Planning change proposal + review record; scheduler stop/conversion/team plan; the original fix record stays as trigger evidence; acceptance records are invalidated/re-judged. |
| **Old authorization/evidence** | The fix instruction and defect record stay as history but no longer authorize implementation; the old fix candidate and affected evidence are invalid; unaffected baseline evidence may be reused; after the change proposal is confirmed, the new version governs. |
| **No silent expansion** | Do not use "the original requirement is unreasonable" to skip gate 1; do not change requirements while fixing; do not append a change as a note to a fix record; do not use fix authorization to implement a change. |

### Change to Refactor

| Item | Content |
| --- | --- |
| **Trigger** | The change proposal or implementation finds the existing structure cannot carry the changed requirement; structural design is needed; the change's behavior goal still holds. |
| **Stop point** | Stop change implementation on affected paths; keep the change candidate; the change proposal stays as input to the refactor but does not authorize the refactor. |
| **Proposer/judge** | Planning judges product/process structure; project management (when established) judges implementation structure and technical contracts; the scheduler judges team, dependencies and stages; the customer confirms the structure proposal. |
| **Customer authorization** | A structure proposal that changes Planning architecture/contracts/acceptance criteria (while preserving confirmed external behavior) → gate 1; pure implementation structure → document-level confirmation; the scheduler's team plan for the team assignment; role/boundary changes → People Operations first; customer implementation authorization → the scheduler's direct dispatch or start; intent/scope changes → gate 0; changing confirmed external behavior → not a pure refactor; reclassify as change/new. |
| **Records** | Communication structure confirmation/gate records; Planning/project management structure proposal + review; scheduler stop/conversion/team plan/regression arrangement; acceptance structure baseline. |
| **Old authorization/evidence** | Still-valid confirmed behavior requirements in the change proposal remain as input; change-implementation old evidence is invalid for the refactor path; the refactor confirmation does not automatically confirm unconfirmed behavior from the change; unaffected evidence may be reused. |
| **No silent expansion** | Do not change the post-change behavior quietly through the refactor; do not treat "structural rewrite" as change implementation; do not skip regression proof; do not implement unauthorized new capabilities inside the refactor. |

### Refactor to Fix

| Item | Content |
| --- | --- |
| **Trigger** | A refactor exposes a hidden defect: actual behavior departs from confirmed behavior or from the behavior the refactor promised to preserve; the defect is inside confirmed behavior and the fix conditions hold. |
| **Stop point** | Stop refactor work on affected paths; keep the candidate; the refactor work item stays incomplete; record the defect, evidence and impact. |
| **Proposer/judge** | The owner/acceptance/tests report facts; the owner judges technical nature; the scheduler verifies single owner, Section 1, no shared contract/architecture change and risk T0/T1; if the fix needs structural change or crosses boundaries, continue the refactor or convert to change/new; do not use the narrow fix. |
| **Customer authorization** | Explicit customer fix instruction; a clear report satisfies gate 0 in the same round; narrow conditions hold → gate 1 skipped and no new role-assignment object arises; otherwise normal flow for the new type. |
| **Records** | Communication fix record + conversion record; scheduler stop/classification/refactor state; owner fix record; acceptance B1/B2; refactor regression evidence updated. |
| **Old authorization/evidence** | The refactor structure confirmation remains valid; the fix baseline is confirmed external behavior/contracts; affected-path old evidence is invalid; unaffected refactor evidence may be reused; the refactor is not complete until the fix passes. |
| **No silent expansion** | Do not use a "hidden defect" to widen the refactor; do not turn a fix into a behavior change; do not skip fix conditions or acceptance because "the refactor already started". |

### Refactor to New

| Item | Content |
| --- | --- |
| **Trigger** | The refactor completes and forms an extension foundation that can support a new capability; the customer proposes or confirms a new capability requirement. |
| **Stop point** | Stop at the extension foundation; do not treat refactor completion as new-capability authorization; record the foundation, supported capability range and limits. |
| **Proposer/judge** | The customer proposes the new requirement; Planning judges new vs change; the scheduler judges the team; acceptance judges by the new-work standard. |
| **Customer authorization** | Full new-work gates 0/1: the customer confirms intent and proposal; the scheduler then completes the team plan; People Operations writes cards first for role/boundary changes; after customer implementation authorization is in place, the scheduler directly dispatches or starts the worker roles. The refactor's structure confirmation cannot replace the new proposal confirmation. |
| **Records** | Communication new gate 0/1 records; Planning new proposal + review; scheduler new team plan; acceptance new B1/B2; refactor records linked as baseline and history. |
| **Old authorization/evidence** | The refactor confirmation authorizes only the refactor, not new behavior; the verified refactor baseline/evidence may be reused as current-behavior and regression baseline; the new capability needs its own proposal, criteria and evidence. |
| **No silent expansion** | Do not say "the extension foundation means the customer already agreed to the new feature"; do not implement new behavior inside the refactor; do not use the refactor's gate-1 confirmation in place of the new work's gate 1. |

### Evidence Invalidation Across Conversions

| Conversion | Invalid old evidence | Reusable old evidence | Old authorization |
| --- | --- | --- | --- |
| New → fix | Implementation, test and acceptance evidence related to the failed criterion/defect path | Evidence for unaffected paths with the same candidate/inputs/dependencies/command | The original gate 1 and team plan remain valid for the same baseline/owner/scope; the fix follows the new instruction |
| Fix → change | The fix candidate and evidence related to the changed behavior/contracts | Unaffected baseline evidence and checks that still match the current candidate | The fix authorization does not cover the change; the change needs gates 0/1 and a new team plan |
| Change → refactor | Change-implementation evidence related to the refactor path | Behavior requirements still confirmed in the change proposal; unaffected baseline evidence | The change authorization does not cover the refactor; the refactor needs structure confirmation and the scheduler's team plan |
| Refactor → fix | Regression evidence for the affected refactor path | Unaffected refactor evidence and the preserved confirmed-behavior baseline | The refactor confirmation remains valid; the fix follows the customer instruction |
| Refactor → new | Evidence that did not cover the new capability | The refactor baseline and verified current-behavior/regression evidence | The refactor confirmation does not cover new work; new work needs full gates 0/1 and the team plan |

**General invalidation rule:** a change to the candidate, inputs, dependencies, contracts or customer-confirmed version invalidates affected evidence; unaffected evidence that still proves it matches the current candidate may be reused; when impact cannot be bounded, treat all evidence as invalid and collect it again.

## Contracts Between Roles

The four work types cross Communication, Planning, the scheduler, People Operations, acceptance and owners. These contracts state what roles must guarantee; they do not prescribe implementation.

| ID | Contract | Provider | Consumer | Content | Failure semantics |
| --- | --- | --- | --- | --- | --- |
| C-1 | **Work-item record** | Communication (customer authorization) + scheduler (scheduling record) | All roles | Each work item records type, baseline version, customer-authorization reference, owner, scope/write set, risk tier, state, evidence and acceptance conclusion; one current type at a time | Missing type/authorization/owner → stop, no dispatch; an unrecorded type change counts as no conversion |
| C-2 | **Defect record** | Communication | Scheduler, owner, acceptance | Symptom, expected behavior and source, actual result, reproduction/evidence, impact, scope/non-goals, explicit customer fix instruction, whether the report is clear | Missing expected source → not a fix; missing customer instruction → gate 0 unmet; missing reproduction → read-only investigation first |
| C-3 | **Fix acceptance baseline** | Acceptance | Scheduler, owner, Communication | B1 derives from existing confirmed behavior/contracts + the defect record, with no new criteria; B1 lines are pass/fail/insufficient evidence/not applicable; B2 is pass/rework/insufficient evidence | If the defect record cannot produce criteria → return to Communication/Planning; acceptance does not invent criteria |
| C-4 | **Change/refactor proposal** | Planning (+ project management when established) | Scheduler, acceptance, owner | Problem, why the original requirement is unreasonable or the structure insufficient, what changes, what is preserved, affected roles/files/evidence, migration/rollback, risks, verification, options | Missing "preserved external behavior" or impact analysis → do not submit to gate 1/structure confirmation |
| C-5 | **Conversion record** | Scheduler (scheduling record) + Communication (customer authorization) | All roles | Stop point, trigger facts, old type, new type, why the old type fails, dependencies, evidence state, customer authorization | Missing any record → do not continue the new type |
| C-6 | **Evidence validity** | Scheduler (change package) + acceptance (judgment) | All roles | Candidate/input/dependency/contract/confirmed-version changes invalidate affected evidence; unaffected evidence may be reused; if impact cannot be bounded, all evidence is invalid | Evidence that cannot prove it matches the current candidate is unusable |
| C-7 | **Dispatch** | Scheduler | Owner, Communication, acceptance | Dispatch only after authorization, scope, dependencies and write-conflict checks pass; a fix goes to the original owner; Communication never dispatches; owners return evidence to the scheduler | Missing authorization/conflict → no dispatch; direct dispatch by Communication is a governance violation |
| C-8 | **Optional items** | Planning/owner | Customer through Communication | Required changes stay separate from recommended options; each option has an ID, benefit, cost, default recommendation and pending status; only customer-selected options are implemented | Default checkmarks/silence are not approval; unselected items are not implemented |

## Stop Conditions

Stop and ask for direction when:

- the smallest valid solution requires changing a protected or frozen artifact without authorization;
- two materially different scope expansions would produce different public behavior;
- required evidence would mutate an external or production system without authorization;
- the trusted baseline cannot be distinguished from conflicting user changes;
- the only apparent way to pass is to weaken a contract, test, permission, or governance rule; or
- required verification repeatedly fails for a cause outside the authorized scope.

When stopped, preserve the current candidate, state the exact failed invariant or missing authority, and propose the smallest decision needed from the user.
