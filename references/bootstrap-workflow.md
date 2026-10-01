# Bootstrap Workflow

When the AI first encounters a project without boundary documents, first determine whether the project is **new** (no source code yet) or **existing** (has source code but no role mapping). Then follow the appropriate path below. Both paths are tasks under the **ANS Governance** built-in role, bound by all Governing Invariants, including one fixed role per context.

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

    **Section 1 requirements:** List layer business source by exact file. Grant each capability's private `src/common/<role-id>/` and dedicated tests as explicit, non-overlapping directory scopes when needed. Project management alone owns `src/common/shared/`, its tests and the shared-component document. Supporting/governance directories follow module-boundary.md. For Service and Provider capabilities, account for required contract, public-entry, and implementation files across the ownership map; a shared public entry has one owner and is read-only for other roles, rather than being duplicated in every whitelist.

    Reuse the role's existing `docs/`. Grant `feature-map.md` and bounded docs/feature/, docs/design/, docs/change/ and docs/fix/ paths. After acceptance, the owner writes its feature navigation and current functional flows under [feature-point.md](feature-point.md). Do not create a second doc/ or features/ directory, architecture JSON or a project-understanding database.

4. **Identify shared abstractions:** Assign shared foundation components under `common/shared/` to project management and record them in the shared-component document. Models, layer contracts and business capabilities keep their appropriate layer and owner; do not move them into common merely because multiple roles use them. Find every Model and cross-module contract (event bus, shared types, utility classes, public entry points). Assign each to exactly one role as **primary owner**. That role's Section 1 includes the shared file; other roles reference it as read-only. Record the planned contracts and owner dependencies in governance documents only. After acceptance, the activated owning role creates and verifies shared Model or contract source files before dependent implementation relies on them.
5. **Create a fixed test role** using [test-role.md](test-role.md), with its own accepted test and report scope for cross-role integration, complete flows and regression. Development owners still own their unit tests.
   **Create an assembly role:** For an executable application, assign one role the language-appropriate entry file, required build/test configuration, and layer-local wiring files. For a library, own its actual package entry rather than inventing an executable main. Resolve exact paths in the accepted whitelist.
6. Create one role card per capability and the applicable assembly role. Create the default project role card and boundary using [project-role.md](project-role.md), including shared-code and test ownership, the shared-component document, design-document ownership and scheduling duties from [scheduler.md](scheduler.md). List its operational record paths and dispatch limits; do not treat this template as a pre-existing role.
   Record planned feature ownership in governance proposals. The role card points to `feature-map.md`; after acceptance, its owner writes the map and one stable `docs/feature/<feature-id>.md` draft per owned feature. Label planned features as planned. A role without directly owned system features says so; do not turn coordination into a fake feature. Use [feature-point.md](feature-point.md).
7. Present all artifacts, including the scheduler definition when created, as candidates for human acceptance (#3). Do not proceed to code changes until accepted.
8. **After acceptance, prepare a handoff to a separate project-scheduler context when coordinated execution is required.** Follow [Role Binding and Handoff](../SKILL.md#role-binding-and-handoff). The bootstrap context remains Governance and does not dispatch application workers. Accepted role cards define scope, but they do not by themselves approve a later code change: the relevant dated proposal must also be confirmed by the customer with an instruction to implement it. The scheduler dispatches owning roles in separate contexts after that gate. A standalone single-role task may omit scheduling records but runs in a separate context bound to its authorized owner with the same document and role-binding gates. Each role owns its code and evidence; no role gains another role's write scope.

## Path B: Existing project (brownfield)

For projects with existing source code that needs role mapping:

1. **Scan the full source tree.** List every file. Classify each by responsibility and architecture layer (I/P/S/Pv/M). Identify which existing capabilities exist based on actual code, not a desired design (#2).
2. For each capability, draft a module boundary document. **Section 1 lists the existing files this role owns** — not files to create. Describe the current architecture in the companion `functional-description.md`, not extra sections in the capability boundary document.
3. **Identify shared abstractions:** Find cross-module contracts, shared models, and public entry points used by multiple capabilities. Assign each to exactly one role as **primary owner**. Other roles that already use it become read-only dependents.
4. Create one role card per capability, referencing its boundary document. Reuse or propose the default project management role and a fixed test role from project-role.md and test-role.md. For existing projects, explicitly propose common/shared ownership, its tests/catalog and independent test-role boundaries before requesting acceptance; existing accepted permissions are not expanded automatically. Keep existing utilities and test paths until migration is approved.
   Include the role's feature-map and existing docs paths in proposed boundaries; project management also needs its own docs/architecture.md. Missing paths in existing accepted boundaries are not implied permission. Do not add architecture JSON or mandatory project-understanding SQLite scopes.
   Map actual features to one primary owner; its card links feature-map.md. After acceptance, the owner maintains that map and one stable `docs/feature/<feature-id>.md` per feature, including its Mermaid flow and links to actual history. Migrate old features/ pages only within approved scope; preserve dated feature history and correct links without fabricating past dates. Check entry points, branches and results in source and tests; mark unverified details instead of guessing from names. See [feature-point.md](feature-point.md).
5. **Full coverage scan:** Verify every source file is listed in or covered by exactly one role's Section 1. Treat duplicate ownership as a conflict to resolve before parallel work. Files not covered by any role are **unowned** — report them to the client for decision: add to an existing role, create a new role, or mark as orphaned and frozen.
6. Present all artifacts as candidates for human acceptance (#3). Do not proceed to code changes until accepted.
7. **After acceptance, prepare a handoff to a separate project-scheduler context for coordinated execution**, or a separate specifically authorized owner context for a standalone task under [Role Binding and Handoff](../SKILL.md#role-binding-and-handoff). The Governance context retains its role. Before a code stage, the customer must also confirm that stage's proposal document and instruct implementation from it. Routine work happens under the owning role's Section 1. Cross-role changes follow the same dispatch rules.

## Architecture and Feature Handoff

After acceptance, project management maintains its own `docs/architecture.md`, showing the overall structure and role collaboration and linking each role's feature-map. The owner maintains its current feature flowcharts and design/change/fix links in the existing docs tree. At delivery, give links to those Markdown documents. Do not add a JSON-maintenance or HTML-rendering stage. Legacy viewers and Dashboard are opt-in only.

## Dependency-Aware Scheduling

The accepted project scheduler owns these decisions and the separate stage-task execution graph. Governance defines role authority; capability and assembly workers implement assigned stages and do not create child agents. Read [the scheduler protocol](scheduler.md) for graph fields, state transitions, collision handling, and sequential fallback.

1. Identify cross-role contracts and their unique owners. The project role drafts or reuses the canonical integration design and checks it against actual role/API reports. Record accepted contract versions and release conditions in the task plan. Design revisions do not grant permission to change code or ownership.
2. Implement and verify shared contracts through their owning roles first. Consumers may prepare independent work against agreed contracts or doubles, but must not treat unavailable implementations as verified dependencies.
3. Run roles concurrently only when write scopes are disjoint, required contracts are agreed, and the work does not depend on an unfinished change. Each role runs in its own independently bound context. When parallel agents are unavailable, use separate contexts sequentially; never switch roles in the same context. If no separate context is available, prepare the handoff and report the pending stage. Limit concurrency to available capacity.
4. Assembly creates the minimal build/test configuration early enough for each role's tests, using actual approved dependency needs; extend it as dependencies become known. Assembly wiring/startup checks and the fixed test role's cross-role, full-flow and regression checks wait for their actual participating implementations, not all roles in the project.
5. When a shared contract changes, its owner reports the impact to project management, which coordinates owner changes and retests and marks affected evidence stale. Resume dependent work after the new contract is settled and rerun the required checks. Do not hide failed dependency tests behind parallel progress.

## Common rules

Both paths share these rules:

- Role names, file names, and document language follow explicit user requirements, then repository conventions, then language/toolchain conventions — see [role-card.md](role-card.md) and [module-boundary.md](module-boundary.md) for format details.
- The ANS Governance role creates governance artifacts only. It never writes application code.
- Bootstrap is complete only after human acceptance.
- When creating or updating project cards, place the [long-term maintainer stance](role-card.md#working-stance-for-every-role) near the beginning. Adapt its focus to each role's responsibility, including management, assembly and testing. This establishes a shared working perspective without adding technical checklists or expanding existing permissions.
- **Document placement:** Reuse each role's existing docs/ for its feature and history documents. Project management keeps overall architecture and cross-role design in its own docs/; participants link them. Existing root history is preserved, not automatically moved. Role-root feature-map, changelog, functional-description and api-spec retain their specific purposes.

## See also

- [Role card](role-card.md)
- [Module boundary document](module-boundary.md)
- [ANS Governed Construction SKILL.md](../SKILL.md)
