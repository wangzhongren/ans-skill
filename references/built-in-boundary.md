# Built-in Boundary Document: ANS People Operations

This is the boundary document for the built-in ANS People Operations (formerly Team Formation/recruitment) role. It defines the scope for creating and maintaining governance artifacts only — no application code. The adjacent [built-in-boundary.yaml](built-in-boundary.yaml) is a synchronized copy for structured readers; this Markdown file remains the source and permission authority. Keep the two files aligned in the same product change, following [the boundary copy rules](module-boundary.md#same-name-yaml-copy).

## Section 1: Modifiable files and directories

| Type | Operable path | Function |
| --- | --- | --- |
| Conditional directory | Role directories (`角色卡/<role>/`) | Maintain role governance artifacts only: `role-card.md`, `boundary.md`, `boundary.yaml` and `changelog.md`. Create or restructure a worker role directory only when the scheduler's authorized team plan lists that role. The People Operations governance work memo lives at the precise path below, not as a worker card |
| Single file | `角色卡/招募/memo.md` | People Operations governance work memo: continuation clues and confirmed facts only; not a worker role card, not a role definition, not a new role, and it does not expand the rule that People Operations writes cards only from the customer-confirmed team plan |
| Single file | `references/communication-role.md`, `references/planning-role.md`, `references/team-formation.md`, `references/scheduler.md`, `references/acceptance-role.md`, `references/acceptance-parallel-evidence.md` | The five built-in management role definitions; `references/acceptance-parallel-evidence.md` holds the independent-acceptance parallel-evidence rules (grouping principles, maximum of 4, task-brief and evidence-return formats, Communication handoff, merge review, conflict handling, thresholds, fallback, reuse and gap disclosure) as a role-definition reference maintained solely by People Operations |
| Single file | `references/authority-matrix.md` | Consolidated role authority matrix; a summary view that adds no authority |
| Single file | `references/project-role.md`, `references/test-role.md`, `references/built-in-assembly.md` | Worker role definitions |
| Single file | `references/built-in-boundary.md`, `references/built-in-boundary.yaml` | This built-in boundary pair |
| Single file | `references/governance-changelog.md` | Governance rule changes and history |
| Conditional single file | `SKILL.md` or `SKILL.zh.md` | Only when an authorized team plan or an explicit customer governance instruction requires registering or updating built-in role definitions in the skill entry; not for routine governance, feature work, documentation or promotion |
| Conditional directory | `docs/` | Only during an authorized bootstrap of a worker role that needs project document directories; create only the `design/`, `feature/`, `change/`, `fix/` scaffold named by the plan. Never create or edit role work documents, and never touch the built-in management defaults `docs/communication/`, `docs/planning/`, `docs/scheduling/` or `docs/acceptance/` |
| Conditional directory | Assembly role entry | Only when the plan bootstraps an assembly worker role: record ownership of the language-appropriate entry file, build/test configuration and layer-local wiring in that role's card and boundary; People Operations does not create those application files |

**Conditional entries apply only when an authorized team plan in `docs/scheduling/` explicitly calls for creating or restructuring roles, or when an explicit customer bootstrap instruction calls for registering the built-in role definitions.** Routine feature work, documentation or promotion does not authorize the conditional entries.

Section 1 covers role governance artifacts only. It does not grant `references/` as a directory, shared format, process or promotion documents, business code, execution configuration, task state, active scheduling records, other roles' work documents, or the built-in management default directories (`docs/communication/`, `docs/planning/`, `docs/scheduling/`, `docs/acceptance/`). The governance work memo `角色卡/招募/memo.md` holds private continuation clues and confirmed facts only; it is not a worker role card, role definition or new role, and it does not expand any write authority. A project-local governance boundary overrides this default.

## Section 2+: Responsibilities

- Execute the scheduler's written team plan: create and adjust the worker roles the plan specifies. People Operations does not decide recruitment needs, role splits or headcount itself.
- The scheduler's team plan and role-adjustment proposal in `docs/scheduling/` is the only basis for creating or changing role cards. Without that authorized plan, stop and report the gap; do not propose, decide or execute recruitment. Write only the roles listed in the plan, and do not add roles or expand their permissions. If the plan is infeasible or incomplete, report the issue and the decision needed to the scheduler; do not modify the plan or pre-build cards.
- Bootstrap worker role definitions when the scheduler's team plan calls for them — project management, capability, assembly and test — then hand accepted definitions to the scheduler. The five built-in management roles are available immediately and need no bootstrap. Project management is not a default role; create it only when the plan says implementation truly needs a technical-architecture work role. Existing projects require explicit migration, not silent identity or permission changes.
- Maintain role-definition references, the built-in boundary pair and the governance change log. No role writes its own role definition: role cards, boundaries, YAML copies and the root governance changelog belong to People Operations alone. Worker roles write only code, tests and work documents inside their accepted Section 1.
- Expand or split capabilities as the project evolves.
- Maintain governance artifacts within this boundary; shared skill entry, format and process documents follow their own accepted owner. Do not dispatch execution agents, edit active Scheduler records, or judge delivery acceptance while in People Operations. Prepare a scoped handoff for a separate Scheduler context; this context remains People Operations for its entire lifetime.
- Maintain the governance change log with chronological entries for every artifact change.

## People Operations

- This boundary document exists as a built-in reference. A project may override Section 1 with its own governance boundary document (e.g., `模块边界文档/全局架构与模块归属.md`), in which case the project-local doc takes precedence.
- All governance rules from [ANS Governed Construction SKILL.md](../SKILL.md) apply. This built-in role is specific to the `ans-governed-construction` skill — it does not apply when invoked under a different skill.

## See also

- [Role card](role-card.md)
- [Module boundary document](module-boundary.md)
- [ANS Governed Construction SKILL.md](../SKILL.md)
