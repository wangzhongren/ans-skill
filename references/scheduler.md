# Scheduling Protocol for the Default Project Role

ANS Governance defines and changes roles, ownership, and policy. The [default project role](project-role.md) owns investigation and shared design; this reference defines its scheduling responsibility under accepted definitions. Capability agents implement and test their scoped work; the assembly role verifies the connected system. Scheduler is not built in. ANS Governance creates its project role card and boundary, which must be accepted before activation. This reference is a template, not mutation authority.

## Create the Project Role

When coordinated execution is required, ANS Governance creates a role directory using the project's naming convention, for example:

```text
角色卡/调度/
  role-card.md
  boundary.md
  functional-description.md
  changelog.md
```

Use the project's default role card for investigation, design, and coordination; do not create a second coordinator merely because the directory example says 调度. The card identifies the project-specific responsibility, required reading, available execution tools, concurrency limit, and handoff protocol. Its required reading includes its own boundary, this scheduler reference, the main skill, action policy, and evidence rules. The boundary contains only Section 1; the workflow description belongs in the companion document. Configure paths and available tools from the actual project, not this example. No subagent tool or particular parallel capacity is assumed.

The project scheduler reads accepted capability/assembly cards without activating their write permissions. Its own card remains active while dispatching; each worker explicitly activates its assigned role. A standalone single-role repair may omit graph records, but activating its execution role still needs the customer-consent/configuration check in project-role.md.

## Suggested Boundary Section 1

| Operable location | Allowed use |
| --- | --- |
| `docs/scheduling/<task-id>/plan.json` | Maintain the stage-task dependency graph within existing task authorization |
| `docs/scheduling/<task-id>/state.json` | Record node state, assignments, evidence references, and execution attempts |
| `docs/scheduling/<task-id>/events.jsonl` | Append dispatch, completion, failure, invalidation, and recovery events |
| `docs/scheduling/<task-id>/board.md` | Generate the coordination table from plan/state; never maintain independent status here |

These paths are suggested entries, not a built-in whitelist. Governance must resolve them into the project scheduler's accepted Section 1 (a bounded conditional scheduling directory is allowed). These are the scheduling portion of the default project role's boundary. Its separately accepted design paths are defined under project-role.md; ownership policy and role definitions remain Governance-owned. Map `docs/` to the existing documentation root and record the resolved paths in the accepted boundary before writing. Use a stable, path-safe task ID and reuse its records on resume. Do not edit application code, tests, build configuration, role cards, boundary documents, implemented API/source contracts, skill rules, or the architecture atlas. Shared design documents may be edited only under the project role's accepted design scope. Read them as needed; reading another role card does not activate it or grant its scope.

A task plan narrows an accepted role's authority; it never grants new permission. Governance policy or ownership changes go to ANS Governance, with required user acceptance. The scheduler does not create roles or act as a second approval authority for their permissions.

## Stage-Task Execution Graph

Derive prerequisites from accepted role boundaries, integration designs, API contracts, and targeted source inspection. No whole-project code graph is needed. The scheduler maintains a separate directed acyclic graph whose nodes are **role + stage + observable deliverable**, not entire roles or source files.

Each plan node records:

1. Stable node ID, owning role, stage, objective, and role-card/boundary paths with their version or content hashes.
2. Exact task write set, required inputs, expected outputs, and checks; the write set must fit the accepted boundary and current user authorization.
3. Prerequisite node IDs and explicit release conditions: contract established, implementation available, or required verification passed. Identify the actual contract/version or candidate evidence required; a stage name alone is insufficient.
4. Completion criteria, including evidence required for this stage. All required checks must pass before the node is marked verified. A verified contract-design node does not imply a verified implementation.

For example, a shared Model contract can release independent Service preparations; Service implementations can run when their required Provider contracts/implementations are ready; final integration waits for the actual participating implementation gates. Build/test setup can be an early assembly-owned node, and end-to-end verification a later one. Cyclic role references may become acyclic stage tasks; if a real prerequisite cycle remains, block dispatch and clarify the design under the project role; route ownership or permission changes to Governance rather than deleting an edge.

## Dispatch Loop

Use [task-operations.md](task-operations.md) and its CLI for plan initialization, authorization/reservation, acknowledgment, checks, feedback, revision and verification. Invoke the actual subagent tool only after dispatch succeeds. The CLI is not itself an agent launcher.

Follow [coordination.md](coordination.md) for shared-table fields, versioned worker reports, acknowledgment, single-writer updates, and change reconciliation. Keep execution status separate from requirement/design change events.

1. **Validate the plan and authority.** Before each activation/dispatch, check customer consent or a matching customer-approved project configuration rule and record its version with the assignment; file ownership alone is insufficient. Check accepted roles, unique file ownership, write subsets, prerequisite IDs, acyclic dependencies, and concrete release criteria. Keep contract versions consistent. Route unowned files or changed authority back to Governance before dispatching the affected node.
2. **Find ready nodes.** A node is ready only when all prerequisites satisfy their recorded conditions against current evidence, its required inputs are present, and no active writer conflicts with its write set. Include supporting documents, generated outputs, shared facades, and configuration in collision checks; different role names do not prove disjoint writes.
3. **Dispatch within capacity.** Use available subagent tools to start a worker with the target role card, accepted boundary, narrowed task, input versions, expected deliverables, and checks. The scheduler is the sole dispatcher. Capability and assembly workers do not create child agents or assign work to peers; they return dependency requests to the scheduler. A graph with one ready node runs sequentially; do not create agents only for symmetry.
4. **Validate returns.** Require changed paths, final candidate identity, artifact references, exact check results, and unresolved issues. Compare actual changes to the assigned scope and verify evidence provenance before recording the node as verified. A worker saying “done” or exiting successfully is not acceptance evidence. Missing or failed checks keep the node unverified.
5. **Release dependents.** Update state and events, then reevaluate ready nodes. Assembly integration must test the final combined candidate; individually passing worker results do not prove the combined tree passes. Assign shared cross-role output generation to a single explicitly authorized execution role/stage, never let every worker write it concurrently. Do not add an atlas synchronization stage unless explicitly requested.

The same scheduler may dispatch an authorized rework stage without creating a new role. Reading broad context is permitted; executing business work while still in Scheduler is not.

## States, Failure, and Resume

Use `pending`, `ready`, `running`, `awaiting-verification`, `verified`, `failed`, `blocked`, and `cancelled` as node states. `ready` is derived from current prerequisites; `verified` is granted only for the recorded stage and candidate. Record each attempt's worker identity and reason for transition; preserve previous failure evidence.

- A failed node blocks its dependent nodes; independent authorized nodes may continue. Fixing code remains the assigned capability role's job. Retry only after identifying a changed condition or a concrete rework plan; do not blindly repeat the same failure or erase evidence.
- Contract, boundary, or relevant source changes invalidate affected results. Hold downstream dispatch, stop/reconcile affected running workers at a safe boundary, and return invalidated nodes to pending/rework. Never relabel old evidence as current by changing a hash alone.
- On resume, check actual worker status, current source/contract identities, and recorded artifacts before trusting persisted state. Do not dispatch a duplicate writer because a previous worker is slow or its status is unknown. Do not reclaim its write scope until it is stopped or confirmed finished.
- Honor user stop/cancel requests and release reservations only when writers are no longer active. Graph edges, scope checks, and evidence gates cannot be waived to make a schedule finish.
- With no subagent tools, execute the same graph sequentially: perform the same customer-consent/configuration check and explicitly switch from the project role into the selected capability role, perform the scoped stage, then switch back to Scheduler before updating its records and selecting the next stage. No role inherits the other's write authority. This is an in-task execution fallback, not a recurring automation.

## Completion and Responsibility

The scheduler owns dispatch accuracy and stage-release decisions. Each capability owner remains responsible for its implementation and evidence; assembly owns integrated verification. Governance owns permission/policy changes. None replaces user authorization.

A task is complete only when its required nodes are verified against current artifacts, integrated checks pass where required, and required documentation and coordination records are current. Cancelled or blocked required nodes mean the task is incomplete. Report completed, blocked, and pending work concisely under the role-card communication rules. Graph output remains an execution record, not proof of universal correctness.
