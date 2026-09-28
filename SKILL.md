---
name: ans-governed-construction
description: Help Codex make code changes within approved file and role boundaries. Use for implementation, bug fixes, or refactoring in projects that need five-layer call rules, tests, and clear evidence. Do not use for read-only answers, ordinary writing, or open-ended brainstorming.
---

# ANS Governed Construction

This skill helps AI change a project without touching unrelated files. Read enough to understand the problem, but edit only files the current task and active role allow. Explain results so a beginning programmer can tell what changed, what it does, and how it was checked.

The governing rule is:

> Read widely when needed; change only what you are allowed to change.

AI may propose a change. The user and the execution environment decide what may run and what may be accepted.

When first invoked, you work under the **ANS Governance** built-in role — no separate role card or boundary document is needed to begin. See [Built-in Role: ANS Governance](#built-in-role-ans-governance).

## Governing Invariants

Maintain these invariants throughout the task:

1. **Edit only allowed files.** A file must be in this task's write scope; ask for a scope change before editing anything else.
2. **Follow the layer rules.** Code may call only capabilities allowed by its layer and the agreed public interface.
3. **A patch is not yet a finished change.** Run the required structure checks and behavior tests first.
4. **Tests prove only what they actually ran.** Record the code version, environment, inputs, and rules used for the result.
5. **Protect frozen files.** Do not change them during an ordinary downstream fix; change them only when the task authorizes it.
6. **Retest callers after changing a dependency.** Earlier test results for affected code are no longer current.
7. **Do not make a failing change look successful.** Never delete tests, loosen assertions, widen permissions, or hide errors just to make it pass unless the user explicitly changes that rule.

### Adjacent-Layer Call Direction

```text
Interface -> Pipeline -> Service -> Provider -> external infrastructure
Model: shared by all four operational layers
```

See [references/architecture.md](references/architecture.md) for the full dependency decision table, three-part layer structure (`abstract/`/`public/`/`impl/`), enforcement edge cases (imports, callbacks, factories, dynamic imports, re-exports), creation locality rules, and Model sharing constraints.

## Role Cards & Module Boundary Documents

Role cards (角色卡) and module boundary documents (模块边界文档) together define **what the AI may read and what it may mutate**. They are per-project artifacts, created autonomously by the AI when needed. Both are candidates until human-accepted. Follow explicit user requirements first, then repository conventions, then language/toolchain conventions. Use OS locale only as a fallback for natural-language prose; never translate identifiers or change filenames solely because of locale.

**Boundary documents** have Section 1 (mutation whitelist); description and ownership details live in the companion `functional-description.md`. Only the built-in Governance reference carries its scope and responsibilities together; project roles, including the scheduler, use boundary.md Section 1 and companion descriptions. **Role cards** describe what the agent does, list must-read docs (including its boundary doc), state the execution principles, and index the **system features this role primarily owns**. Each feature gets one current-behavior document under that role's `features/`; do not confuse a system feature with a role duty or use feature ownership as mutation permission. See [references/module-boundary.md](references/module-boundary.md), [references/role-card.md](references/role-card.md), and [references/feature-point.md](references/feature-point.md).

**Files not listed in Section 1 are read-only by default.** To mutate an unlisted file, the AI must first propose updating the boundary document's Section 1 (Governing Invariant #1).

The project keeps one [SQLite project-understanding store](references/project-context.md) at `project-context/context.sqlite3`. Each role reads its overview first, then queries task-relevant topics by `role_id`. Content writes use the role-scoped CRUD tool and its accepted logical row scope; the store does not replace canonical contracts or authorize changes.

Dated documents explain work to people; they are not copies of the task audit log. Use [the shared documentation rules](references/documentation.md) plus only the guide for the type being written: [design](references/documentation-design.md), [feature](references/documentation-feature.md), [change](references/documentation-change.md), or [fix](references/documentation-fix.md). A feature document must trace the complete path and meaningful branches; a change document must name the user-visible entry and verified code location. If that location is unknown, keep investigating before implementing rather than inventing a path. Keep date metadata for navigation and link detailed test evidence instead of copying logs.

For work that would change application code or tests, prepare the relevant dated document first and make the proposed behavior and scope reviewable. Summarize it in the chat with a link and, when helpful, a small diagram or table. Do not change application code or tests until the customer confirms that document and instructs implementation based on it. An existing confirmation and implementation instruction for that document/version remains valid across turns; do not ask again. Read-only investigation and document preparation may continue while a decision is pending. If the design changes materially, present the revised document before implementing the affected change.

Separate changes required by the task or existing contracts from optional hardening, compatibility or speculative additions. Show each optional item in both the document and its plain-language chat summary, with a stable item ID, reason, benefit and added cost. Options are checked by default as recommendations but remain pending; only implement the options explicitly covered by the customer's confirmed selection and implementation authorization. A default checkmark alone is not consent. Follow [the optional-change rules](references/documentation.md).

After writing a document, link it and restate its meaning in brief, plain language for a beginning programmer; do not just copy technical headings or identifiers. Explain the problem, proposed change, how the user will use it, and what is or is not done. When needed and authorized, a read-only subagent may help shorten the explanation; prefer a low-cost model with low reasoning effort and minimal context, then verify its summary against the document before sending. Follow [the documentation handoff guide](references/documentation.md). For a design proposal, invite the customer to ask what they want clarified; that invitation is not itself confirmation or permission to implement.

Write each Flow so a beginning programmer can answer: **What is the user trying to do? What changes on success? What happens on failure?** Put those answers in `flow.intent`, using short, concrete sentences backed by current code. Put button clicks in `flow.triggers`, actual `if/else` conditions in `flow.graph.edges`, and debugging checks plus source locations on error nodes. Never use generic filler such as "from entry to result" as a purpose, invent branches from prose, or bulk-fill old flows from button names. Update only task-relevant flows after checking real code and tests; mark the rest as missing. A resulting HTTP request is a step of the same Flow, not a separate Event. See [Interface constraints](references/interface.md) and [project context](references/project-context.md).

### Bootstrap

On a project with no boundary documents, follow the [bootstrap workflow](references/bootstrap-workflow.md) under the ANS Governance built-in role.

### Governance Rules

- Every role card must reference its module boundary document. Every boundary document must list specific application source files in Section 1, not wildcard directories; supporting and governance locations (`docs/`, role directories, the skill's own `references/`) may use directory-scoped or conditional entries.
- Adding or removing a file from a capability must update its boundary document's Section 1. A mismatch is a documentation gap — flag or block acceptance.
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

Project roles (scheduler, capabilities, and assembly) and their boundary documents are created by ANS Governance. The scheduler is an ordinary project role, not another built-in role. A role never creates itself. Each role is a directory containing a role card, a boundary document, and a changelog — see [references/role-card.md](references/role-card.md) for the layout.

**After bootstrap, ANS Governance creates no application code.** Implementation of each capability is a separate task under that capability's role. Load its role card and boundary doc Section 1 before writing code.

### Default Project Role

Governance creates the [default project role](references/project-role.md), which owns global investigation, architecture/abstraction design, inter-role integration design documents, and scheduling. It writes only its accepted design documents and execution records, never application source or permission configuration. Keep it active in the main conversation while authorized workers implement their assigned roles. Read [the dispatch protocol](references/scheduler.md) for the scheduling part. The execution graph comes from agreed role contracts and explicit task prerequisites.

### Default Project Dashboard

Every project using this skill gets the reusable Dashboard workflow in [dashboard.md](references/dashboard.md). After the project role is accepted, it starts or reuses one local read-only dashboard for the actual project, opens it when possible, and provides its URL. The shared UI and server remain in the Skill installation; role cards, boundaries, project understanding and coordination records come from that project. A separately deployed shared Dashboard is optional. When configured, completed local management changes can be recorded with `python3 -m dashboard.versioned_sync --root <project-root> --record`; **only a user-requested sync command uploads them**. Cloud data is a versioned project snapshot; a conflict must be shown to the customer and never auto-resolved. Store the one project Key in the project-root `.ans-dashboard.local.json` via `python3 -m dashboard.local_config init`; keep it out of prompts and version control. See [dashboard/README.md](dashboard/README.md). Never point a real task at `test/game-engine` or copy its example data as if it described the new project. If the user opts out or the environment cannot host a viewer, report that limitation without blocking otherwise authorized development.

The shared Dashboard may also host an opt-in [role channel](dashboard/README.md#role-channel): each role sends its own task messages and exact permission requests using the project's shared Key and declaring its active role ID. The server checks project scope but does not independently authenticate each role behind that shared Key. Only an administrator login records decisions. A Dashboard decision is not dispatch or mutation authority: continue to enforce customer consent or approved configuration through `task_ops` before any worker activation.

## Role Switching

Each agent context has exactly one active role at a time; concurrent agents may hold different roles. Switching roles changes mutation authority, required reading, and execution context.

### Activation

1. **Load the target role card** from `角色卡/<role>/role-card.md`. The role-directory root name follows the project language (`角色卡/` in Chinese projects, e.g. `role-cards/` in English ones); examples use the Chinese form.
2. **Load boundary.md Section 1** — this becomes the only mutation authority.
3. **Verify authorization and activation:** Obtain customer consent for the role activation/task scope or match a preauthorized rule in the designated customer-approved project configuration, as specified in [project-role.md](references/project-role.md). This applies equally to subagent dispatch and in-place switching. Explicitly state the target role and confirm its loaded Section 1 is the active whitelist. Writing application code without an active role card is a governance violation (Governing Invariant #1).

Activation requires an explicit role switch and loading its scope; merely reading a card to route or schedule work does not activate it. Only ANS Governance uses its built-in reference Section 1; the project scheduler must load its own accepted card and boundary. The active role persists until another explicit activation or task end.

### When to Switch

| Current role | Switch to | When |
|---|---|---|
| ANS Governance (built-in) | Project scheduler | Role definitions accepted; task requires execution planning or dispatch |
| Project scheduler | Capability or assembly role | Ready stage dispatched to a worker, or explicit sequential fallback |
| Capability or assembly role | Project scheduler | Sequential stage returns; report results/dependency requests to the scheduler |
| Capability worker | Default project role (handoff) | Return a cross-role request; the worker does not switch identity or acquire another scope |
| Default project role | ANS Governance (built-in) | Customer-authorized governance change; capability workers return requests instead of self-switching |
| Project scheduler | ANS Governance (built-in) | Missing role, ownership conflict, or required policy/scope change |

For coordinated execution, hand off from ANS Governance to the accepted project scheduler after bootstrap acceptance; it dispatches ready stages. Existing accepted definitions can be reused. A standalone single-role task may omit scheduling records, but leaving the default project role to execute it still requires the same consent/configuration gate; workers may not independently spawn or switch roles.

### Rules

- **One role per task context.** A single AI agent works under one role at a time. Only an activated, accepted project scheduler dispatches execution agents, each with its own role card, narrowed scope, and ready prerequisites. Workers do not spawn or assign other workers; use explicit sequential role switching when subagent tools are unavailable. See [bootstrap scheduling](references/bootstrap-workflow.md#dependency-aware-scheduling).
- **Role activation required before mutation.** Before creating or modifying any file, verify the current role. Without an active project role card, only ANS Governance may create governance artifacts. Scheduling records require an accepted project scheduler role card and boundary.
- **No silent role drift.** When a task crosses role boundaries (e.g., fixing a bug in one capability reveals a governance gap), hold the cross-scope mutation and return it to the project role. A worker remains locked to its assignment; a new role activation requires the consent/configuration gate.
- **Evidence is role-scoped.** Verification evidence collected under one role is valid only for that role's mutation scope. Switching roles alone does not invalidate evidence. Scheduler may inspect role-produced verification evidence to release a stage, without transferring the owner's responsibility or treating it as final integrated verification.
- **Assembly role is a capability role.** It follows the same switching rules. It may prepare build/test configuration early. Final integration waits for its actual dependencies and their verification, not every unrelated role. Read the participating roles' `api-spec.md` before wiring; each assembly-owned file still obeys its layer's call rules. See [Assembly](references/built-in-assembly.md).

## Task Routing

The project scheduler routes coordinated execution to the correct accepted role before dispatch. A standalone single-role task can activate its owner only after the customer-consent/configuration check. Missing roles or ownership changes return to ANS Governance.

### Routing Sources

The primary routing table is each role's `boundary.md` Section 1. Every file in the project belongs to exactly one role or is unowned. Use targeted source searches, stack traces, and integration contracts to trace dependencies; no code-atlas scan is required.

### Routing Process

1. **Extract file evidence.** From the bug report or task description, identify affected files, error locations, stack traces, or user-visible symptoms. Prefer concrete file paths over abstract descriptions.
2. **Look up the owning role.** Search all `角色卡/*/boundary.md` Section 1 tables for the affected files. The role whose Section 1 lists the file is the owner.
   - **File found** → Scheduler assigns a stage to that owner; the worker loads its role card and follows [Role Switching](#role-switching) activation.
   - **File unlisted** → it is read-only by default. Report the gap and decide: add to an existing role's Section 1, create a new role, or mark as frozen.
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
| [Default project role](references/project-role.md) | Main-conversation investigation, architecture/abstraction/integration design, and role-activation authorization |
| [Legacy role function graphs](references/role-atlas.md) | User explicitly requests a step-by-step source walkthrough or the old role graph |
| [Local dashboard](references/dashboard.md) | Default project handoff, resume, live role/stage viewing, and final project URL delivery |
| [Task operations](references/task-operations.md) | Initialize/dispatch tasks, check scope and revisions, accept feedback, run approved checks, recover records |
| [Coordination table](references/coordination.md) | Project/worker progress, issues, completion reports, requirement/design revisions, and shared status rendering |
| [Project scheduler template](references/scheduler.md) | Governance creates a scheduler role, or an accepted project scheduler plans, dispatches, resumes, or releases stages |
| [Bootstrap workflow](references/bootstrap-workflow.md) | First encounter with a project — no boundary documents exist |
| [Action and communication](references/action-policy.md) | Starting a task or choosing whether to act, inspect, preview, ask, or notify; calibrate actions to existing authorization and evidence |
| [Workflow](references/workflow.md) | Any design, investigation, or mutation: baseline, bottom-up construction, top-down diagnosis, mutation contract, scope expansion, and stop conditions |
| [Module boundary document Section 1](references/module-boundary.md) | Before any task: load Section 1 to determine mutation scope |
| [Role card](references/role-card.md) | Before any task: load role card for capability context, execution principles, and required reading |
| [Evidence and acceptance](references/evidence.md) | Frozen artifacts or changed dependencies, and before accepting or reporting completion of any candidate |
| [Human-first documentation](references/documentation.md) | When writing a dated document; then load only its design, feature, change, or fix guide |
| [System feature-point document](references/feature-point.md) | When assigning a system feature to a role or writing/updating that feature's current-behavior document |

Map repository names to the five responsibilities; naming differences do not relax dependencies. Report existing conflicts and scope the necessary repair rather than silently adding exceptions or migrating unrelated code. Filenames and export mechanisms follow the project language; `main.js` and `index.js` are not universal requirements.

## Optional Code Atlas

Do not load code-atlas references, scan/update/query atlas snapshots, or open the graph during ordinary development, investigation, or acceptance. Use the retained [atlas tools](references/code-atlas.md) only when the user explicitly requests them. The task dependency graph and role Dashboard remain part of coordination and do not require a code atlas.
