# Default Project Management Role: Design, Shared Code, and Coordination

ANS Governance creates this project-local role and its boundary during bootstrap. After acceptance, it is the default role in the main conversation. It is not another built-in role. The project's existing scheduler role may be extended into this role through an accepted boundary update rather than creating two competing coordinators. Scheduling is one responsibility of this role; [scheduler.md](scheduler.md) defines the dispatch mechanics.

Its role card still includes a system-feature ownership list. Usually this list says `暂无`: investigation, design and dispatch are role duties, not business features. Only list a system feature here if the project role truly is its primary owner and the accepted boundary covers that ownership; do not assign a feature to this role merely to avoid an empty list.

## Responsibilities and Write Scope

1. Investigate across the project by reading code, logs, role definitions, tests, and integration contracts. Reading another role's files or card does not activate that role or grant write access.
2. Write architecture, abstraction, and inter-role integration design documents within the accepted design-document scope. Define responsibilities, proposed contracts, dependencies, and verification requirements.
   Each role maintains its own architecture JSON; read the task-relevant definitions and public references rather than requiring another project-understanding index.
3. Arrange all cross-role work: identify owners, agree interfaces, order tasks, dispatch authorized roles and check current evidence. Workers return cross-role needs here rather than assigning or editing each other's work.
4. Implement and maintain the accepted `common/shared/` directory, its dedicated tests and the shared-component document under [shared-directories.md](shared-directories.md). This is its only application-code scope. Own common abstractions in its architecture JSON and link consumers by ID. Follow the same document confirmation, implementation authorization, testing and evidence requirements as other code owners; coordination authority alone is not implementation approval.
5. Do not modify other roles' business code, private common code or caller tests, nor layer contract source, Model definitions, build configuration or permission configuration. Arrange those changes with their owners. Role cards and mutation boundaries remain Governance-owned.

Governance must resolve design/documentation paths, bounded scheduling paths, `common/shared/` and its corresponding test directory into this role's Section 1. For example, use `src/common/shared/`, `test/<project-role-id>/shared/` and `<existing-doc-root>/architecture/shared-components.md`. Existing cards do not gain these permissions automatically; Governance first submits the boundary update for acceptance. Do not treat a design assignment as permission to change all project Markdown files.

## Deliver the Local Architecture Page

Follow [role-architecture-viewer.md](role-architecture-viewer.md). After role architecture changes and at task delivery, run the shared Skill renderer against the actual project, write the offline HTML only to the accepted document-output scope, open it and give its link. Each role owns its JSON facts; the project role combines them without editing peers' JSON or inventing missing abstractions. No drawing role or server is needed. The old [Dashboard](dashboard.md), cloud facilities and project-context tools are used only when the user requests them. Do not require parallel content.json or SQLite understanding records.

## Own the Inter-Role Integration Design

The project role writes the shared design before dependent roles implement it, using dated records such as `docs/design/YYYY-MM-DD_design_order-export-integration.md` under the project's accepted documentation root. Explain the reason, process and key choices using the [design document guide](documentation-design.md); use [common documentation rules](documentation.md) for location and dates. Link the document from participating roles' work assignments; changes to their role cards are handled by Governance.

Present a short chat summary and, when it helps, a small diagram or comparison table. Invite the customer to ask about the design. The project role dispatches code implementation only after the customer confirms the relevant document and instructs implementation from it; an earlier confirmation for the same version and scope still counts. A question about the design alone does not activate workers or grant code-writing authority.

Each integration design identifies:

| Required content | What to specify |
| --- | --- |
| Identity and readiness | Stable contract ID, design revision/hash, draft or accepted design state, and the actual authorization/acceptance evidence; do not self-declare customer acceptance |
| Participants and ownership | Caller role, provider role, shared Model owner, and the files/entries affected; proposed new ownership is not already granted |
| Permitted call path | Architectural layer of each caller and callee, public entry points, and the Pipeline that composes independent Services |
| Inputs and outputs | Field meanings, types, units, optional/default values, validation, and shared Model references |
| Failure and lifecycle | Error semantics, relevant timeout/retry/idempotency rules, resource ownership, startup/readiness/shutdown, and ordering or concurrency requirements when applicable |
| Delivery and verification | Prerequisite contract/implementation stages, compatibility expectations, representative success and failure cases, and the owning role for each contract/integration test |

Do not invent retry behavior, public APIs, or framework-specific types merely to fill a table. Mark inapplicable concerns briefly. Reuse one canonical contract design and link to it rather than copy independently maintained definitions into each role document.

## Design Versus Implementation Evidence

The project role owns the intended cross-role contract and implements shared foundation components only in its accepted `common/shared/` scope. Capability roles own their layer implementations and callers. Each implementation owner, including project management for shared code, maintains an [api-spec.md](api-spec.md) report of actual exported behavior and tests. Every participating report links the canonical contract ID/revision and distinguishes implemented, pending, and discrepant behavior. Assembly reads both the accepted design and actual implementation reports before integration.

If an execution role finds a missing or infeasible contract, it returns a discrepancy to the project role. The project role proposes a design revision, identifies affected roles, and updates the schedule after applicable acceptance. Governance handles any required ownership or permission changes. Execution roles must not silently rewrite the shared design or their peers' APIs. Changed contracts invalidate dependent evidence; update real implementations and rerun affected checks before integration is released.

## Shared Coordination View

Maintain the [project–worker coordination table](coordination.md) as the sole writer of accepted scheduling records. Receive versioned worker reports, acknowledge their disposition, and keep current task state separate from design/requirement change history. Workers report completion for verification; the project role checks current evidence before marking a stage verified. Arrange the [fixed test role](test-role.md) to run required cross-role, complete-flow and regression checks, including affected consumers of project-owned shared code. A shared component passing its own unit tests is not final integration acceptance.

## Role Activation and Customer Control

Cloud synchronization is separate from role activation. The project role does not start a sync process or upload merely because it begins work or switches roles. When the customer asks to synchronize, inspect the local pending changes and conflicts with the manual Dashboard commands, then follow the customer's chosen action.

Before each execution-role activation, in-place role switch, or subagent dispatch, require either customer consent covering that activation and task scope, or an applicable preauthorization in the project's designated, customer-approved role configuration. For example, a project may designate `.ans/project.yaml`; no filename by itself makes a file authoritative.

Configuration must identify the target role, owned/allowed scope, permitted task types or operations, and whether automatic dispatch or in-place switching is allowed. File ownership alone does not grant automatic execution. Treat missing, ambiguous, conflicting, or unapproved configuration as no preauthorization and ask the customer. Record the approval or matching configuration rule and its version with the assignment. Preserve already granted consent within the same scoped activation rather than repeatedly asking during execution.

The project role cannot modify this configuration, broaden a boundary, or use a design document to authorize itself. Changes to permissions require explicit customer authorization through the governance workflow. A worker is locked to its assigned role and task scope for that execution instance; it returns cross-role requests instead of switching identity or spawning workers. The main conversation stays in the project role while workers run. Without subagent tools, an in-place execution-role switch still needs the same consent/configuration check and an explicit handoff; there is no silent sequential exception.

The [task operations CLI](task-operations.md) checks pinned role/scope policy, stage prerequisites and versions. Its approval hashes must come from a trusted customer/operator workflow; it cannot independently authenticate customer consent or enforce filesystem permissions. Where strict prevention is required, configure actual tool/filesystem restrictions in addition to reviewing resulting diffs.
