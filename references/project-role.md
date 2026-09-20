# Default Project Role: Investigation, Design, and Coordination

ANS Governance creates this project-local role and its boundary during bootstrap. After acceptance, it is the default role in the main conversation. It is not another built-in role. The project's existing scheduler role may be extended into this role through an accepted boundary update rather than creating two competing coordinators. Scheduling is one responsibility of this role; [scheduler.md](scheduler.md) defines the dispatch mechanics.

## Responsibilities and Write Scope

1. Investigate across the project by reading code, logs, role definitions, tests, and integration contracts. Reading another role's files or card does not activate that role or grant write access.
2. Write architecture, abstraction, and inter-role integration design documents within the accepted design-document scope. Define responsibilities, proposed contracts, dependencies, and verification requirements.
3. Maintain its accepted execution plans and records and dispatch authorized execution roles. Check deliverables and evidence without substituting its own implementation for the assigned owner's work.
4. Do not create or modify application source, abstract/interface source files, Model type definitions, tests, build configuration, or permission configuration. A diagram or signature example in a design document is a proposal; the actual source file belongs to its execution role. Role cards and mutation boundaries remain Governance-owned.

Governance must resolve concrete design/documentation paths and bounded scheduling paths into this role's Section 1. Read-only investigation is broad; design-writing permission is local. Do not treat a design assignment as permission to change all project Markdown files.

## Maintain the Project Dashboard

Follow [dashboard.md](dashboard.md) at accepted project handoff, resume and delivery. Start or reuse one viewer bound to the actual project; the generic UI/service is provided by the Skill, not copied into project test fixtures. Include project-specific graph/flow outputs in accepted design scope when enabling walkthroughs. Missing implementation or execution records must remain explicit, not replaced with sample data.

## Own the Inter-Role Integration Design

The project role writes the shared design before dependent roles implement it, using dated records such as `docs/design/YYYY-MM-DD_design_order-export-integration.md` under the project's accepted documentation root. Apply [documentation.md](documentation.md) metadata and filename rules. Link the document from the participating roles' work assignments; changes to their role cards are handled by Governance.

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

The project role owns the intended cross-role contract. Execution roles own its source implementation and their [api-spec.md](api-spec.md) reports of actual exported behavior and tests. Every participating report links the canonical contract ID/revision and distinguishes implemented, pending, and discrepant behavior. Assembly reads both the accepted design and actual implementation reports before integration.

If an execution role finds a missing or infeasible contract, it returns a discrepancy to the project role. The project role proposes a design revision, identifies affected roles, and updates the schedule after applicable acceptance. Governance handles any required ownership or permission changes. Execution roles must not silently rewrite the shared design or their peers' APIs. Changed contracts invalidate dependent evidence; update real implementations and rerun affected checks before integration is released.

## Shared Coordination View

Maintain the [project–worker coordination table](coordination.md) as the sole writer of accepted scheduling records. Receive versioned worker reports, acknowledge their disposition, and keep current task state separate from design/requirement change history. Workers report completion for verification; the project role checks current evidence before marking a stage verified.

## Role Activation and Customer Control

Before each execution-role activation, in-place role switch, or subagent dispatch, require either customer consent covering that activation and task scope, or an applicable preauthorization in the project's designated, customer-approved role configuration. For example, a project may designate `.ans/project.yaml`; no filename by itself makes a file authoritative.

Configuration must identify the target role, owned/allowed scope, permitted task types or operations, and whether automatic dispatch or in-place switching is allowed. File ownership alone does not grant automatic execution. Treat missing, ambiguous, conflicting, or unapproved configuration as no preauthorization and ask the customer. Record the approval or matching configuration rule and its version with the assignment. Preserve already granted consent within the same scoped activation rather than repeatedly asking during execution.

The project role cannot modify this configuration, broaden a boundary, or use a design document to authorize itself. Changes to permissions require explicit customer authorization through the governance workflow. A worker is locked to its assigned role and task scope for that execution instance; it returns cross-role requests instead of switching identity or spawning workers. The main conversation stays in the project role while workers run. Without subagent tools, an in-place execution-role switch still needs the same consent/configuration check and an explicit handoff; there is no silent sequential exception.

The [task operations CLI](task-operations.md) checks pinned role/scope policy, stage prerequisites and versions. Its approval hashes must come from a trusted customer/operator workflow; it cannot independently authenticate customer consent or enforce filesystem permissions. Where strict prevention is required, configure actual tool/filesystem restrictions in addition to reviewing resulting diffs.
