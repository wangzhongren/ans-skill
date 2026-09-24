# Module Boundary Document (模块边界文档)

A module boundary document defines a module's mutation scope. It is the single source of truth for what an AI role may create or modify.

A boundary document lives inside the role directory as `boundary.md`. It contains **only Section 1** — the mutation whitelist. Functional description, architecture, and ownership details go in a separate companion document (`functional-description.md`). Only the built-in Governance reference is an exception: it carries its scope and responsibilities directly. The project scheduler follows the ordinary role-card, boundary Section 1, and companion-document structure; its scope covers execution records, not application ownership.

## Structure

Follow explicit user requirements first, then repository conventions, then language/toolchain conventions. Use OS locale only as a fallback for natural-language prose; never translate identifiers or change filenames solely because of locale.

### Section 1: Modifiable files and directories

The mutation whitelist. A table listing every file or directory the AI may create or modify, tagged by type and function.

| Type | Operable path | Function |
| --- | --- | --- |
| Single file | `src/module/service.py` | Business transformation |
| Conditional directory | `docs/` | Task-specific documentation only |
| Logical row scope | `project-context/context.sqlite3`, `role_id=<role>` | This role's understanding rows, only through `context_store.py` |

**Files not listed in Section 1 are read-only by default.** To mutate an unlisted file, the AI must first propose updating Section 1 — a change subject to the same evidence and acceptance gates as code changes.

The shared project-understanding SQLite file is a narrow supporting-artifact exception to file-exclusive ownership: each accepted role can own only its `role_id` rows. This row scope does not cover schema changes, other roles' rows, raw SQL, or direct file edits. The CRUD tool checks role filters and revisions, but cannot authenticate the human or active AI role; the accepted boundary and dispatch authorization remain necessary.

### Private abstractions

Within its Section 1 files, a role may create helpers, utilities, and internal types without declaring them in Section 1 or any shared ownership registry. These are **private abstractions** — invisible to other roles and governed only by the role's own code quality constraints. Prefer a private abstraction over creating a shared one until a second consumer emerges.

### Companion file: `functional-description.md`

Architecture diagrams, key code locations, detailed explanations, and ownership tables live in `functional-description.md` — a separate file in the same role directory. See [functional-description.md](functional-description.md) for the format.

## Governance

- Section 1 must list specific application source files, not wildcard directories. Supporting and governance locations (`docs/`, role directories, the skill's own `references/`) may use directory-scoped or conditional entries.
- Adding or removing a file from a capability must update Section 1. A mismatch is a documentation gap.
- The boundary document obeys the same evidence and acceptance gates as code changes.

## See also

- [Role card](role-card.md)
- [ANS Governed Construction SKILL.md](../SKILL.md)
