# Built-in Boundary Document: ANS Governance

This is the boundary document for the built-in governance role. It defines the scope for creating and maintaining governance artifacts only — no application code.

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

- Create and maintain governance artifacts (role cards, module boundary documents).
- Bootstrap new projects with initial role structure, create a project scheduler role when coordination is needed, then hand accepted definitions to that project role for execution.
- Expand or split capabilities as the project evolves.
- Update governance rules in SKILL.md. Do not dispatch execution agents or edit active Scheduler records while in Governance; explicitly hand off or switch to Scheduler.
- Maintain the governance change log with chronological entries for every artifact change.

## Governance

- This boundary document exists as a built-in reference. A project may override Section 1 with its own governance boundary document (e.g., `模块边界文档/全局架构与模块归属.md`), in which case the project-local doc takes precedence.
- All governance rules from [ANS Governed Construction SKILL.md](../SKILL.md) apply. This built-in role is specific to the `ans-governed-construction` skill — it does not apply when invoked under a different skill.

## See also

- [Role card](role-card.md)
- [Module boundary document](module-boundary.md)
- [ANS Governed Construction SKILL.md](../SKILL.md)
