# Module Boundary Document (模块边界文档)

A module boundary document defines a module's mutation scope. It is the single source of truth for what an AI role may create or modify.

A boundary document lives inside the role directory as `boundary.md`. It contains **only Section 1** — the mutation whitelist. Functional description, architecture, and ownership details go in a separate companion document (`functional-description.md`). Only the built-in Governance reference is an exception: it carries its scope and responsibilities directly. Project management follows the same structure, with separate grants for design, execution records, shared code and its tests.

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
| Single file | `角色卡/<role>/feature-map.md` | Navigation for owned system features |
| Conditional directory | `角色卡/<role>/docs/feature/` | Stable feature descriptions, flowcharts and history links |
| Conditional directory | `角色卡/<role>/docs/` | Owned design/change/fix history; project management also owns its architecture document |

**Files not listed in or covered by an accepted directory in Section 1 are read-only by default.** To mutate an uncovered file, the AI must first propose updating Section 1 — a change subject to the same evidence and acceptance gates as code changes. Directory entries use explicit project-relative paths and responsibilities, not a blanket `src/` or `common/` grant. Ownership must not overlap, including a file grant inside another role's directory.

For the project management role, the common-code directory is `src/common/shared/`, with its corresponding test directory and its own `docs/architecture/shared-components.md` and `docs/architecture.md`. It cannot claim every role's common directory. See [shared-directories.md](shared-directories.md).

New role boundaries use feature-map and existing docs scopes; do not require architecture JSON or project-understanding SQLite entries. If the user explicitly works with a legacy SQLite store, any existing accepted row scope still covers only that role's rows, not schema changes or peers' records. Documents and diagrams do not grant write permissions. Legacy viewers remain opt-in and cannot expand authority.

### Private abstractions

Within its Section 1 files and accepted private common directory, a role may create helpers, utilities, and internal types without listing each symbol or new internal filename in Section 1. These are private to that role. Start local when the current task is local; a concrete cross-role reuse need goes to project management. There is no mandatory minimum caller count. Domain contracts still belong to Model or their relevant layer.

### Companion file: `functional-description.md`

Role-local module notes and key code locations live in `functional-description.md`; it links the feature-map rather than duplicating feature flows. Project management owns overall architecture in its own `docs/architecture.md`. Current behavior and history navigation for each feature live in `docs/feature/<feature-id>.md`; see [feature-point.md](feature-point.md).

## Governance

- Layer business source remains listed by exact file. The exception is an explicitly owned `common/<role-id>/` or project-owned `common/shared/` subtree. Dedicated role-owned test directories, including the fixed test role's integration/regression directory, may also be granted explicitly. Supporting and governance locations (`docs/`, role directories, the skill's own `references/`) may use bounded directory entries.
- Adding or removing files inside an accepted directory does not require a boundary rewrite. Adding a new directory scope, changing an owner or adding/removing individually listed paths requires Governance to update Section 1. Editing the content of an already permitted file does not require a boundary rewrite. Task scope and customer-confirmed designs still apply to both forms of ownership.
- The boundary document obeys the same evidence and acceptance gates as code changes.

## See also

- [Role card](role-card.md)
- [ANS Governed Construction SKILL.md](../SKILL.md)
