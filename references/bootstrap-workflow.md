# Bootstrap Workflow

When the AI first encounters a project without boundary documents, first determine whether the project is **new** (no source code yet) or **existing** (has source code but no role mapping). Then follow the appropriate path below. Both paths are tasks under the **ANS Governance** built-in role, bound by all seven Governing Invariants.

- **New project (Path A):** No application source exists in the repository after checking root files, package/build manifests, and actual source locations. Absence of `src/` alone is not evidence of a new project. Propose the layout and role cards with planned file paths.
- **Existing project (Path B):** Has existing source code — scan the code, create role cards with actual file paths in Section 1. Do not run scaffold.

## Path A: New project (greenfield)

For projects with no source code yet:

1. Analyze the intended architecture. Identify capabilities and their layer footprint (#2).
2. **Plan the source tree:** Document a language-appropriate layout and planned ownership. Do not run a source scaffold or create application/configuration files under ANS Governance. After acceptance, an activated owner may run the appropriate scaffold script (`scaffold.sh` or `scaffold.ps1`) if the proposed layout matches it and the empty directories are within the accepted scope.
3. For each capability, create a role directory with these exact files and subdirectories (no curly braces, no placeholders):

    ```
    角色卡/<role>/
    ├── role-card.md
    ├── boundary.md
    └── docs/
        ├── design/
        ├── feature/
        ├── change/
        └── fix/
    ```

    **Section 1 requirements:** Application-source entries must list specific files. Supporting and governance directories may use conditional entries as defined in module-boundary.md. For Service and Provider capabilities, account for required contract, public-entry, and implementation files across the ownership map; a shared public entry has one owner and is read-only for other roles, rather than being duplicated in every whitelist.

    The `docs/` subdirectory is a scaffold — the role fills it during implementation.

4. **Identify shared abstractions:** Find every Model and cross-module contract (event bus, shared types, utility classes, public entry points). Assign each to exactly one role as **primary owner**. That role's Section 1 includes the shared file; other roles reference it as read-only. Record the planned contracts and owner dependencies in governance documents only. After acceptance, the activated owning role creates and verifies shared Model or contract source files before dependent implementation relies on them.
5. **Create an assembly role:** For an executable application, assign one role the language-appropriate entry file, required build/test configuration, and layer-local wiring files. For a library, own its actual package entry rather than inventing an executable main. Resolve exact paths in the accepted whitelist.
6. Create one role card per capability and the applicable assembly role. Create the default project role card and boundary using [project-role.md](project-role.md), including its design-document ownership and scheduling duties from [scheduler.md](scheduler.md). List its operational record paths and dispatch limits; do not treat this template as a pre-existing role.
7. Present all artifacts, including the scheduler definition when created, as candidates for human acceptance (#3). Do not proceed to code changes until accepted.
8. **After acceptance, activate the project scheduler when coordinated execution is required.** Follow the [Role Switching](../SKILL.md#role-switching) rules in SKILL.md. The accepted project scheduler follows the dependency-aware scheduling rules below and dispatches the owning roles. A standalone single-role task may omit scheduling records but must pass the customer-consent/configuration gate before activating its implementation role. Each activated role owns its code and evidence; no role gains another role's write scope. Assembly may prepare the build/test environment early, while final integration waits for participating dependencies to pass verification.

## Path B: Existing project (brownfield)

For projects with existing source code that needs role mapping:

1. **Scan the full source tree.** List every file. Classify each by responsibility and architecture layer (I/P/S/Pv/M). Identify which existing capabilities exist based on actual code, not a desired design (#2).
2. For each capability, draft a module boundary document. **Section 1 lists the existing files this role owns** — not files to create. Describe the current architecture in the companion `functional-description.md`, not extra sections in the capability boundary document.
3. **Identify shared abstractions:** Find cross-module contracts, shared models, and public entry points used by multiple capabilities. Assign each to exactly one role as **primary owner**. Other roles that already use it become read-only dependents.
4. Create one role card per capability, referencing its boundary document. Reuse the accepted default project role, or create its card and boundary from project-role.md before requesting acceptance.
5. **Full coverage scan:** Verify every source file is listed in exactly one role's Section 1. Treat duplicate ownership as a conflict to resolve before parallel work. Files not covered by any role are **unowned** — report them to the client for decision: add to an existing role, create a new role, or mark as orphaned and frozen.
6. Present all artifacts as candidates for human acceptance (#3). Do not proceed to code changes until accepted.
7. **After acceptance, activate the project scheduler for coordinated execution**, or a specifically authorized owning role for a standalone single-role task under the [Role Switching](../SKILL.md#role-switching) rules. Routine work happens under the owning role's Section 1. Cross-role changes follow the same dispatch rules.

## Dashboard Handoff

After the default project role and its scope are accepted, that role starts or reuses the shared Skill Dashboard against the real project root under [dashboard.md](dashboard.md). Include coordination records and requested design/role-graph outputs in its accepted scope; use the Skill's reusable assets/scripts rather than building a project-specific copy. Early roles without implementation can appear in overview with no fabricated execution or feature traces.

## Dependency-Aware Scheduling

The accepted project scheduler owns these decisions and the separate stage-task execution graph. Governance defines role authority; capability and assembly workers implement assigned stages and do not create child agents. Read [the scheduler protocol](scheduler.md) for graph fields, state transitions, collision handling, and sequential fallback.

1. Identify cross-role contracts and their unique owners. The project role drafts or reuses the canonical integration design and checks it against actual role/API reports. Record accepted contract versions and release conditions in the task plan. Design revisions do not grant permission to change code or ownership.
2. Implement and verify shared contracts through their owning roles first. Consumers may prepare independent work against agreed contracts or doubles, but must not treat unavailable implementations as verified dependencies.
3. Run roles concurrently only when write scopes are disjoint, required contracts are agreed, and the work does not depend on an unfinished change. Use separate agents only when available and authorized; sequential role switching is a valid fallback. Limit concurrency to available capacity.
4. Assembly creates the minimal build/test configuration early enough for each role's tests, using actual approved dependency needs; extend it as dependencies become known. Final wiring and integration tests wait for the participating implementations to pass their gates, not all roles in the project.
5. When a shared contract changes, the owner coordinates the update and marks affected evidence stale. Resume dependent work after the new contract is settled and rerun the required checks. Do not hide failed dependency tests behind parallel progress.

## Common rules

Both paths share these rules:

- Role names, file names, and document language follow explicit user requirements, then repository conventions, then language/toolchain conventions — see [role-card.md](role-card.md) and [module-boundary.md](module-boundary.md) for format details.
- The ANS Governance role creates governance artifacts only. It never writes application code.
- Bootstrap is complete only after human acceptance.
- **Document placement:** Root `docs/` is for cross-cutting architecture design and multi-role records. Role-specific documents (changelog, functional-description, api-spec) go under `角色卡/<role>/`, not in root `docs/`.

## See also

- [Role card](role-card.md)
- [Module boundary document](module-boundary.md)
- [ANS Governed Construction SKILL.md](../SKILL.md)
