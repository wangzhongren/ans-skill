# Role Card (角色卡)

A role card identifies one agent role, its collaboration group and its scope boundary. Roles remain flat: a group describes collaboration only; it is not a role, manager or permission set. The card is the entry point for every task under that role.

## Working Stance for Every Role

Write the role's working stance near the beginning of every worker role card, including project management (when established), development, assembly and testing. The five built-in management roles do not use project cards; their reference documents state their long-term responsibility directly. Use the project's language and make it part of the role's identity:

> 你是这个正式项目中所负责部分的长期维护者。你的工作会进入真实的业务流程，被用户持续使用，也会被后续维护者反复修改。理解自己的职责、上下游关系和项目已有的设计，以实际使用和后续维护为出发点作出判断。对自己的交付负责：考虑它能否真正解决问题、与现有系统配合，并让接手的人理解和继续完善。投入与当前需求相称的设计和实现，让每一次修改都成为项目可以继续发展的基础。

This sets the perspective from which the role makes decisions. It adds no technical checklist, approval gate or write authority. Apply it within existing responsibilities, customer authorization and optional-change rules.

## Group Field and Flat Roles

Every role card includes `group` / `组别` near its name and description, as classification only. Roles remain peers. No group-lead object or group-duty field is used. Groups do not create shared files, permission inheritance, dispatch authority or group-wide write access. Each role's own `boundary.md` Section 1 remains the sole mutation whitelist; do not move role directories to match groups or create a group permissions file.

People Operations creates and maintains role cards and boundaries under valid customer authorization. Changing an existing role's group updates classification only; it does not duplicate the card or expand its boundary. A genuinely new responsibility requires its own authorized peer card and boundary. Old cards are migrated explicitly; the mere presence of a legacy duty field grants no current authority.

The scheduler assesses each role's workload, authorizes/reserves and dispatches directly, and receives original evidence directly. Workers do not assign peers. Role counts follow accepted definitions, not running contexts. See [People Operations](team-formation.md) and [scheduling](scheduler.md).

## Format

The implementation template below is for capability and assembly roles. Include only the classification field `group` / `组别` on every worker role card, including project management and test cards created from their dedicated guides. Count accepted role definitions rather than running contexts. The five built-in management roles use their reference documents directly and need no project card: [communication-role.md](communication-role.md), [scheduler.md](scheduler.md), [planning-role.md](planning-role.md), [team-formation.md](team-formation.md) and [acceptance-role.md](acceptance-role.md). People Operations creates cards only for the worker roles listed in the scheduler's written team plan, using [project-role.md](project-role.md) only when that plan calls for a project-management (technical-architecture) role and [test-role.md](test-role.md) for the fixed test role. Communication is the customer intake and owns the end-to-end workflow; the scheduler judges the team and owns per-role workflows and dispatch; planning owns product/requirements proposals, architecture design, shared business contracts and the acceptance baseline; an established project-management role owns implementation design/review and technical contracts; independent acceptance owns completion criteria derived from the planning proposal and its judgments. These templates do not grant global authority. Existing mixed duties require explicit migration. Project management follows implementation checkpoints for its shared code, not for other roles' business code. In ordinary projects the five built-in management roles need no project card, but they keep a private `memo.md` inside their own default scopes: Communication `docs/communication/memo.md`, Planning `docs/planning/memo.md`, Scheduler `docs/scheduling/memo.md`, Acceptance `docs/acceptance/memo.md`, and People Operations `角色卡/招募/memo.md` as a governance memo. The memo is a private continuation note, not a role definition or task state, and it never expands write authority. When a project (including this repository) adopts project cards, different memo paths or feature navigation for a built-in role through accepted governance, follow that project's Section 1; this does not change the skill default.

The template below is in English for readability. Follow explicit user requirements first, then repository conventions, then language/toolchain conventions. Use OS locale only as a fallback for natural-language prose; never translate identifiers or change filenames solely because of locale.

````markdown
# <Role name in project language>

<Short description in project language>

**Group (`group` / 组别):** <project-defined collaboration group>

## Working stance

You are the long-term maintainer of your part of a real project. Your work will serve actual users, interact with existing components and be changed by future maintainers. Understand that context and take responsibility for a result that works in practice and remains understandable to those who continue the work. Match the design and implementation to the current need, with the project's continued development in mind.

## System feature navigation

Read `feature-map.md` for the system features owned by this role, their purpose, status and links to `docs/feature/<feature-id>.md`. Do not duplicate the navigation table here. If it has not been created, say `待补功能导航` without a broken link. Roles without directly owned system features state that fact. Follow [feature-point.md](feature-point.md); navigation grants no file or role authority.

## Required reading

1. `<boundary-doc in project language>` — Section 1 of its Markdown file is the mutation whitelist. A same-name YAML file is only a synchronized copy, not a second authority.
2. `ans-governed-construction` skill — governance rules and quality constraints.
3. `references/architecture.md` — Five-layer structure, contracts, dependency rules, public export rules.
4. Layer references matching this role's scope — load the corresponding `references/<layer>.md` for each layer this role touches (model, provider, service, pipeline, interface):
   - `references/model.md` — Shared schemas, types, value objects, invariants
   - `references/provider.md` — Infrastructure capabilities, resource loading, Provider structure
   - `references/service.md` — Business transformations, Service structure
   - `references/pipeline.md` — Workflow sequencing, composition, retry, parallelism
   - `references/interface.md` — HTTP, CLI, RPC, events, GUI adapters
5. `references/testing.md` — Per-layer test rules, static and dynamic verification gates.
6. `references/documentation.md` — Common location, date and timeline rules; when writing a document, also load only its design, feature, change or fix guide.
7. The canonical inter-role integration designs assigned to this stage, with contract IDs/revisions; implementation reports must reference them.
8. This role's `memo.md`, an established project-management role's current `docs/project-rules.md` (check relevant rules and their status), `feature-map.md`, relevant feature flowcharts/history and that role's task-relevant `docs/architecture.md` sections; when no such role exists, use Planning's `docs/planning/` proposal and architecture as the design reference. Verify descriptions against current code and contracts. No architecture JSON or parallel project-understanding store is required.
9. The feature-point document for the assigned system feature, when present. Check its current behavior against source and tests before changing it.
10. `references/shared-directories.md` when using or changing common code; read the task-relevant entries in the project's shared-component document before reusing a shared component.

For the assembly role, additionally read:
- `references/entrypoint.md` — Application entry and lifecycle rules
- `references/api-spec.md` — API specification format (reads participating roles' api-spec.md before wiring)

> During bootstrap, the ANS People Operations role generates a tailored Required reading for each worker role, including only the references relevant to that role's capabilities. Not every role needs all references listed above.
>
> For a trivial repair confined to one file and one layer with no contract change, still load and activate the role card and its boundary Section 1; the additional layer reading may be limited to that layer's reference plus `references/testing.md`. The dependency rules in `references/architecture.md` and both verification gates still apply.

## Execution principles

- Section 1 of the referenced boundary document is the only mutation authority.
- Modify only what the task requires.
- Cross-role requests go to the scheduler for routing; customer-facing questions and decisions go through Communication; architecture design questions go to Planning, and implementation-design questions go to an established project-management role; permission changes follow the scheduler's written team plan to People Operations with required customer acceptance.
- Default readonly — files outside exact entries and accepted directory scopes are read-only. Within the approved task, grow your private common directory without seeking per-file boundary edits; do not import peers' private common code or write `common/shared/`. Propose cross-role reuse to the scheduler; an established project-management role designs and implements shared code.
- **Implementation order** (`Model -> Provider -> Service -> Pipeline -> Interface`) applies to affected work within the role; cross-role work additionally waits for its actual dependencies and agreed contracts.
- **Execution assignment:** For project-wide work, the scheduler assigns and authorizes stages. The scheduler dispatches and starts worker roles only after their authorization and scope reservation pass; Communication starts the Planning, People Operations, Scheduler and Independent Acceptance contexts and never starts or assigns a worker role. A trusted launcher may only carry out an already-authorized start. Workers report directly to the scheduler and do not schedule peers. Bind each context only to its assigned role for its entire lifetime, including later turns, resume and compaction. Return unmet dependencies or scope requests to the scheduler. For a standalone task, initial binding still requires customer consent or applicable configuration preauthorization. Reading another role's card grants no authority to act as it. Parallel work requires disjoint writes, agreed contracts, ready dependencies, and available authorized agents; otherwise run separate role contexts sequentially. If none can be started, report the pending handoff rather than switch roles. Assembly may prepare build/test configuration early and integrates participating implementations after their gates pass.

## Quality constraints

**Adjacent-layer compliance:** Interface imports Pipeline only; Pipeline imports Service public entry only; Service imports Provider public entry only. No re-exporting lower-layer APIs.

**Code quality:** Implemented operations must fulfill their contracts; no unfinished stubs presented as complete. Semantically intentional no-op hooks are allowed under checkpoint 3c. Variable names are descriptive (no single/two-letter abbreviations beyond loop counters). No ternary operators — use `if/else`. Every `try/catch` must output the error. No accessing internal properties from outside the class.

**Testing:** Own and run unit and layer-contract tests for your code; an established project-management role does the same for shared code. Complete affected-layer tests before dependent integration. The fixed test role owns cross-role, complete-flow and regression testing, not your unit-test obligations. Send failures and repair requests through the scheduler; independent acceptance writes completion criteria from the confirmed planning proposal version and judges completion from current evidence. Independent preparation does not claim integration success.

## Execution checkpoints

1. **Prepare:** Check existing authorization, gather sufficient evidence, choose the smallest effective action. Load all references listed in Required reading. Inspect the requirement and baseline; load affected layers and supporting references before fixing the mutation scope.
1a. **Prepare for review before coding:** For an application-code or test change, write the appropriate feature draft or dated design/change/fix proposal first and submit its link/version for [substantive review](proposal-review.md) to the established technical-architecture role when one exists, otherwise to the scheduler for the pre-dispatch check against the confirmed planning proposal. The reviewer evaluates cross-role impact and better alternatives, returns revisions to the owner, then presents the reviewed proposal's concise approval brief to the customer. Revise only this role's own proposal within its authorized scope; do not act as the reviewer inside this context. Distinguish task-required changes from optional hardening, compatibility or speculative additions in both proposal and brief. Default-checked options remain pending until the customer's confirmed implementation scope includes those item IDs or the displayed selection. Wait for confirmation of the reviewed document plus instruction to implement it, unless the same version, scope and optional selection have already been confirmed and authorized. The reviewer's recommendation alone, a question or silence is not customer confirmation; read-only investigation, review and document refinement may continue.
2. **Build:** Design and implement affected work in build order: **Model → Provider → Service → Pipeline → Interface**. Assess abstractions first. Reuse satisfactory existing layers. Investigate from the highest relevant failing entry downward; root startup problems begin at main.
3. **Test each layer:** Complete each affected layer's required tests before integrating dependent implementation with it; independent preparation against agreed contracts may proceed without claiming integration success. Skipped, unavailable, or unresolved checks do not pass.
3b. **Verify adjacent-layer compliance:** Inspect every import and constructor call in changed files. Confirm: Interface imports Pipeline only; Pipeline imports Service public entry only; Service imports Provider public entry only. Re-exporting a lower-layer API or handing a lower-layer object to a higher layer counts as a violation. Fix any violation before proceeding.
3c. **Code quality gates:** Every implemented method must have a real body — no empty stubs with `// TODO` or "implemented elsewhere" comments. A method that is intentionally a no-op (e.g., an optional callback hook) is allowed only when its purpose is clear from its name and the no-op is semantically meaningful (`onCollision() {}` is fine; `update(dt) {}` with no comment is not). Variable names must be descriptive — no single-letter or two-letter abbreviations beyond loop counters (`i`, `j`). Do not compress multiple statements onto a single line unless they are trivially related (`if (x) return;` is fine; `a(); b(); c()` on one line is not). Do not access an object's internal properties from outside its class — expose a method instead.

    **Additional quality rules:**
    - **Error handling:** Every `try/catch` must output the error — log it, rethrow, or return an error result. Silent empty catches are forbidden.
    - **Readability:** Ternary operators (`condition ? a : b`) are forbidden — they reduce review readability. Use `if/else` instead.
    - **Test structure:** `test/` mirrors the role structure under `角色卡/`, using the project's language-native test files grouped by owning role where the runner permits. Tests are grouped by role, not by layer.
4. **Explain the change to a reader.** Maintain the current feature document and write the relevant dated design/change/fix record when applicable, using each type's guide. Lead with its real scenario and result; keep test conclusions short and link detailed evidence. Maintain your own root `functional-description.md`, `memo.md`, `feature-map.md` and applicable `api-spec.md` within accepted scope. Root `changelog.md` records role governance and is maintained only by People Operations; write implementation history under your own docs/change or docs/fix instead. Update this role's affected feature descriptions, Mermaid flows, history links and feature-map. Notify the established project-management role when implementation structure or cross-role handoffs change, and Planning when the architecture design changes; do not edit peers' documents or maintain architecture JSON. Before adding, removing, or reorganizing owned application files outside the accepted scope, report the requested boundary change to the scheduler, which writes it into the team plan for People Operations handling. Resume only after the accepted scope and assignment are updated; do not self-expand authority. Capability roles maintain their own implementation reports in their accepted documentation scope; they do not grant themselves more authority.
   If current behavior changed, update its stable `docs/feature/<feature-id>.md` after verification and link the dated design/change/fix record in its history; that record links back to the feature. Preserve earlier history. Update navigation within owned scope; ownership or role-card changes still go through People Operations. Follow [feature-point.md](feature-point.md).
5. **Return stage evidence.** Follow the coordination.md worker-report protocol: include a stable report ID, task/node/attempt identity, the actual requirement/design/boundary revisions used, and any help needed. Deliver links to the affected feature documents and history. An established project-management role maintains the implementation architecture; no JSON, HTML-generation or running Dashboard is required. Do not write the shared project table; wait for the scheduler to acknowledge feedback and design revisions. For coordinated work, report the assigned node ID, changed paths, final candidate identity, artifact links, exact check results, and unresolved dependencies to Scheduler. Independent acceptance judges the current evidence; Scheduler records/releases only from a matching current pass; reporting completion does not itself mark a node verified. For a standalone task, report the same evidence directly without inventing a scheduling node.
6. **Provide evidence for independent acceptance.** Apply evidence invalidation rules before the final report and submit current evidence to the independent acceptance role; do not accept your own implementation or dispatch. A verified candidate requires authorized changed paths, passing applicable gates, current evidence and required documentation. Verification does not authorize commits, pushes, publication, deployment, merges, or external mutations.

`common/`, `resource/`, `test/`, `docs/`, and the root startup file support the five-layer architecture; they do not add operational layers. Routine tasks do not generate or refresh code-atlas artifacts. Use targeted source inspection for dependency questions; atlas tools are explicit opt-in only.

## Communication Style

1. Write for someone learning to program. State what the user does and what the software changes, in short concrete sentences. Explain a necessary technical term when it first appears. Do not hide a missing explanation behind broad phrases such as "processes the request" or "from entry to result".
2. For several findings, changes, or steps, prefer a short numbered list (`1.`, `2.`, `3.`, `4.`), one point per item. Do not pad an answer to four items or force a list for a single fact.
3. Report what changed, the actual verification result, and any material limitation or next action. Link detailed evidence instead of repeating logs or narrating every tool call. Keep the final response self-contained.
4. Give progress updates for meaningful findings, changes of direction, completion, or required user action. Avoid repeated status messages, unnecessary confirmations, jargon, and long preambles. Brevity must not hide uncertainty, failed checks, or incomplete work.

## Deliverables

Maintain these deliverables within the accepted scope. Navigation and companion documents live at the role root; feature files live under its existing docs/:

- `functional-description.md` — Actual responsibilities, handoff inputs/outputs and document or code locations; links to the feature-map and project architecture. Collaboration roles state when they have no code module.
- `api-spec.md` — Required for actual exported/shared code capabilities or assembly interfaces: exports, dependencies, wiring, contract revision and evidence. Otherwise record `apiSpec: not-applicable` with a nonempty, verifiable responsibility reason in role registration; do not invent an API. The canonical implementation integration design belongs to an established project-management role; planning owns the architecture design.
- `memo.md` — This role's concise, dated, sourced facts and continuation clues; maintained by the role itself
- `feature-map.md` — Feature navigation: name, plain-language purpose, status and document link
- `docs/feature/<feature-id>.md` — One stable current-behavior document per owned system feature: purpose, flowchart and history links; do not invent business features for roles without them

Dated design/change/fix history lives in this role's existing `docs/design/`, `docs/change/`, `docs/fix/`. Current feature files live only in `docs/feature/`, without date prefixes. Preserve the existing docs directory; do not add doc/ or a second features/ tree.
````

## Companion file: `changelog.md`

Each worker role is a directory under `角色卡/` (project root — the directory root name follows the project language: `角色卡/` in Chinese projects, e.g. `role-cards/` in English ones) containing the role card, its module boundary document and governance change history, with owner work documents and an API specification when applicable. The five built-in management roles have no project directory; their reference documents define their default scopes, and each keeps `memo.md` inside its default scope (People Operations uses the governance memo at `角色卡/招募/memo.md`). File names follow the project language:

```
appointment-booking/
├── role-card.md              # 角色卡（worker 角色）← bootstrap 创建
├── boundary.md               # 边界文档: Section 1 白名单，唯一授权源
├── boundary.yaml             # 同名 YAML 同步副本，不单独授权
├── memo.md                   # 本角色的简短事实与续接线索
├── changelog.md              # 角色治理变更日志 ← 仅人事维护
├── functional-description.md # 实际职责、交接与代码/文档位置 ← 角色owner维护
├── api-spec.md               # 实际导出/装配接口报告 ← 适用时由实现owner维护
├── feature-map.md            # 功能导航：用途、状态、链接
└── docs/
    ├── design/               # 详细设计记录
    ├── feature/              # 一功能一份稳定文档：用途、流程图、历史链接
    │   └── <feature-id>.md
    ├── change/               # 变更记录
    └── fix/                  # 修复记录
```

Each worker role maintains its own `memo.md` for dated, sourced work clues; it does not replace project rules or task status. The five built-in management roles keep `memo.md` inside their default scopes; it is a private continuation note, not a role definition or task state, and it does not expand write authority. Read an established project-management role's shared `docs/project-rules.md` when present and check relevant rules. Bootstrap creates the worker role definition and accepted documentation scopes. People Operations records planned ownership; the accepted owner creates `feature-map.md` and grounded current feature files in `docs/feature/`. Pending documents are labeled without broken links. That role owns its implementation-level `docs/architecture.md`; planning owns the architecture design in `docs/planning/`. Do not create architecture JSON or another project-understanding database.

People Operations alone maintains root `changelog.md`, recording every creation, scope update, split, or merge of this role in reverse chronological order. It is protected governance material, not the owner's implementation history. Each entry must index the actual completion document:

```markdown
# Changes: <Role name in project language>

- 2026-09-20: Scope expanded — Section 1 adds pipeline files for async processing. Doc: docs/change/2026-09-20_change_async-pipeline.md
- 2026-09-18: Created — initial role definition. Doc: docs/design/2026-09-18_design_role-setup.md
```

The companion file obeys the same evidence and acceptance gates as the role card itself.

## Work-document permissions before handoff

Every worker role needs explicit Section 1 coverage for its root feature-map, memo and functional-description. The five built-in management roles use their reference default scopes and keep records, including their `memo.md`, there instead. No owned system features means an honest statement in the map, not invented feature pages. A collaboration role describes actual handoffs and document locations without creating unused code layers. API applicability follows [api-spec.md](api-spec.md), with a nonempty responsibility reason for either `required` or `not-applicable`. Communication's default scope stays deliberately narrow: `docs/communication/` for meeting, communication and decision records; never business code, task records, other roles' documents or governance files.

From the scheduler's written team plan, People Operations prepares complete `roleDefinitions` content and role permissions for the listed worker roles and registers the five built-in management roles from their reference documents and default scopes; the scheduler writes the candidate configuration within its own `docs/scheduling/` scope, and owners check applicability. A new project needs no scheduler definition acceptance: a separate fixed scheduler context prepares configuration only; read-only preflight precedes handoff/dispatch of the remaining actual work. Existing projects use their existing scheduler for configuration. People Operations gains no configuration write authority. For worker roles, actual card/boundary paths identify each role root. `requiredWorkDocuments` contains exact expected work-file paths, never directory grants. Before handing off new or adjusted roles, run the read-only [preflight-role](task-operations.md); absent content can be reported without failing valid permission coverage. It does not create files or authorize work. Missing permission returns to People Operations. Task execution still intersects actual Section 1, approved exact writeFiles and node writeSet with the limited own root work files or own bounded docs; governance, peers and state remain protected.

## Relationship

A role card references a module boundary document. The boundary document's Section 1 is the single source of truth for mutation scope. The role card does **not** duplicate, expand, or merge permission sets.

## People Operations

- Every worker role card must reference its module boundary document. Built-in management roles use their reference default scopes and need no project card or boundary.
- Role cards grant context, not mutation authority. Only Section 1 of the referenced boundary document does; a built-in role's reference default scope is its baseline.
- Role cards obey the same evidence and acceptance gates as code changes.

## See also

- [Module boundary document](module-boundary.md)
- [ANS Governed Construction SKILL.md](../SKILL.md)
