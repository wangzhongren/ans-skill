# Module Boundary Document (模块边界文档)

A module boundary document defines a module's mutation scope. It is the single source of truth for what an AI role may create or modify. A role card's `group` / `组别` is classification only and never merges or expands independent scopes. No group-lead duty grants dispatch or permission authority.

A boundary document lives inside the role directory as `boundary.md`. It contains **only Section 1** — the mutation whitelist. Functional description, architecture, and ownership details go in a separate companion document (`functional-description.md`). Only the built-in Team Formation reference is an exception: it carries its scope and responsibilities directly. Scheduler, project management and independent acceptance follow the same structure, each with its own grants: scheduling records; architecture/shared code/tests; or criteria/acceptance reports. A reusable template grants none of these paths automatically.

## Same-Name YAML Copy

When Team Formation creates or adjusts a boundary, it creates or updates a YAML copy beside it with the same basename and `.yaml` extension, for example `boundary.md` and `boundary.yaml`, in the same delivery. Existing boundaries receive a copy at their next authorized Team Formation maintenance; do not batch-migrate old examples. Markdown is the only maintained and authorized source. YAML is a synchronized copy for readers that need structured data; it is not a second permission source. Do not create YAML copies for other Markdown documents just because they are structured or contain tables.

Use this small structure:

```yaml
source: built-in-boundary.md
section1:
  entries:
    - type: Conditional directory
      path: references/
      purpose: Maintain reference documents for role cards and boundary doc format
      condition: Conditional entries apply only when the task explicitly calls for creating or restructuring roles.
  notes:
    - Conditional entries apply only when the task explicitly calls for creating or restructuring roles. Routine feature work does not authorize governance artifact changes.
```

`source` is the sibling Markdown filename, relative to the YAML file. `section1.entries` has exactly one item per Section 1 table row, in the same order. Preserve each row's original `type`, `path`, and `purpose` text; remove only backticks used for Markdown presentation. Keep alternatives and descriptive or placeholder paths as written. Do not split an alternative into extra entries, normalize a path into a broader directory, or otherwise widen the scope. `condition` is optional and may contain only a condition stated by the source. If a condition also appears outside the table, preserve its full original sentence in `notes` too.

`notes` is an ordered list of the boundary source's non-table statements that affect permission, scope, or precedence. Preserve their original wording and order rather than summarizing them. This includes statements before the table, such as the role's overall scope, and after the table, such as default read-only rules, conditional-entry limits, ownership restrictions, or override precedence. Include the built-in Team Formation reference's role scope and responsibilities there. Do not use notes to add a grant that the Markdown does not contain.

When the Markdown and YAML differ, the mismatch must be fixed in the corresponding Team Formation artifact before the pair is accepted. Existing authorized work continues to use the Markdown boundary. A YAML mismatch never widens access or blocks an already authorized task. `task_ops` currently reads Markdown; do not claim it reads or enforces this YAML. This documentation rule does not add a parser, CLI, configuration system, or program-level permission check.

## Structure

Follow explicit user requirements first, then repository conventions, then language/toolchain conventions. Use OS locale only as a fallback for natural-language prose; never translate identifiers or change filenames solely because of locale.

### Section 1: Modifiable files and directories

The mutation whitelist. A table listing every file or directory the AI may create or modify, tagged by type and function.

| Type | Operable path | Function |
| --- | --- | --- |
| Single file | `src/module/service.py` | Business transformation |
| Owned directory | `src/common/<role-id>/` | Only this role's private helpers and framework code |
| Owned directory | `test/<role-id>/` | This role's assigned tests and test fixtures; no production code |
| Conditional directory | `docs/` | Task-specific documentation only |
| Single file | `角色卡/<role>/feature-map.md` | Owned feature navigation; state when no system feature is owned |
| Single file | `角色卡/<role>/memo.md` | This role's continuation clues |
| Single file | `角色卡/<role>/functional-description.md` | Actual duties, handoffs and document/code locations |
| Single file, when applicable | `角色卡/<role>/api-spec.md` | Real exported/shared capability or assembly-interface report |
| Conditional directory | `角色卡/<role>/docs/feature/` | Stable feature descriptions, flowcharts and history links |
| Conditional directory | `角色卡/<role>/docs/` | Owned design/change/fix history; project management also owns its architecture document |

**Files not listed in or covered by an accepted directory in Section 1 are read-only by default.** To mutate an uncovered file, the AI must first propose updating Section 1 — a change subject to the same evidence and acceptance gates as code changes. Directory entries use explicit project-relative paths and responsibilities, not a blanket `src/` or `common/` grant. Ownership must not overlap, including a file grant inside another role's directory.

For the project management role, the common-code directory is `src/common/shared/`, with its corresponding test directory and its own `docs/architecture/shared-components.md` and `docs/architecture.md`. It cannot claim every role's common directory. See [shared-directories.md](shared-directories.md).

New role boundaries use feature-map and existing docs scopes; do not require architecture JSON or project-understanding SQLite entries. If the user explicitly works with a legacy SQLite store, any existing accepted row scope still covers only that role's rows, not schema changes or peers' records. Documents and diagrams do not grant write permissions. Legacy viewers remain opt-in and cannot expand authority.

### Role work documents and protected governance

Explicitly cover each project role's own `feature-map.md`, `memo.md` and `functional-description.md` by exact root file paths. Include `api-spec.md` when real exported/shared capabilities or assembly interfaces make it applicable. Collaboration roles describe actual duties and document handoffs; an explicit, evidenced API non-applicability decision avoids invented code or exports. Add only actual bounded own docs scopes. These grants do not open the entire role directory.

Role cards, boundaries, synchronized YAML and root governance changelog remain Team Formation-owned. Other roles' roots and files, `.ans/`, task/scheduling state and custom registered governance paths stay protected from ordinary execution even if a broad common/test/docs entry would contain them. Legitimate scheduler management scopes may participate in complete ownership checks, but state still changes only through Store, never ordinary execution writeFiles. Check directory intersections across all registered actual Section 1 permissions before selecting current files, including nested role roots, protected filenames under docs and prefix-similar paths. Preserve existing exact business-source and private common/test rules.

The existing configuration's complete `roleDefinitions.requiredWorkDocuments` lists exact expected files for [read-only preflight](task-operations.md); it grants nothing and does not restrict future dated docs already covered by accepted directories. Actual task work files must additionally be precise approved writeFiles and node writeSet entries. Missing paths return to Team Formation; preflight cannot edit Section 1. Markdown remains the sole authority and YAML remains its synchronized copy.

### Private abstractions

Within its Section 1 files and accepted private common directory, a role may create helpers, utilities, and internal types without listing each symbol or new internal filename in Section 1. These are private to that role. Start local when the current task is local; a concrete cross-role reuse need goes to project management. There is no mandatory minimum caller count. Domain contracts still belong to Model or their relevant layer.

### Companion file: `functional-description.md`

Role-local module notes and key code locations live in `functional-description.md`; each role's private work clues live in its own `memo.md`. Project-wide engineering constraints belong in project management's `docs/project-rules.md` and require an explicit Section 1 path. The companion description links the feature-map rather than duplicating feature flows. Project management owns overall architecture in its own `docs/architecture.md`. Current behavior and history navigation for each feature live in `docs/feature/<feature-id>.md`; see [feature-point.md](feature-point.md).

## Team Formation

- Layer business source remains listed by exact file. The exception is an explicitly owned `common/<role-id>/` or project-owned `common/shared/` subtree. Dedicated role-owned test directories, including the fixed test role's integration/regression directory, may also be granted explicitly. Supporting and governance locations (`docs/`, role directories, the skill's own `references/`) may use bounded directory entries.
- Adding or removing files inside an accepted directory does not require a boundary rewrite. Adding a new directory scope, changing an owner or adding/removing individually listed paths requires Team Formation to update Section 1. Editing the content of an already permitted file does not require a boundary rewrite. Task scope and customer-confirmed designs still apply to both forms of ownership.
- The boundary document obeys the same evidence and acceptance gates as code changes.

## See also

- [Role card](role-card.md)
- [ANS Governed Construction SKILL.md](../SKILL.md)
