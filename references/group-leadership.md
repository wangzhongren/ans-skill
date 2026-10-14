# Group Leadership and Workload Review

A group lead is an added coordination duty held by an existing project role. It does not create a new role or change the role's identity, permissions, or fixed context. Record the group's name in `group` / `组别` and the duty in ordinary Markdown as `groupDuty` / `组内职责：组长／组员`. These are documentation fields, not CLI authorization fields.

## Assigning the Duty

Use accepted project role definitions to count group members, not the number of currently running agent contexts. Starting several contexts bound to one `roleId` does not add members or create another lead.

Each group has one lead. A group with one accepted role defaults to that role as lead. When a member joins, keep the existing lead. Governance changes an existing role's `groupDuty` only when effective customer authorization or an explicitly approved configuration covers that change. If a multi-role group has no clear lead or has conflicting lead definitions, project management resolves the ownership question; no role claims the position. This does not stop other work already approved and arranged by project management.

The lead continues its own business work. It may organize only the group's authorized tasks: arrange a group meeting, split approved work, select an eligible member, start that member in a separate context, and gather progress and evidence. Members keep their own fixed role contexts. Ordinary members do not assign work to peers, and a lead never acts as another role, edits a member's files, or changes a member's authorization.

## Group and Project Responsibilities

Project management receives new requests and assesses the affected groups' current tasks, remaining work, available members, dependencies, and blockers. It asks the relevant lead for observed progress and constraints. Unknown effort remains “to assess”; do not invent estimates or create a workload database. Do not require a meeting for every small request.

Project management handles cross-group work, acceptance, global dependencies, and stage records. A group lead handles coordination inside its group after project management has assigned and authorized that work. Requests to add a role, change ownership, or widen a write scope go to project management and Governance. Group membership does not grant write authority over another role's private `common/`, Model definitions, public contracts, or `common/shared/`; existing owners and layer rules remain in force.

When more capacity is needed, project management may propose an additional peer role. State its business responsibility, exact non-overlapping boundary, separation from current roles, handoff and verification plan, expected benefit, and cost. A proposal or lead's title grants no permission. Before requesting new customer authorization, check whether existing consent or explicitly approved configuration covers the exact role definition and boundary change. If it does not, request authorization. Governance creates or maintains the role definitions only within that authorization. The new role follows the usual implementation proposal confirmation and task authorization rules before implementation.

## Two-Level Task Dispatch

A lead may split and organize only work already assigned to the group. Before starting a member, check that the exact role has customer authorization or applicable approved preauthorization, the relevant implementation document has customer confirmation and an explicit instruction to implement, the role's own boundary covers the write set, dependencies are ready, and no active writer overlaps. A group lead cannot waive any check or send a member across group boundaries.

With `task_ops`, project management or a trusted operator first uses the existing coordinator flow to authorize each exact `roleId` and reserve its scope. `groupDuty` and ordinary agent child/parent structure are not CLI fields and do not authorize group execution. Only after that succeeds may the group lead start the named independent member context, or project management may start it using the lead's plan. The coordinator token remains with project management or the trusted operator. Each worker token goes only to its designated execution context; a group lead receives no token for another member. If the lead is itself the assigned worker, it may use only its own worker token. The trusted launcher provides each token directly to its designated context. Project management remains the sole writer of global task records and the only role that records global verification.

Without `task_ops`, follow the same per-role authorization, customer-confirmed implementation document plus explicit instruction to implement, boundary, dependency, conflict, and context-isolation rules. Do not simulate approval or use a parent/child agent arrangement to inherit permissions. When a required check is missing, keep the stage pending.

## Meetings and Reports

The project-management role hosts project-wide and cross-group meetings. A group lead hosts a group-only meeting when the task calls for discussion. Each host stays in its fixed role context; participants contribute from their own fixed contexts and do not gain write permission from discussion. Do not hold a meeting for every small request.

The actual host may write minutes only in its own accepted `docs/meetings/` scope. If that scope is absent, keep a chat draft and route a scope request through Governance. Meeting consensus is a recommendation, not customer authorization to change code, tests, roles, or boundaries.

Members send actual progress, failures, blockers, changed paths, and evidence to their group lead for group coordination. The lead forwards the original evidence with a concise summary to project management. Do not alter or omit failures. The test role's report remains its own evidence; a lead must not edit it. Project management alone updates the global task record and reports project-wide status.

See [role cards](role-card.md), [project management](project-role.md), [scheduling](scheduler.md), [meetings](meeting.md), [task operations](task-operations.md), and [coordination records](coordination.md).
