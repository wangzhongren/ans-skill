# Role Project Context

Each accepted project role, including the default project role and assembly role, maintains its own `project-context/` directory under its role directory. This is a navigable view of the project from that role's responsibility, not a second copy of the whole project's specification. The owning role updates it only within its accepted `boundary.md` Section 1 and task scope.

```text
角色卡/<role>/project-context/
  README.md          # Short overview and links to relevant topics
  flows/             # Participating workflows and upstream/downstream roles
  definitions/       # Terms and responsibility boundaries used by this role
  events/            # Events received or emitted, and when
  interfaces/        # Public capabilities provided or called
  data/              # Data read, created or changed; canonical owner
```

Use the project's existing role-directory name (`角色卡/` or `role-cards/`). Create `README.md` when the role has enough verified project evidence to describe its participation. Create each category and topic file only when it has real content; do not fill empty folders or copy another role's context. Use short topic-based filenames such as `flows/order-export.md`. These are living navigation files, so they do not use the dated filenames or event frontmatter required for `docs/design|feature|change|fix/` records.

The index names the role's current responsibilities and links to the relevant topic files. Organize its overview around the actual workflow: entry, this role's action, next role or output. A topic file gives the role-relevant meaning, affected code locations, upstream/downstream role, and a link to the canonical source or accepted contract. Mark proposed, implemented, or uncertain behavior explicitly. Put each topic in the category that answers the reader's first question; link to related topics rather than copying their contents.

`definitions/` explains how this role uses a term; `events/` records triggers, producers and consumers; `interfaces/` indexes provided/consumed public entries and contract IDs; `data/` records read/write effects and the primary owner. Canonical interfaces, event schemas, Model definitions, permissions, and implementation evidence remain in their accepted design, `api-spec.md`, Model/source, and `boundary.md`. Context links to them and never grants a new capability or write scope. `functional-description.md` still explains the role's own implementation in detail; project context shows where that implementation fits in project workflows.

At task start, read `README.md` and only the topic files relevant to the task, then verify claims against current source and contracts. After a verified change, the owning role updates affected context topics and index links in the same authorized task. A cross-role change is reported to the project role, which identifies impacted owners and versions; each affected owner refreshes its own context after the canonical change is accepted. Missing or stale context is a navigation gap, not proof that the code or contract is absent. Do not regenerate every role's context for a local change.

The Dashboard lists and reads only `README.md` and direct Markdown files in the five named categories under each direct role folder. It does not render arbitrary project files through the context viewer. See [dashboard.md](dashboard.md).
