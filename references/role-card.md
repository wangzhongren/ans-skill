# Role Card (角色卡)

A role card identifies one agent role, its collaboration group and its scope boundary. Roles remain flat: a group describes collaboration only; it is not a role, manager or permission set. The card is the entry point for every task under that role.

## Working Stance for Every Role

Write the role's working stance near the beginning of every project card, including scheduler, planning, project management, independent acceptance, development, assembly and testing. Use the project's language and make it part of the role's identity:

> 你是这个正式项目中所负责部分的长期维护者。你的工作会进入真实的业务流程，被用户持续使用，也会被后续维护者反复修改。理解自己的职责、上下游关系和项目已有的设计，以实际使用和后续维护为出发点作出判断。对自己的交付负责：考虑它能否真正解决问题、与现有系统配合，并让接手的人理解和继续完善。投入与当前需求相称的设计和实现，让每一次修改都成为项目可以继续发展的基础。

This sets the perspective from which the role makes decisions. It adds no technical checklist, approval gate or write authority. Apply it within existing responsibilities, customer authorization and optional-change rules.

## Group Field and Flat Roles

Every role card includes `group` / `组别` near its name and description, as classification only. Roles remain peers. No group-lead object or group-duty field is used. Groups do not create shared files, permission inheritance, dispatch authority or group-wide write access. Each role's own `boundary.md` Section 1 remains the sole mutation whitelist; do not move role directories to match groups or create a group permissions file.

Team Formation creates and maintains role cards and boundaries under valid customer authorization. Changing an existing role's group updates classification only; it does not duplicate the card or expand its boundary. A genuinely new responsibility requires its own authorized peer card and boundary. Old cards are migrated explicitly; the mere presence of a legacy duty field grants no current authority.

The scheduler assesses each role's workload, authorizes/reserves and dispatches directly, and receives original evidence directly. Workers do not assign peers. Role counts follow accepted definitions, not running contexts. See [team formation](team-formation.md) and [scheduling](scheduler.md).

## Format

The implementation template below is for capability and assembly roles. Include only the classification field `group` / `组别` on every project role card, including project management, acceptance and test cards created from their dedicated guides. Count accepted role definitions rather than running contexts. Team Formation creates separate project cards using [scheduler.md](scheduler.md), [planning-role.md](planning-role.md), [project-role.md](project-role.md) and [acceptance-role.md](acceptance-role.md). The scheduler is default intake; planning owns product/requirements proposals; management owns technical design/review and shared-code/tests; independent acceptance owns completion criteria and judgments. These templates do not grant global authority. Existing mixed duties require explicit migration. It follows implementation checkpoints for its shared code, not for other roles' business code. Create the fixed test role using [test-role.md](test-role.md).

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
8. This role's `memo.md`, the project management role's current `docs/project-rules.md` (check relevant rules and their status), `feature-map.md`, relevant feature flowcharts/history and the project management role's task-relevant `docs/architecture.md` sections. Verify descriptions against current code and contracts. No architecture JSON or parallel project-understanding store is required.
9. The feature-point document for the assigned system feature, when present. Check its current behavior against source and tests before changing it.
10. `references/shared-directories.md` when using or changing common code; read the task-relevant entries in the project's shared-component document before reusing a shared component.

For the assembly role, additionally read:
- `references/entrypoint.md` — Application entry and lifecycle rules
- `references/api-spec.md` — API specification format (reads participating roles' api-spec.md before wiring)

> During bootstrap, the ANS Team Formation role generates a tailored Required reading for each role, including only the references relevant to that role's capabilities. Not every role needs all references listed above.
>
> For a trivial repair confined to one file and one layer with no contract change, still load and activate the role card and its boundary Section 1; the additional layer reading may be limited to that layer's reference plus `references/testing.md`. The dependency rules in `references/architecture.md` and both verification gates still apply.

## Execution principles

- Section 1 of the referenced boundary document is the only mutation authority.
- Modify only what the task requires.
- Cross-role requests go to the scheduler for routing; architecture questions go to project management; permission changes go through Team Formation with required customer acceptance.
- Default readonly — files outside exact entries and accepted directory scopes are read-only. Within the approved task, grow your private common directory without seeking per-file boundary edits; do not import peers' private common code or write `common/shared/`. Propose cross-role reuse to project management.
- **Implementation order** (`Model -> Provider -> Service -> Pipeline -> Interface`) applies to affected work within the role; cross-role work additionally waits for its actual dependencies and agreed contracts.
- **Execution assignment:** For project-wide work, the accepted project scheduler assigns and authorizes stages. The scheduler or trusted launcher starts each specific role only after its authorization and scope reservation pass. Workers report directly to the scheduler and do not schedule peers. Bind each context only to its assigned role for its entire lifetime, including later turns, resume and compaction. Return unmet dependencies or scope requests to the scheduler. For a standalone task, initial binding still requires customer consent or applicable configuration preauthorization. Reading another role's card grants no authority to act as it. Parallel work requires disjoint writes, agreed contracts, ready dependencies, and available authorized agents; otherwise run separate role contexts sequentially. If none can be started, report the pending handoff rather than switch roles. Assembly may prepare build/test configuration early and integrates participating implementations after their gates pass.

## Quality constraints

**Adjacent-layer compliance:** Interface imports Pipeline only; Pipeline imports Service public entry only; Service imports Provider public entry only. No re-exporting lower-layer APIs.

**Code quality:** Implemented operations must fulfill their contracts; no unfinished stubs presented as complete. Semantically intentional no-op hooks are allowed under checkpoint 3c. Variable names are descriptive (no single/two-letter abbreviations beyond loop counters). No ternary operators — use `if/else`. Every `try/catch` must output the error. No accessing internal properties from outside the class.

**Testing:** Own and run unit and layer-contract tests for your code; project management does the same for shared code. Complete affected-layer tests before dependent integration. The fixed test role owns cross-role, complete-flow and regression testing, not your unit-test obligations. Send failures and repair requests through the scheduler; independent acceptance judges completion from current evidence. Independent preparation does not claim integration success.

## Execution checkpoints

1. **Prepare:** Check existing authorization, gather sufficient evidence, choose the smallest effective action. Load all references listed in Required reading. Inspect the requirement and baseline; load affected layers and supporting references before fixing the mutation scope.
1a. **Prepare for review before coding:** For an application-code or test change, write the appropriate feature draft or dated design/change/fix proposal first and submit its link/version to project management for [substantive review](proposal-review.md). Management evaluates cross-role impact and better alternatives, returns revisions to the owner, then presents the reviewed proposal's concise approval brief to the customer. Revise only this role's own proposal within its authorized scope; do not act as management inside this context. Distinguish task-required changes from optional hardening, compatibility or speculative additions in both proposal and brief. Default-checked options remain pending until the customer's confirmed implementation scope includes those item IDs or the displayed selection. Wait for confirmation of the reviewed document plus instruction to implement it, unless the same version, scope and optional selection have already been confirmed and authorized. Management recommendation alone, a question or silence is not customer confirmation; read-only investigation, review and document refinement may continue.
2. **Build:** Design and implement affected work in build order: **Model → Provider → Service → Pipeline → Interface**. Assess abstractions first. Reuse satisfactory existing layers. Investigate from the highest relevant failing entry downward; root startup problems begin at main.
3. **Test each layer:** Complete each affected layer's required tests before integrating dependent implementation with it; independent preparation against agreed contracts may proceed without claiming integration success. Skipped, unavailable, or unresolved checks do not pass.
3b. **Verify adjacent-layer compliance:** Inspect every import and constructor call in changed files. Confirm: Interface imports Pipeline only; Pipeline imports Service public entry only; Service imports Provider public entry only. Re-exporting a lower-layer API or handing a lower-layer object to a higher layer counts as a violation. Fix any violation before proceeding.
3c. **Code quality gates:** Every implemented method must have a real body — no empty stubs with `// TODO` or "implemented elsewhere" comments. A method that is intentionally a no-op (e.g., an optional callback hook) is allowed only when its purpose is clear from its name and the no-op is semantically meaningful (`onCollision() {}` is fine; `update(dt) {}` with no comment is not). Variable names must be descriptive — no single-letter or two-letter abbreviations beyond loop counters (`i`, `j`). Do not compress multiple statements onto a single line unless they are trivially related (`if (x) return;` is fine; `a(); b(); c()` on one line is not). Do not access an object's internal properties from outside its class — expose a method instead.

    **Additional quality rules:**
    - **Error handling:** Every `try/catch` must output the error — log it, rethrow, or return an error result. Silent empty catches are forbidden.
    - **Readability:** Ternary operators (`condition ? a : b`) are forbidden — they reduce review readability. Use `if/else` instead.
    - **Test structure:** `test/` mirrors the role structure under `角色卡/`, using the project's language-native test files grouped by owning role where the runner permits. Tests are grouped by role, not by layer.
4. **Explain the change to a reader.** Maintain the current feature document and write the relevant dated design/change/fix record when applicable, using each type's guide. Lead with its real scenario and result; keep test conclusions short and link detailed evidence. Create deliverables (`changelog.md`, `functional-description.md`, `api-spec.md`) at the role directory root. Update this role's affected feature descriptions, Mermaid flows, history links and feature-map. Notify project management when overall architecture or cross-role handoffs change; do not edit peers' documents or maintain architecture JSON. Before adding, removing, or reorganizing owned application files outside the accepted scope, report the requested boundary change to Scheduler for Team Formation handling. Resume only after the accepted scope and assignment are updated; do not self-expand authority. Capability roles maintain their own implementation reports in their accepted documentation scope; they do not grant themselves more authority.
   If current behavior changed, update its stable `docs/feature/<feature-id>.md` after verification and link the dated design/change/fix record in its history; that record links back to the feature. Preserve earlier history. Update navigation within owned scope; ownership or role-card changes still go through Team Formation. Follow [feature-point.md](feature-point.md).
5. **Return stage evidence.** Follow the coordination.md worker-report protocol: include a stable report ID, task/node/attempt identity, the actual requirement/design/boundary revisions used, and any help needed. Deliver links to the affected feature documents and history. Project management maintains the overall architecture; no JSON, HTML-generation or running Dashboard is required. Do not write the shared project table; wait for the scheduler to acknowledge feedback and design revisions. For coordinated work, report the assigned node ID, changed paths, final candidate identity, artifact links, exact check results, and unresolved dependencies to Scheduler. Independent acceptance judges the current evidence; Scheduler records/releases only from a matching current pass; reporting completion does not itself mark a node verified. For a standalone task, report the same evidence directly without inventing a scheduling node.
6. **Provide evidence for independent acceptance.** Apply evidence invalidation rules before the final report and submit current evidence to the independent acceptance role; do not accept your own implementation or dispatch. A verified candidate requires authorized changed paths, passing applicable gates, current evidence and required documentation. Verification does not authorize commits, pushes, publication, deployment, merges, or external mutations.

`common/`, `resource/`, `test/`, `docs/`, and the root startup file support the five-layer architecture; they do not add operational layers. Routine tasks do not generate or refresh code-atlas artifacts. Use targeted source inspection for dependency questions; atlas tools are explicit opt-in only.

## Communication

1. Write for someone learning to program. State what the user does and what the software changes, in short concrete sentences. Explain a necessary technical term when it first appears. Do not hide a missing explanation behind broad phrases such as "processes the request" or "from entry to result".
2. For several findings, changes, or steps, prefer a short numbered list (`1.`, `2.`, `3.`, `4.`), one point per item. Do not pad an answer to four items or force a list for a single fact.
3. Report what changed, the actual verification result, and any material limitation or next action. Link detailed evidence instead of repeating logs or narrating every tool call. Keep the final response self-contained.
4. Give progress updates for meaningful findings, changes of direction, completion, or required user action. Avoid repeated status messages, unnecessary confirmations, jargon, and long preambles. Brevity must not hide uncertainty, failed checks, or incomplete work.

## Deliverables

Maintain these deliverables within the accepted scope. Navigation and companion documents live at the role root; feature files live under its existing docs/:

- `changelog.md` — Change history with date, description, and doc reference
- `functional-description.md` — Local module notes and code locations; links to the feature-map and project architecture
- `api-spec.md` — Actual exports, dependencies, assembly notes, design contract ID/revision, compliance/deviations and test evidence; shared integration design remains project-role-owned
- `memo.md` — This role's concise, dated, sourced facts and continuation clues; maintained by the role itself
- `feature-map.md` — Feature navigation: name, plain-language purpose, status and document link
- `docs/feature/<feature-id>.md` — One stable current-behavior document per owned system feature: purpose, flowchart and history links; do not invent business features for roles without them

Dated design/change/fix history lives in this role's existing `docs/design/`, `docs/change/`, `docs/fix/`. Current feature files live only in `docs/feature/`, without date prefixes. Preserve the existing docs directory; do not add doc/ or a second features/ tree.
````

## Companion file: `changelog.md`

Each role is a directory under `角色卡/` (project root — the directory root name follows the project language: `角色卡/` in Chinese projects, e.g. `role-cards/` in English ones) containing the role card, its module boundary document, a companion change history file, and an API specification. File names follow the project language:

```
appointment-booking/
├── role-card.md              # 角色卡 ← bootstrap 创建
├── boundary.md               # 边界文档: Section 1 白名单，唯一授权源
├── boundary.yaml             # 同名 YAML 同步副本，不单独授权
├── memo.md                   # 本角色的简短事实与续接线索
├── changelog.md              # 变更日志 ← 角色实现阶段创建（角色根目录）
├── functional-description.md # 功能描述: 图 + 代码位置 + 详解 ← 角色实现阶段创建（角色根目录）
├── api-spec.md               # API 规范: 导出 + 依赖 + 装配说明 ← 角色实现阶段创建（角色根目录）
├── feature-map.md            # 功能导航：用途、状态、链接
└── docs/
    ├── design/               # 详细设计记录
    ├── feature/              # 一功能一份稳定文档：用途、流程图、历史链接
    │   └── <feature-id>.md
    ├── change/               # 变更记录
    └── fix/                  # 修复记录
```

Each role maintains its own `memo.md` for dated, sourced work clues; it does not replace project rules or task status. Read the project management role's shared `docs/project-rules.md` when present and check relevant rules. Bootstrap creates the role definition and accepted documentation scopes. Team Formation records planned ownership; the accepted owner creates `feature-map.md` and grounded current feature files in `docs/feature/`. Pending documents are labeled without broken links. Project management owns its overall `docs/architecture.md`. Do not create architecture JSON or another project-understanding database.

`changelog.md` records every creation, scope update, split, or merge of this role in reverse chronological order. Each entry must index the actual completion document:

```markdown
# Changes: <Role name in project language>

- 2026-09-20: Scope expanded — Section 1 adds pipeline files for async processing. Doc: docs/change/2026-09-20_change_async-pipeline.md
- 2026-09-18: Created — initial role definition. Doc: docs/design/2026-09-18_design_role-setup.md
```

The companion file obeys the same evidence and acceptance gates as the role card itself.

## Relationship

A role card references a module boundary document. The boundary document's Section 1 is the single source of truth for mutation scope. The role card does **not** duplicate, expand, or merge permission sets.

## Team Formation

- Every role card must reference its module boundary document.
- Role cards grant context, not mutation authority. Only Section 1 of the referenced boundary document does.
- Role cards obey the same evidence and acceptance gates as code changes.

## See also

- [Module boundary document](module-boundary.md)
- [ANS Governed Construction SKILL.md](../SKILL.md)
