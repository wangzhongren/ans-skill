# Role Card (角色卡)

A role card identifies one agent role and its scope boundary. It is the entry point for every task under that role.

## Format

The implementation template below is for capability and assembly roles. Governance creates the default project card using [project-role.md](project-role.md), with accepted design and scheduling scopes; do not copy business implementation checkpoints into it.

The template below is in English for readability. Follow explicit user requirements first, then repository conventions, then language/toolchain conventions. Use OS locale only as a fallback for natural-language prose; never translate identifiers or change filenames solely because of locale.

````markdown
# <Role name in project language>

<Short description in project language>

## System features owned by this role

| Feature | Current status | How it works |
| --- | --- | --- |
| <System feature a user can trigger> | Planned / implemented / needs verification | `features/<feature-id>.md` (link after creation) |

List only current or planned system features for which this role is the primary owner, not role duties such as coding or testing. Mark planned features as planned; use `None yet` when the role owns no system feature. Follow [feature-point.md](feature-point.md). Each feature gets its own current-behavior document after the owning role is accepted; until then show `待补文档` as plain text instead of a broken link. This list does not grant permission to change files.

## Required reading

1. `<boundary-doc in project language>` — Section 1 is the mutation whitelist.
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
8. This role's overview from the shared project-understanding store, when present, and only the topics relevant to the assignment. Query with this role's ID; verify claims against current code and contracts. Follow [project-context.md](project-context.md).
9. The feature-point document for the assigned system feature, when present. Check its current behavior against source and tests before changing it.

For the assembly role, additionally read:
- `references/entrypoint.md` — Application entry and lifecycle rules
- `references/api-spec.md` — API specification format (reads participating roles' api-spec.md before wiring)

> During bootstrap, the ANS Governance role generates a tailored Required reading for each role, including only the references relevant to that role's capabilities. Not every role needs all references listed above.
>
> For a trivial repair confined to one file and one layer with no contract change, still load and activate the role card and its boundary Section 1; the additional layer reading may be limited to that layer's reference plus `references/testing.md`. The dependency rules in `references/architecture.md` and both verification gates still apply.

## Execution principles

- Section 1 of the referenced boundary document is the only mutation authority.
- Modify only what the task requires.
- Cross-scope changes go back to the client.
- Default readonly — unlisted files are read-only unless Section 1 says otherwise.
- **Implementation order** (`Model -> Provider -> Service -> Pipeline -> Interface`) applies to affected work within the role; cross-role work additionally waits for its actual dependencies and agreed contracts.
- **Execution assignment:** For coordinated work, the accepted project scheduler dispatches this role according to bootstrap-workflow.md and scheduler.md. Do not spawn child agents or independently schedule peers. Return unmet dependencies or scope requests to the scheduler. For a standalone task, the role still requires customer consent or applicable configuration preauthorization. It cannot activate itself, switch to another role, or create workers. Parallel work requires disjoint writes, agreed contracts, ready dependencies, and available authorized agents; otherwise use sequential role switching. Assembly may prepare build/test configuration early and integrates participating implementations after their gates pass.

## Quality constraints

**Adjacent-layer compliance:** Interface imports Pipeline only; Pipeline imports Service public entry only; Service imports Provider public entry only. No re-exporting lower-layer APIs.

**Code quality:** Implemented operations must fulfill their contracts; no unfinished stubs presented as complete. Semantically intentional no-op hooks are allowed under checkpoint 3c. Variable names are descriptive (no single/two-letter abbreviations beyond loop counters). No ternary operators — use `if/else`. Every `try/catch` must output the error. No accessing internal properties from outside the class.

**Testing:** Tests go under the project's language-native test files grouped by owning role where the runner permits. Complete each layer's tests before integrating dependent implementation with it; independent preparation against agreed contracts may proceed without claiming integration success.

## Execution checkpoints

1. **Prepare:** Check existing authorization, gather sufficient evidence, choose the smallest effective action. Load all references listed in Required reading. Inspect the requirement and baseline; load affected layers and supporting references before fixing the mutation scope.
1a. **Explain before coding:** For an application-code or test change, write the appropriate dated document first and show its short summary to the customer. Distinguish task-required changes from optional hardening, compatibility or speculative additions in both places. Default-checked options remain pending until the customer's confirmed implementation scope includes those item IDs or the displayed selection. Wait for confirmation of that document plus instruction to implement it, unless the same version, scope and optional selection have already been confirmed and authorized. A question or silence is not confirmation; read-only investigation and document refinement may continue.
2. **Build:** Design and implement affected work in build order: **Model → Provider → Service → Pipeline → Interface**. Assess abstractions first. Reuse satisfactory existing layers. Investigate from the highest relevant failing entry downward; root startup problems begin at main.
3. **Test each layer:** Complete each affected layer's required tests before integrating dependent implementation with it; independent preparation against agreed contracts may proceed without claiming integration success. Skipped, unavailable, or unresolved checks do not pass.
3b. **Verify adjacent-layer compliance:** Inspect every import and constructor call in changed files. Confirm: Interface imports Pipeline only; Pipeline imports Service public entry only; Service imports Provider public entry only. Re-exporting a lower-layer API or handing a lower-layer object to a higher layer counts as a violation. Fix any violation before proceeding.
3c. **Code quality gates:** Every implemented method must have a real body — no empty stubs with `// TODO` or "implemented elsewhere" comments. A method that is intentionally a no-op (e.g., an optional callback hook) is allowed only when its purpose is clear from its name and the no-op is semantically meaningful (`onCollision() {}` is fine; `update(dt) {}` with no comment is not). Variable names must be descriptive — no single-letter or two-letter abbreviations beyond loop counters (`i`, `j`). Do not compress multiple statements onto a single line unless they are trivially related (`if (x) return;` is fine; `a(); b(); c()` on one line is not). Do not access an object's internal properties from outside its class — expose a method instead.

    **Additional quality rules:**
    - **Error handling:** Every `try/catch` must output the error — log it, rethrow, or return an error result. Silent empty catches are forbidden.
    - **Readability:** Ternary operators (`condition ? a : b`) are forbidden — they reduce review readability. Use `if/else` instead.
    - **Test structure:** `test/` mirrors the role structure under `角色卡/`, using the project's language-native test files grouped by owning role where the runner permits. Tests are grouped by role, not by layer.
4. **Explain the change to a reader.** Write the relevant dated design, feature, change or fix document using that type's guide. Lead with its real scenario and result; keep test conclusions short and link detailed evidence. Create deliverables (`changelog.md`, `functional-description.md`, `api-spec.md`) at the role directory root. Create or refresh relevant rows in the shared project-understanding store through its CRUD CLI when verified understanding changes, within this role's accepted logical row scope. Before adding, removing, or reorganizing owned application files outside the accepted scope, report the requested boundary change to Scheduler for Governance handling. Resume only after the accepted scope and assignment are updated; do not self-expand authority. Capability roles maintain their own implementation reports in their accepted documentation scope; they do not grant themselves more authority.
   If the current behavior of a system feature changed, update its `features/<feature-id>.md` after verification. Keep the dated document as the history of this particular change. If feature ownership or the role-card list must change, request a Governance update; the execution role does not edit its own role card. Follow [feature-point.md](feature-point.md).
5. **Return stage evidence.** Follow the coordination.md worker-report protocol: include a stable report ID, task/node/attempt identity, the actual requirement/design/boundary revisions used, and any help needed. The default project role feeds the shared Dashboard; do not create a separate viewer for this worker. Do not write the shared project table; wait for the project role to acknowledge feedback and design revisions. For coordinated work, report the assigned node ID, changed paths, final candidate identity, artifact links, exact check results, and unresolved dependencies to Scheduler. Scheduler validates the release conditions; reporting completion does not itself mark a node verified. For a standalone task, report the same evidence directly without inventing a scheduling node.
6. **Verify acceptance.** Apply evidence invalidation and acceptance rules before the final report. A verified candidate requires authorized changed paths, passing applicable gates, current evidence and required documentation. Verification does not authorize commits, pushes, publication, deployment, merges, or external mutations.

`utils/`, `resource/`, `test/`, `docs/`, and the root startup file support the five-layer architecture; they do not add operational layers. Routine tasks do not generate or refresh code-atlas artifacts. Use targeted source inspection for dependency questions; atlas tools are explicit opt-in only.

## Communication

1. Write for someone learning to program. State what the user does and what the software changes, in short concrete sentences. Explain a necessary technical term when it first appears. Do not hide a missing explanation behind broad phrases such as "processes the request" or "from entry to result".
2. For several findings, changes, or steps, prefer a short numbered list (`1.`, `2.`, `3.`, `4.`), one point per item. Do not pad an answer to four items or force a list for a single fact.
3. Report what changed, the actual verification result, and any material limitation or next action. Link detailed evidence instead of repeating logs or narrating every tool call. Keep the final response self-contained.
4. Give progress updates for meaningful findings, changes of direction, completion, or required user action. Avoid repeated status messages, unnecessary confirmations, jargon, and long preambles. Brevity must not hide uncertainty, failed checks, or incomplete work.

## Deliverables

When implementation is complete, create these documents at the role directory root (same level as `role-card.md`):

- `changelog.md` — Change history with date, description, and doc reference
- `functional-description.md` — Architecture diagrams, key code locations, detailed explanation
- `api-spec.md` — Actual exports, dependencies, assembly notes, design contract ID/revision, compliance/deviations and test evidence; shared integration design remains project-role-owned
- `features/<feature-id>.md` — One current-behavior document for each system feature primarily owned by this role; do not create filler files for roles with no system feature

Detailed design, feature, change, and fix records go into `docs/design/`, `docs/feature/`, `docs/change/`, `docs/fix/` respectively.
````

## Companion file: `changelog.md`

Each role is a directory under `角色卡/` (project root — the directory root name follows the project language: `角色卡/` in Chinese projects, e.g. `role-cards/` in English ones) containing the role card, its module boundary document, a companion change history file, and an API specification. File names follow the project language:

```
appointment-booking/
├── role-card.md              # 角色卡 ← bootstrap 创建
├── boundary.md               # 边界文档: Section 1 白名单 ← bootstrap 创建
├── changelog.md              # 变更日志 ← 角色实现阶段创建（角色根目录）
├── functional-description.md # 功能描述: 图 + 代码位置 + 详解 ← 角色实现阶段创建（角色根目录）
├── api-spec.md               # API 规范: 导出 + 依赖 + 装配说明 ← 角色实现阶段创建（角色根目录）
├── features/                 # 本角色负责的系统功能点；一功能一文档（有内容时创建）
│   └── <feature-id>.md        # 当前怎样触发、运行、分支和结束
└── docs/
    ├── design/               # 详细设计记录
    ├── feature/              # 功能记录
    ├── change/               # 变更记录
    └── fix/                  # 修复记录
```

Bootstrap creates only the role definition: `role-card.md` and `boundary.md`. It lists planned or source-identified system features in the card, but their current-behavior documents are created by the accepted owning role within its `features/` scope. A planned path may be shown as plain text with `待补文档` until the file exists; do not leave a broken link. Other role documents are also created by the owning role when grounded in actual project evidence. The project-understanding database is created on first authorized use, and a role needs an accepted logical row-scope entry in Section 1 before writing its rows.

`changelog.md` records every creation, scope update, split, or merge of this role in reverse chronological order. Each entry must index the actual completion document:

```markdown
# Changes: <Role name in project language>

- 2026-09-20: Scope expanded — Section 1 adds pipeline files for async processing. Doc: docs/feature/async-pipeline.md
- 2026-09-18: Created — initial role definition. Doc: docs/design/architecture.md
```

The companion file obeys the same evidence and acceptance gates as the role card itself.

## Relationship

A role card references a module boundary document. The boundary document's Section 1 is the single source of truth for mutation scope. The role card does **not** duplicate, expand, or merge permission sets.

## Governance

- Every role card must reference its module boundary document.
- Role cards grant context, not mutation authority. Only Section 1 of the referenced boundary document does.
- Role cards obey the same evidence and acceptance gates as code changes.

## See also

- [Module boundary document](module-boundary.md)
- [ANS Governed Construction SKILL.md](../SKILL.md)
