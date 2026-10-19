# Built-in Boundary Document: ANS Team Formation

This is the boundary document for the built-in governance role. It defines the scope for creating and maintaining governance artifacts only — no application code. The adjacent [built-in-boundary.yaml](built-in-boundary.yaml) is a synchronized copy for structured readers; this Markdown file remains the source and permission authority. Keep the two files aligned in the same product change, following [the boundary copy rules](module-boundary.md#same-name-yaml-copy).

## Section 1: Modifiable files and directories

| Type | Operable path | Function |
| --- | --- | --- |
| Single file | `SKILL.md` or `SKILL.zh.md` | Update governance rules, invariants, checkpoints |
| Conditional directory | `references/` | Maintain reference documents for role cards and boundary doc format |
| Conditional directory | `docs/` | Create project docs scaffold during bootstrap: `design/`, `feature/`, `change/`, `fix/` subdirectories |
| Conditional directory | Role directories (`角色卡/<role>/`) | Create, update, or restructure a role directory containing `role-card.md`, `boundary.md`, and `changelog.md` |
| Conditional directory | Assembly role entry | Create the assembly role during bootstrap: records ownership of the language-appropriate entry file, build/test configuration, and layer-local wiring; does not create those application files |

**Conditional entries apply only when the task explicitly calls for creating or restructuring roles.** Routine feature work does not authorize governance artifact changes.

## Section 2+: Responsibilities

- Form and adjust the team, including recruitment needs, unique ownership, classification-only groups; create and maintain role cards and module boundary documents within task authorization. Templates do not grant global project write authority.
- Bootstrap new projects with separate project scheduler, planning, project-management, independent acceptance and applicable worker definitions, then hand accepted definitions to a fresh scheduler context. Existing projects require explicit migration, not silent identity or permission changes.
- Expand or split capabilities as the project evolves.
- Update governance rules in SKILL.md. Do not dispatch execution agents, edit active Scheduler records, or judge delivery acceptance while in Team Formation. Prepare a scoped handoff for a separate Scheduler context; this context remains Team Formation for its entire lifetime.
- Maintain the governance change log with chronological entries for every artifact change.

## Team Formation

- This boundary document exists as a built-in reference. A project may override Section 1 with its own governance boundary document (e.g., `模块边界文档/全局架构与模块归属.md`), in which case the project-local doc takes precedence.
- All governance rules from [ANS Governed Construction SKILL.md](../SKILL.md) apply. This built-in role is specific to the `ans-governed-construction` skill — it does not apply when invoked under a different skill.

## See also

- [Role card](role-card.md)
- [Module boundary document](module-boundary.md)
- [ANS Governed Construction SKILL.md](../SKILL.md)
