# Scheduling Protocol for the Default Project Role

ANS Governance defines and changes roles, ownership, and policy. The [default project role](project-role.md) owns investigation and shared design; this reference defines its scheduling responsibility under accepted definitions. Capability agents implement and unit-test their scoped work. Project management implements shared components and their tests; assembly verifies wiring/startup; the fixed test role verifies cross-role, complete-flow and regression behavior. Scheduler is not built in. ANS Governance creates its project role card and boundary, which must be accepted before activation. This reference is a template, not mutation authority.

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

If a shared Dashboard role channel is enabled, each worker may send its own scoped messages and exact permission requests using the project's shared Key while declaring its active role ID. The default project role may route questions to other roles, but neither that channel nor an administrator's recorded decision dispatches a worker. Recheck the current task, role boundary, write set and customer consent or approved configuration in `task_ops` before activation.

## Suggested Boundary Section 1

| Operable location | Allowed use |
| --- | --- |
| `docs/scheduling/<task-id>.md` | Keep one Git-readable plan, current step table and ordered task history; `task_ops` is its only writer |

These paths are suggested entries, not a built-in whitelist. Governance must resolve them into the project scheduler's accepted Section 1 (a bounded conditional scheduling directory is allowed). These are the scheduling portion of the default project role's boundary. Its separately accepted design paths are defined under project-role.md; ownership policy and role definitions remain Governance-owned. Map `docs/` to the existing documentation root and record the resolved paths in the accepted boundary before writing. Use a stable, path-safe task ID and reuse its records on resume. Scheduling permissions do not grant source permissions. Only the project role's separately accepted `common/shared/`, corresponding test and document scopes permit shared implementation. Do not edit other roles' application code/tests, build configuration, role cards, boundaries or skill rules. Shared implementation and design still need the applicable document confirmation and task authorization. Read them as needed; reading another role card does not activate it or grant its scope.

A task plan narrows an accepted role's authority; it never grants new permission. Governance policy or ownership changes go to ANS Governance, with required user acceptance. The scheduler does not create roles or act as a second approval authority for their permissions.

## Stage-Task Execution Graph

Derive prerequisites from accepted role boundaries, integration designs, API contracts, and targeted source inspection. No whole-project code graph is needed. The scheduler maintains a separate directed acyclic graph whose nodes are **role + stage + observable deliverable**, not entire roles or source files.

Each plan node records:

1. Stable node ID, owning role, stage, objective, and role-card/boundary paths with their version or content hashes.
2. Exact task write set, required inputs, expected outputs, and checks; the write set must fit the accepted boundary and current user authorization.
3. Prerequisite node IDs and explicit release conditions: contract established, implementation available, or required verification passed. Identify the actual contract/version or candidate evidence required; a stage name alone is insufficient.
4. Completion criteria, including evidence required for this stage. All required checks must pass before the node is marked verified. A verified contract-design node does not imply a verified implementation.

For example, a shared Model contract can release independent Service preparations; Service implementations can run when their required Provider contracts/implementations are ready; final integration waits for the actual participating implementation gates. Build/test setup can be an early assembly-owned node, shared implementation a project-owned node, and end-to-end verification a later test-role-owned node. Cyclic role references may become acyclic stage tasks; if a real prerequisite cycle remains, block dispatch and clarify the design under the project role; route ownership or permission changes to Governance rather than deleting an edge.

## Dispatch Loop

Use [task-operations.md](task-operations.md) and its CLI for plan initialization, authorization/reservation, acknowledgment, checks, feedback, revision and verification. Invoke the actual subagent tool only after dispatch succeeds. The CLI is not itself an agent launcher.

Choose the lowest-cost available model that can reliably do the assigned task, and specify it explicitly when the tool supports model selection. Summarizing, extracting facts and simple checks normally use a low-cost model with low reasoning effort; do not automatically inherit the main agent's model or full conversation history. Complex implementation or a critical review may need a stronger model; explain the task-specific reason rather than upgrading every worker. Respect a customer-specified model and budget. Only pass the role, boundaries and task-relevant inputs needed by that worker; comply with any tool restrictions on model overrides and history forking.

Follow [coordination.md](coordination.md) for shared-table fields, versioned worker reports, acknowledgment, single-writer updates, and change reconciliation. Keep execution status separate from requirement/design change events.

1. **Validate the plan and authority.** Before a code/test activation or dispatch, identify the relevant feature draft or dated design/change/fix proposal and the customer's confirmation plus instruction to implement that version; do not treat an invitation to ask questions as approval. Include only optional item IDs or the displayed selection actually covered by that authorization; a default checkmark does not approve extra work. Reuse a confirmation already given for the same document, scope and selection. Also check role activation consent or a matching customer-approved project configuration rule and record its version with the assignment; file ownership alone is insufficient. Check accepted roles, unique file ownership, write subsets, prerequisite IDs, acyclic dependencies, and concrete release criteria. Keep contract versions consistent. Route unowned files or changed authority back to Governance before dispatching the affected node.
2. **Find ready nodes.** A node is ready only when all prerequisites satisfy their recorded conditions against current evidence, its required inputs are present, and no active writer conflicts with its write set. Include supporting documents, generated outputs, shared facades, and configuration in collision checks; different role names do not prove disjoint writes.
3. **Dispatch within capacity.** Use available subagent tools to start a fresh independent worker context with only the target role card, accepted boundary, narrowed task, input versions, expected deliverables, and checks. Do not inherit the coordinator's full role-bearing history. Reuse a worker only for its original role. The scheduler is the sole dispatcher of execution workers. Capability and assembly workers do not create child agents or assign work to peers; they return dependency requests to the scheduler. A graph with one ready node runs sequentially in its owner's separate context; isolation is still required without parallelism.
4. **Validate returns.** Require changed paths, final candidate identity, artifact references, exact check results, and unresolved issues. Compare actual changes to the assigned scope and verify evidence provenance before recording the node as verified. A worker saying “done” or exiting successfully is not acceptance evidence. Missing or failed checks keep the node unverified.
5. **Release dependents.** Update state and events, then reevaluate ready nodes. Assembly wiring checks and test-role integration/regression checks must use the final combined candidate; individually passing worker results do not prove the combined tree passes. Assign shared cross-role output generation to a single explicitly authorized execution role/stage, never let every worker write it concurrently. Do not add an atlas synchronization stage unless explicitly requested.

The same project management role may dispatch authorized rework without creating a new role. It may implement a separately authorized shared-code stage in its own scope without pretending to switch identity; its tests and affected consumers still need current verification. Other business implementation stays with its assigned owner. Testing workers follow the same no-self-dispatch and role-activation rules as capability workers.

## States, Failure, and Resume

Use `pending`, `ready`, `running`, `awaiting-verification`, `verified`, `failed`, `blocked`, and `cancelled` as node states. `ready` is derived from current prerequisites; `verified` is granted only for the recorded stage and candidate. Record each attempt's worker identity and reason for transition; preserve previous failure evidence.

- A failed node blocks its dependent nodes; independent authorized nodes may continue. Fixes belong to the code owner: project management for shared components, the assigned capability role for business/private code. The test role reports reproducible failures to project management and retests fixes. Retry only after identifying a changed condition or a concrete rework plan; do not blindly repeat the same failure or erase evidence.
- Contract, boundary, or relevant source changes invalidate affected results. Hold downstream dispatch, stop/reconcile affected running workers at a safe boundary, and return invalidated nodes to pending/rework. Never relabel old evidence as current by changing a hash alone.
- On resume, check actual worker status, current source/contract identities, and recorded artifacts before trusting persisted state. Do not dispatch a duplicate writer because a previous worker is slow or its status is unknown. Do not reclaim its write scope until it is stopped or confirmed finished.
- Honor user stop/cancel requests and release reservations only when writers are no longer active. Graph edges, scope checks, and evidence gates cannot be waived to make a schedule finish.
- With no subagent tools or capacity, prepare scoped handoffs and execute the graph sequentially in separate contexts bound to their respective roles, under the same customer-consent/configuration checks. Results return to the existing scheduler context for record updates and stage selection. If a separate context cannot be started, keep the stage pending and report the limitation. Never switch the scheduler context into a worker role and back.

## Completion and Responsibility

The scheduler owns dispatch accuracy and stage-release decisions. Each code owner remains responsible for its implementation and unit/contract evidence; assembly owns wiring/startup checks, and the fixed test role owns independent cross-role, full-flow and regression evidence. Project management coordinates repairs and acceptance, including for its own shared-code changes. Governance owns permission/policy changes. None replaces user authorization.

A task is complete only when its required nodes are verified against current artifacts, integrated checks pass where required, and required documentation and coordination records are current. Cancelled or blocked required nodes mean the task is incomplete. Report completed, blocked, and pending work concisely under the role-card communication rules. Graph output remains an execution record, not proof of universal correctness.
