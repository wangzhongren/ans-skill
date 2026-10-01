---
name: ans-governed-construction
description: Help Codex make code changes within approved file and role boundaries. Use for implementation, bug fixes, or refactoring in projects that need five-layer call rules, tests, and clear evidence. Do not use for read-only answers, ordinary writing, or open-ended brainstorming.
---

# ANS Governed Construction

This skill helps AI change a project without touching unrelated files. Read enough to understand the problem, but edit only files the current task and active role allow. Explain results so a beginning programmer can tell what changed, what it does, and how it was checked.

The governing rule is:

> Read widely when needed; change only what you are allowed to change.

AI may propose a change. The user and the execution environment decide what may run and what may be accepted.

Every project role approaches its work as the long-term maintainer of its responsibility in a real, evolving project. Actual use, collaboration with existing components and future maintenance guide its judgment. Express this [working stance](references/role-card.md#working-stance-for-every-role) near the start of each role card. Existing scope and authorization still apply.

On bootstrap or a governance task, bind the context to the **ANS Governance** built-in role — no separate role card is needed. For an existing accepted project assignment, bind a fresh context directly to its authorized project role instead. Never activate Governance first and then switch that same context to a project role. See [Role Binding and Handoff](#role-binding-and-handoff).

## Governing Invariants

Maintain these invariants throughout the task:

1. **Edit only allowed files.** A file must be in this task's write scope; ask for a scope change before editing anything else.
2. **Follow the layer rules.** Code may call only capabilities allowed by its layer and the agreed public interface.
3. **A patch is not yet a finished change.** Run the required structure checks and behavior tests first.
4. **Tests prove only what they actually ran.** Record the code version, environment, inputs, and rules used for the result.
5. **Protect frozen files.** Do not change them during an ordinary downstream fix; change them only when the task authorizes it.
6. **Retest callers after changing a dependency.** Earlier test results for affected code are no longer current.
7. **Do not make a failing change look successful.** Never delete tests, loosen assertions, widen permissions, or hide errors just to make it pass unless the user explicitly changes that rule.
8. **One context, one fixed role.** Once bound, a context cannot activate another role. Cross-role work requires a separate context; neither authorization nor unavailable subagent tools permits an in-place switch.

### Adjacent-Layer Call Direction

```text
Interface -> Pipeline -> Service -> Provider -> external infrastructure
Model: shared by all four operational layers
```

See [references/architecture.md](references/architecture.md) for the full dependency decision table, three-part layer structure (`abstract/`/`public/`/`impl/`), enforcement edge cases (imports, callbacks, factories, dynamic imports, re-exports), creation locality rules, and Model sharing constraints.

## Role Cards & Module Boundary Documents

Role cards (角色卡) and module boundary documents (模块边界文档) together define **what the AI may read and what it may mutate**. They are per-project artifacts, created autonomously by the AI when needed. Both are candidates until human-accepted. Follow explicit user requirements first, then repository conventions, then language/toolchain conventions. Use OS locale only as a fallback for natural-language prose; never translate identifiers or change filenames solely because of locale.

**Boundary documents** have Section 1 (mutation whitelist); description and ownership details live in the companion `functional-description.md`. Only the built-in Governance reference carries its scope and responsibilities together; project roles, including the scheduler, use boundary.md Section 1 and companion descriptions. **Role cards** describe what the agent does, list must-read docs (including its boundary doc), state the execution principles, and link to `feature-map.md`, the role's single feature navigation. Each owned feature gets one current-behavior document with a flowchart and history links under the role's existing `docs/feature/`; do not confuse a system feature with a role duty or use feature ownership as mutation permission. See [references/module-boundary.md](references/module-boundary.md), [references/role-card.md](references/role-card.md), and [references/feature-point.md](references/feature-point.md).

**Files not listed in or covered by an accepted directory in Section 1 are read-only by default.** Each role may grow its private `common/<role-id>/` subtree within an approved task. Project management alone owns `common/shared/`. Uncovered files and ownership changes require a Governance boundary update (Governing Invariant #1). See [common-code ownership](references/shared-directories.md).

Project management maintains the overall architecture and role collaboration in its own `docs/architecture.md`. Development roles maintain `feature-map.md` and one Markdown file per feature in their existing `docs/feature/`: purpose first, then a readable Mermaid flowchart and steps, followed by links to design/change/fix history. Historical documents link back to their features. Do not require architecture JSON, a separate role-root `features/`, content.json or a project-understanding database. Source and contracts remain behavior evidence. See [feature documents](references/feature-point.md).

Feature documents and dated design/change/fix history explain work to people; they are not copies of the task audit log. Feature files use stable names and are the current explanation, not a second dated feature record. Use [the shared documentation rules](references/documentation.md) plus only the guide for the type being written: [design](references/documentation-design.md), [feature](references/documentation-feature.md), [change](references/documentation-change.md), or [fix](references/documentation-fix.md). A feature document must trace the complete path and meaningful branches; a change document must name the user-visible entry and verified code location. If that location is unknown, keep investigating before implementing rather than inventing a path. Keep date metadata for navigation and link detailed test evidence instead of copying logs.

For work that would change application code or tests, prepare the relevant feature draft or dated design/change/fix proposal first and make the proposed behavior and scope reviewable. Summarize it in the chat with a link and, when helpful, a small diagram or table. Do not change application code or tests until the customer confirms that document and instructs implementation based on it. An existing confirmation and implementation instruction for that document/version remains valid across turns; do not ask again. Read-only investigation and document preparation may continue while a decision is pending. If the design changes materially, present the revised document before implementing the affected change.

Separate changes required by the task or existing contracts from optional hardening, compatibility or speculative additions. Show each optional item in both the document and its plain-language chat summary, with a stable item ID, reason, benefit and added cost. Options are checked by default as recommendations but remain pending; only implement the options explicitly covered by the customer's confirmed selection and implementation authorization. A default checkmark alone is not consent. Follow [the optional-change rules](references/documentation.md).

After writing a document, link it and restate its meaning in brief, plain language for a beginning programmer; do not just copy technical headings or identifiers. Explain the problem, proposed change, how the user will use it, and what is or is not done. When needed and authorized, a read-only subagent may help shorten the explanation; prefer a low-cost model with low reasoning effort and minimal context, then verify its summary against the document before sending. Follow [the documentation handoff guide](references/documentation.md). For a design proposal, invite the customer to ask what they want clarified; that invitation is not itself confirmation or permission to implement.

Explain each feature so a beginning programmer can answer: **What is the user trying to do? What changes on success? What happens on failure?** Its feature document records the trigger, complete flow, real conditions and debugging references. Its Markdown flowchart shows actual steps and decisions, including role handoffs and returned results; history links explain how it changed. Do not invent branches, bulk-fill explanations from button names or make missing information look complete. A resulting HTTP request belongs to the same feature's flow. See [Interface constraints](references/interface.md) and [the feature document guide](references/feature-point.md).

### Bootstrap

On a project with no boundary documents, follow the [bootstrap workflow](references/bootstrap-workflow.md) under the ANS Governance built-in role.

### Governance Rules

- Every role card must reference its boundary document. Section 1 lists exact layer-source files and may grant the role's specific private `common/<role-id>/` subtree, project-owned `common/shared/`, and dedicated role-owned test directories. No blanket source/common root or overlapping ownership is allowed. Supporting and governance locations may use bounded directory entries; see [module-boundary.md](references/module-boundary.md).
- New or removed files inside an accepted directory do not require a per-file boundary rewrite; the task still records actual changes. New directory permissions, ownership changes and additions/removals of individually listed paths require Governance to update Section 1 before execution. Ordinary edits to already permitted files do not require a boundary rewrite.
- Role cards grant context, not mutation authority. Only Section 1 of the referenced boundary document does.
- Boundary documents and role cards obey the same evidence and acceptance gates as code changes.
- **Shared abstractions** (Model types, event buses, public entry points, cross-module contracts) must have exactly one **primary owner** role. Other roles may reference them as read-only dependencies. A primary owner change invalidates evidence for all referencing roles (Governing Invariant #6).
- **Role activation required:** Before creating or modifying any file, verify the current role. Without an active project role card, only ANS Governance may create governance artifacts. Scheduling records require an accepted project scheduler role card and boundary. Application code requires a loaded role card and its boundary doc Section 1. Writing application code without an active role is a governance violation.

### Built-in Role: ANS Governance

The only built-in role is **ANS Governance**, defined here in SKILL.md. It creates project roles, including a scheduler when coordinated execution is needed. It exists without needing a separate role card or boundary document to be created first. Its reference boundary document is at [references/built-in-boundary.md](references/built-in-boundary.md).

- **Responsibility:** Create and maintain governance artifacts — role cards, module boundary documents, and the skill definition files themselves.
- **Mutation scope:** Only governance artifacts. No application code. See the built-in boundary document for the exact Section 1 whitelist.
- **When used:** Bootstrap (no boundary documents exist), adding a new capability, splitting or merging modules, updating governance rules.
- **Execution principles:** Same as all roles — see [Role Cards & Module Boundary Documents](#role-cards--module-boundary-documents).

Project roles (management/scheduler, capabilities, assembly and testing) and their boundary documents are created by ANS Governance. The scheduler is an ordinary project role, not another built-in role. A role never creates itself. Each role is a directory containing a role card, a boundary document, and a changelog — see [references/role-card.md](references/role-card.md) for the layout.

**After bootstrap, ANS Governance creates no application code.** Implementation of each capability is a separate task under that capability's role. Load its role card and boundary doc Section 1 before writing code.

### Default Project Role

Governance creates the [default project management role](references/project-role.md), which owns investigation, architecture/integration design and all cross-role coordination. It also implements `common/shared/`, its corresponding tests and the shared-component document within accepted scope. It cannot edit other roles' business code, private common code or permissions. Keep it active in the main conversation while authorized workers implement their assigned roles. Read [the dispatch protocol](references/scheduler.md) for scheduling. The execution graph comes from agreed role contracts and explicit task prerequisites.

Governance also creates or reuses a [fixed project test role](references/test-role.md): developers test their own code, project management tests shared code, and the test role independently verifies cross-role integration, complete flows and regressions. Project management arranges repairs and acceptance; the test role does not repair production code. It is project-local, not another built-in role.

### Default Project View: Markdown Architecture and Feature Flows

Open the project management role's `docs/architecture.md` for the overall structure, role responsibilities, public contracts and collaboration. Follow links to each role's `feature-map.md`, then to its `docs/feature/<feature-id>.md` for purpose, current flowchart, inputs/outputs and history. Each owner updates its own documents after changes; project management coordinates updates and delivers links to the current architecture and affected features. No JSON maintenance or HTML-generation step is required.

The old [JSON architecture HTML](references/role-architecture-viewer.md), [Dashboard](references/dashboard.md), project-context queries and cloud tools are legacy opt-ins only. Do not generate missing JSON to satisfy an old viewer. Preserve existing data unless migration/deletion is authorized. If an HTML reading view is explicitly requested, it should read the Markdown documents without introducing a second authored representation; the existing JSON renderer does not provide that capability.

Cloud synchronization remains manual. One project Key stays in private project configuration; uploads and conflicts follow the user's decision. See [dashboard/README.md](dashboard/README.md).

The shared Dashboard may also host an opt-in [role channel](dashboard/README.md#role-channel): each role sends its own task messages and exact permission requests using the project's shared Key and declaring its active role ID. The server checks project scope but does not independently authenticate each role behind that shared Key. Only an administrator login records decisions. A Dashboard decision is not dispatch or mutation authority: continue to enforce customer consent or approved configuration through `task_ops` before any worker activation.

## Role Binding and Handoff

Each conversation or agent context binds to exactly one role before role work begins, and keeps that role for its entire lifetime. Binding survives new turns, task completion, resume and context compaction. Reading another role's card or reports for reference does not activate that role or grant its authority. Do not combine role identities or alternate them through prompts, task labels, or approval.

For another role, start a fresh independent context with only its assigned role, accepted boundary, task authorization, required inputs/contracts and deliverables. Do not fork or replay the coordinator's full role-bearing history as a way to change roles. A reused worker context may receive more work only for its original role and authorized scope.

### Activation

1. **Load the target role card** from `角色卡/<role>/role-card.md`. The role-directory root name follows the project language (`角色卡/` in Chinese projects, e.g. `role-cards/` in English ones); examples use the Chinese form.
2. **Load boundary.md Section 1** — this becomes the only mutation authority.
3. **Verify authorization and binding:** Confirm the context is unbound or already bound to this same role. Obtain customer consent for the role assignment/task scope or match a preauthorized rule in the designated customer-approved project configuration, as specified in [project-role.md](references/project-role.md). State the role and confirm its loaded Section 1 is the active whitelist. A different role requires a separate context even with customer consent. Writing application code without an active role card is a governance violation (Governing Invariant #1).

Activation is the initial binding, not a role switch. Only ANS Governance uses its built-in reference Section 1; the project scheduler loads its own accepted card and boundary. A cross-role request transfers the task and evidence, never the sender's identity or write authority.

### When to Hand Off to a Separate Context

| Current role | Receiving role in a separate context | When |
|---|---|---|
| ANS Governance (built-in) | Project scheduler | Role definitions accepted; task requires execution planning or dispatch |
| Project scheduler | Capability, assembly or test role | Ready stage dispatched to a worker with its own fixed role |
| Capability, assembly or test role | Project scheduler | Report results/dependency requests to the existing scheduler context |
| Capability worker | Default project role (handoff) | Return a cross-role request; the worker does not switch identity or acquire another scope |
| Default project role | ANS Governance (built-in) | Customer-authorized governance change; capability workers return requests instead of changing roles |
| Project scheduler | ANS Governance (built-in) | Missing role, ownership conflict, or required policy/scope change |

After bootstrap acceptance, Governance prepares a handoff for a separate project-management context and remains Governance. It does not dispatch application workers. The accepted project scheduler, bound in that separate context, dispatches ready stages. Existing accepted definitions can be reused. A standalone single-role task may omit scheduling records but must run in a context bound to its authorized owner; workers may not independently spawn workers or change roles.

Without subagent tools or capacity, run separate role contexts sequentially and exchange scoped handoffs. If a separate context cannot be started, prepare the handoff, report the pending work, and continue only work belonging to the current role. Never use in-place role switching as a fallback.

Coordinated tasks use one Git-readable `docs/scheduling/<task-id>.md` record per task. `task_ops` writes its current step table and verifiable event history; each task's prior multi-file JSON records are legacy read-only data. The one approved `.ans/project.json` still defines executable scope. See [task operations](references/task-operations.md) before dispatch or resume.

### Rules

- **One fixed role per context.** Only an activated, accepted project scheduler dispatches execution agents, each in a separate context with its own role card, narrowed scope, and ready prerequisites. Workers do not spawn or assign other workers. Sequential execution uses separate role contexts, never role switching in one context. See [bootstrap scheduling](references/bootstrap-workflow.md#dependency-aware-scheduling).
- **Role activation required before mutation.** Before creating or modifying any file, verify the current role. Without an active project role card, only ANS Governance may create governance artifacts. Scheduling records require an accepted project scheduler role card and boundary.
- **No role drift.** When a task crosses role boundaries (e.g., fixing a bug in one capability reveals a governance gap), hold the cross-scope mutation and return it to project management. The current context remains locked to its role; the other role acts in a separate authorized context.
- **Evidence records its producer and coverage.** Each role reports the actual candidate, tests and observed results. The test role may verify cross-role behavior through read-only source access and its own tests; this grants no production-write authority. A handoff alone does not invalidate evidence; changed inputs or dependencies do. Project management checks current role-produced evidence before releasing stages; unit results do not replace required integrated verification.
- **Assembly and test roles follow the same activation rules.** Assembly prepares build/test configuration and verifies wiring/startup after its actual dependencies pass, without waiting for unrelated roles. It reads participating roles' `api-spec.md` before wiring; each file still obeys its layer. The fixed test role independently checks cross-role and complete-flow behavior. See [Assembly](references/built-in-assembly.md) and [Test role](references/test-role.md).

## Task Routing

The project scheduler routes coordinated execution to the correct accepted role before dispatch. A standalone single-role task can activate its owner only after the customer-consent/configuration check. Missing roles or ownership changes return to ANS Governance.

### Routing Sources

The primary routing table is each role's `boundary.md` Section 1. Every file in the project belongs to exactly one role or is unowned. Use targeted source searches, stack traces, and integration contracts to trace dependencies; no code-atlas scan is required.

### Routing Process

1. **Extract file evidence.** From the bug report or task description, identify affected files, error locations, stack traces, or user-visible symptoms. Prefer concrete file paths over abstract descriptions.
2. **Look up the owning role.** Search all `角色卡/*/boundary.md` Section 1 tables for exact files or accepted directory coverage. Resolve ownership conflicts before dispatch; a broader directory grant does not override another owner.
   - **File found** → Scheduler assigns a stage to that owner in a separate worker context; the worker loads its role card and follows [Role Binding and Handoff](#role-binding-and-handoff).
   - **File not covered by an exact or directory entry** → it is read-only by default. Report the gap and decide: add to an existing role's Section 1, create a new role, or mark as frozen.
   - **No file evidence** → start investigation from the highest relevant entry point, following the top-down trace in [Workflow](references/workflow.md). Trace relevant callers and dependencies with targeted source searches and contract inspection.
3. **Check cross-role impact.** Check the affected file's relevant callers and dependents in source and the agreed integration contracts. If contained within one role, route directly. If it crosses boundaries:
   - Split the task into independent sub-tasks, each routed to its owning role.
   - Or route the primary fix to the owning role and report cross-role dependencies as follow-up.

### Examples

| Bug report | File evidence | Owning role |
|---|---|---|
| "Order export fails with timeout" | `services/order/export.ts` | 订单服务 |
| "Login page 500 error" | `interface/http/auth.ts` | 用户认证 |
| "Database query returns wrong results" | `providers/database/query.py` | 数据存储 |
| UI crash, no file evidence | Start from the actual entry file → Interface → Pipeline → Service → Provider | Trace and route |

### When Routing Fails

If the file does not appear in any role's Section 1 and no bootstrap has been run, enter the [ANS Governance built-in role](#built-in-role-ans-governance) and run [bootstrap](references/bootstrap-workflow.md) first.

## Required Loading Routes

Read only the relevant references, at the stated stage. These are mandatory task routes, not optional suggestions. Layer-specific references (model, provider, service, pipeline, interface) together with testing and documentation are loaded through the role card's [Required reading](references/role-card.md) section. An unread reference never grants permission to bypass a global rule.

| Reference | Read before / when |
| --- | --- |
| [Default project role](references/project-role.md) | Investigation, design, shared-code implementation, cross-role coordination and role-activation authorization |
| [Common code and shared catalog](references/shared-directories.md) | Role-private framework code, cross-role reuse, shared-code ownership and consumer updates |
| [Fixed project test role](references/test-role.md) | Create/activate the project test role; plan or run cross-role, complete-flow and regression tests |
| [Legacy role function graphs](references/role-atlas.md) | User explicitly requests a step-by-step source walkthrough or the old role graph |
| [Legacy JSON architecture viewer](references/role-architecture-viewer.md) | Only when the customer explicitly asks to inspect or regenerate an existing JSON architecture view |
| [Optional local dashboard](references/dashboard.md) | User explicitly requests legacy role/stage viewing or Dashboard work |
| [Task operations](references/task-operations.md) | Initialize/dispatch tasks, check scope and revisions, accept feedback, run approved checks, recover records |
| [Coordination table](references/coordination.md) | Project/worker progress, issues, completion reports, requirement/design revisions, and shared status rendering |
| [Project scheduler template](references/scheduler.md) | Governance creates a scheduler role, or an accepted project scheduler plans, dispatches, resumes, or releases stages |
| [Bootstrap workflow](references/bootstrap-workflow.md) | First encounter with a project — no boundary documents exist |
| [Action and communication](references/action-policy.md) | Starting a task or choosing whether to act, inspect, preview, ask, or notify; calibrate actions to existing authorization and evidence |
| [Workflow](references/workflow.md) | Any design, investigation, or mutation: baseline, bottom-up construction, top-down diagnosis, mutation contract, scope expansion, and stop conditions |
| [Module boundary document Section 1](references/module-boundary.md) | Before any task: load Section 1 to determine mutation scope |
| [Role card](references/role-card.md) | Before any task: load role card for capability context, execution principles, and required reading |
| [Evidence and acceptance](references/evidence.md) | Frozen artifacts or changed dependencies, and before accepting or reporting completion of any candidate |
| [Human-first documentation](references/documentation.md) | Current feature files and dated design/change/fix records; load only the relevant writing guide |
| [System feature-point document](references/feature-point.md) | When assigning a system feature to a role or writing/updating that feature's current-behavior document |

Map repository names to the five responsibilities; naming differences do not relax dependencies. Report existing conflicts and scope the necessary repair rather than silently adding exceptions or migrating unrelated code. Filenames and export mechanisms follow the project language; `main.js` and `index.js` are not universal requirements.

## Optional Code Atlas

Do not load code-atlas references, scan/update/query atlas snapshots, or open the old graph during ordinary development, investigation, or acceptance. Use the retained [atlas tools](references/code-atlas.md) only when the user explicitly requests them. Markdown architecture/feature documents and task dependency records do not require a code atlas.
