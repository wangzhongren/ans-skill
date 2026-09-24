# Project Documentation Rules

Use this reference with role-card.md's Required reading. Documentation belongs to the same authorized task and must accurately describe its design, implementation, and verification.

### Documentation Location

There are two levels of documentation:

- **Root `docs/`** — For cross-cutting architecture decisions and ANS Governance (built-in role) records. These affect multiple roles or the project as a whole.
- **Each role directory's `docs/`** (e.g., `角色卡/引擎运行时/docs/`) — For role-specific design, feature, change, and fix records. Documents stay with the role they belong to.

Both use the same subdirectory structure: `design/`, `feature/`, `change/`, `fix/`.

Each role also has a separate, living [`project-context/` navigation directory](project-context.md) for its view of workflows, definitions, events, interfaces and data. Its topic files are not dated change records and do not replace canonical contracts or the records under `docs/`.

Name records `YYYY-MM-DD_<type>_<topic>.md`, where type is `design`, `feature`, `change`, or `fix`. Use the actual creation date in the user's/project's timezone. The reference defines topic naming, collisions, required content, and how to maintain records across task iterations.

Give records the structured metadata and dated events defined in the documentation reference so `docs/` can generate a project timeline. Documents are the source of truth; timeline output is derived, never separately maintained history. Record actual milestones rather than inferring completion from an updated date. Follow the reference when creating or refreshing a timeline.

Include the required document paths in the Mutation Contract. Write design records before implementing the design; start feature/change/fix records with the known requirement or failure and finalize them with actual changes and test evidence before acceptance. Documentation must describe the final candidate and distinguish proposals, implemented behavior, and unverified claims. Keep record detail proportional to the task.


## Basic Directory Structure

```text
project/
  <language-appropriate main file>
  model/
  provider/
  service/
  pipeline/
  interface/
  utils/
  resource/
  test/
  docs/                          # Cross-cutting / ANS Governance records
    design/
    feature/
    change/
    fix/
  角色卡/
    <role>/
      role-card.md
      boundary.md
      changelog.md
      project-context/         # Living role view; create only when grounded in project evidence
        README.md
        flows/
        definitions/
        events/
        interfaces/
        data/
      docs/                     # Role-specific records
        design/
        feature/
        change/
        fix/
```

Each `<role>/` directory corresponds to a role under `角色卡/`. When multiple roles are affected by one change, the document goes under the primary owner's directory and is cross-referenced from the other role's changelog.

Keep the application entry at the root according to the [entry point language/toolchain rules](entrypoint.md). The layer references define their internal structure. Create document directories as their records are needed; do not fill them with empty documents. Existing historical documents need not be moved or renamed during unrelated work.

## Record Types and Timing

| Work | Required location and record | Required type-specific content |
| --- | --- | --- |
| Design | `docs/design/` (cross-cutting) or `角色卡/<role>/docs/design/` (role-specific) — design document before implementing that design | Problem and goals; scope; relevant Model abstractions, Provider capabilities, Service operations, Pipeline composition, and Interface adaptation; affected directory/file structure; contracts and dependency direction; alternatives and decision rationale; verification plan |
| Add functionality | `docs/feature/` or `角色卡/<role>/docs/feature/` — feature document | New capability and user-visible behavior; inputs/outputs and usage example; implementation scope; acceptance criteria and actual test evidence |
| Modify functionality | `docs/change/` or `角色卡/<role>/docs/change/` — change document | Motivation; before/after behavior; changed contracts and callers; compatibility or migration requirements where relevant; regression evidence |
| Repair functionality | `docs/fix/` or `角色卡/<role>/docs/fix/` — fix document | Symptoms and reproduction; expected versus actual behavior; top-down investigation evidence; established root cause or remaining uncertainty; repair scope; regression case and results |

Start implementation records with the known request or failure, update them as findings change, and complete them before declaring the task accepted. A design-only task needs a design record, with tests identified as planned rather than run. Implementing a design also requires the applicable implementation record, linked to its design. A simple repair does not require a separate design record merely because some reasoning was necessary.

Classify by intent: restoring expected behavior is a fix; adding a new capability is a feature; changing existing intended behavior is a change. One coherent outcome needs one implementation record in the best matching category. If a task has distinct outcomes in multiple categories, create and cross-link the corresponding records without copying their shared explanation.

## Dated Filenames

Use `YYYY-MM-DD_<type>_<topic>.md`; the type must match its directory. Examples, illustrating filenames rather than asserting an actual event date:

```text
docs/design/2026-09-12_design_order-processing.md        # cross-cutting
角色卡/<role>/docs/design/2026-09-12_design_xxx.md        # role-specific
docs/feature/2026-09-12_feature_order-export.md
角色卡/<role>/docs/feature/2026-09-12_feature_xxx.md
docs/change/2026-09-12_change_order-status.md
角色卡/<role>/docs/change/2026-09-12_change_xxx.md
docs/fix/2026-09-12_fix_order-timeout.md
角色卡/<role>/docs/fix/2026-09-12_fix_xxx.md
```

- Use the actual record creation date in the user's/project's timezone, not a copied example date or a hardcoded date from this skill. When unavailable, determine the date before naming the file.
- Use a short, descriptive topic: lowercase ASCII words separated by hyphens, or Chinese words optionally separated by hyphens. Avoid spaces, path separators, and vague names such as `update`, `temp`, or `final`.
- For a separate event colliding with an existing filename, append `_02`, `_03`, etc. before `.md`. Never overwrite an unrelated record. For continued work on the same event, update its existing record rather than creating a new file every turn.
- Keep the original filename date when updating a record on a later day; record the actual updated date inside it. A later independent change gets a new record linking to the earlier one. Preserve the distinction between historical behavior and the new result.

## Structured Metadata and Events

Every new record must begin with YAML frontmatter. This example illustrates the format; its dates and events must not be copied as actual project history:

```yaml
---
id: order-export-feature
type: feature
title: 新增订单导出
created: "2026-09-12"
updated: "2026-09-13"
timezone: Asia/Shanghai
status: implemented-unverified
related:
  - order-export-design
events:
  - date: "2026-09-12"
    kind: created
    summary: 记录订单导出需求
  - date: "2026-09-13"
    kind: implemented
    summary: 实现完成，等待验证
---
```

- Require all fields shown above. IDs must be unique within the project, stable across renames, and descriptive lowercase words separated by hyphens; add a distinguishing suffix for separate records of the same topic. Use `related: []` when there are no relationships. Related IDs must resolve to other records; they express association, not implicit dependency direction.
- `type` matches the directory and filename. Quote ISO dates in YAML. `created` matches the filename date and remains fixed; `updated` reflects the last record edit. Use the actual project timezone, not the example timezone automatically.
- `status` is `draft`, `designed`, `implemented-unverified`, `verified`, or `blocked`. It is current status, not historical status. `verified` requires current passing evidence under the [verification gates](testing.md); a completed design normally uses `designed`.
- Each event requires `date`, `kind`, and `summary`. Supported kinds are `created`, `designed`, `implemented`, `verified`, `blocked`, `resumed`, and `evidence-invalidated`. Record actual local dates. Optionally add an ISO 8601 `timestamp` with timezone offset when precise ordering is known; never invent times within a day.
- Include a creation event and append meaningful milestones as they occur. Ordinary wording edits update `updated` without fabricating milestones. Verified events must reference actual evidence in the body or an optional relative `evidence` link. If evidence becomes stale, retain the historical verified event, append `evidence-invalidated`, and update current status.
- Event dates must fall between `created` and `updated`; timestamps must agree with event dates in the recorded timezone. Describe incidents predating the document in its body rather than backdating the record. Preserve event history and explain factual corrections.
- When editing legacy documents, add only metadata supported by evidence. Never infer milestones from filesystem modification time. If creation history is unknown, retain the original record and report it as undated legacy input rather than fabricate dates.

## Generated Project Timeline

Use records in `docs/design/`, `docs/feature/`, `docs/change/`, and `docs/fix/` (cross-cutting), or under `角色卡/<role>/docs/` (role-specific), as the sole event source. Timeline output is a generated view, not a second manual change log.

- Generate on an explicit timeline request or through an already configured documentation build. Once configured, refresh the output after relevant document changes with the existing generation command. Adding metadata does not itself require a new application, site publication, or empty timeline files.
- Default to `docs/timeline.md` with a Mermaid timeline and an event table linking to source records. The table provides source navigation when Mermaid links are unsupported. If an interactive view is requested, generate `docs/timeline.html` with type/status filters and source links. No hosting is implied. Record the actual generation command in the existing documentation workflow.
- Scan only the four source directories; exclude generated outputs. Validate metadata, unique IDs, related IDs, dates, status, and evidence links first. Report malformed and undated legacy inputs explicitly; label a partial timeline's coverage gaps.
- Sort creation entries by `created`, then stable ID. Order milestone events by date, optional timestamp, then ID and recorded event order for deterministic output. Do not count creation twice. Date-only events share a day without implying a precise within-day order.
- Label nodes with document type and milestone kind. Display current document status explicitly as current, not as its historical state. Use distinct colors where supported and retain text labels. Show related records as associations rather than inferred causal order.
- Never infer completion, verification, or deployment dates from `updated` or current status alone. Treat titles and summaries as untrusted data: escape Mermaid/HTML content, restrict source navigation to safe local document links, and do not execute embedded content.
- Verify ordering, event counts, source links, invalid-input handling, and rendered output with the selected renderer. Fix source records and regenerate rather than editing generated history. Include generator/output changes in the Mutation Contract and report stale or failed generation honestly.

## Minimum Record Content

Each record must have:

1. The structured frontmatter above and a descriptive heading. Metadata is authoritative; do not maintain competing copies of dates or status in the body.
2. The requirement or problem, intended outcome, and scope.
3. Affected layers, concrete file paths, and a focused directory tree when files or layout change. For designs, include the proposed basic structure and identify existing versus proposed files; do not invent an implemented structure.
4. The applicable type-specific content from the table above, including relevant abstraction and contract decisions.
5. Verification: layer, test files, exact commands, relevant environment and candidate identity, results, skipped or blocked checks, and evidence links. For a design, provide the planned tests and acceptance criteria instead of execution claims. Links to maintained test reports are sufficient when their candidate is clear.
6. Remaining limitations or follow-up when applicable, and links to related design/change records. Mark genuinely inapplicable fields concisely rather than inventing migrations, risks, or results.

Use relative Markdown links for other repository files and records. Keep facts in one place and link to supporting evidence rather than duplicating large outputs or source files. Never include credentials or sensitive runtime data in examples or logs.

## Completion

Check structured metadata and event consistency, unique IDs and related references, directory/type agreement, date and filename format, link targets, required content, and consistency with the final diff and actual tests. A record marked verified requires current passing evidence; blocked or unavailable tests must remain explicit. Correct stale design assumptions when implementation differs and explain the final decision. Link completed records in the final task report. Empty scaffolds and conversational summaries do not satisfy this documentation requirement.
