# Bootstrap Workflow

When the AI first encounters a project without boundary documents, first determine whether the project is **new** (no source code yet) or **existing** (has source code but no role mapping). Then follow the appropriate path below. Team formation on both paths is performed under the **ANS Team Formation** built-in role, bound by all Governing Invariants, including one fixed role per context.

- **New project (Path A):** No application source exists in the repository after checking root files, package/build manifests, and actual source locations. Absence of `src/` alone is not evidence of a new project. Propose the layout and role cards with planned file paths.
- **Existing project (Path B):** Has existing source code — scan the code, create role cards with actual file paths in Section 1. Do not run scaffold.

## Path A: New project (greenfield)

For projects with no source code yet:

1. Analyze the intended architecture. Identify capabilities and their layer footprint (#2).
2. **Plan the source tree:** Document a language-appropriate layout and planned ownership. Do not run a source scaffold or create application/configuration files under ANS Team Formation. After acceptance, an activated owner may run the appropriate scaffold script (`scaffold.sh` or `scaffold.ps1`) if the proposed layout matches it and the empty directories are within the accepted scope.
3. For each capability, resolve an actual role layout like the following. Team Formation creates the governance files; accepted owners create their permitted work-document content after handoff. Grant the needed paths explicitly, but do not require absent work content or four empty history directories before permission preflight:

    ```
    角色卡/<role>/
    ├── role-card.md
    ├── boundary.md
    ├── boundary.yaml
    ├── memo.md
    ├── functional-description.md
    ├── feature-map.md
    ├── changelog.md             # governance owner only
    └── docs/
        ├── design/
        ├── feature/
        ├── change/
        └── fix/
    ```

    **Section 1 requirements:** List layer business source by exact file. Grant each capability's private `src/common/<role-id>/` and dedicated tests as explicit, non-overlapping directory scopes when needed. Project management alone owns `src/common/shared/`, its tests and the shared-component document. Supporting/governance directories follow module-boundary.md. For Service and Provider capabilities, account for required contract, public-entry, and implementation files across the ownership map; a shared public entry has one owner and is read-only for other roles, rather than being duplicated in every whitelist.

    Reuse the role's existing `docs/`. Explicitly grant the role's root `feature-map.md`, `memo.md`, `functional-description.md`, applicable `api-spec.md`, and only the bounded docs paths its duties require; do not require four empty history directories. After acceptance, the owner writes its feature navigation and current functional flows under [feature-point.md](feature-point.md). For each newly created or adjusted boundary, Team Formation delivers its synchronized same-name YAML copy with the Markdown source. Do not create a second doc/ or features/ directory, architecture JSON or a project-understanding database.

4. **Identify shared abstractions:** Assign shared foundation components under `common/shared/` to project management and record them in the shared-component document. Models, layer contracts and business capabilities keep their appropriate layer and owner; do not move them into common merely because multiple roles use them. Find every Model and cross-module contract (event bus, shared types, utility classes, public entry points). Assign each to exactly one role as **primary owner**. That role's Section 1 includes the shared file; other roles reference it as read-only. Record the planned contracts and owner dependencies in governance documents only. After acceptance, the activated owning role creates and verifies shared Model or contract source files before dependent implementation relies on them.
5. **Create a fixed test role** using [test-role.md](test-role.md), with its own accepted test and report scope for cross-role integration, complete flows and regression. Development owners still own their unit tests.
   **Create an assembly role:** For an executable application, assign one role the language-appropriate entry file, required build/test configuration, and layer-local wiring files. For a library, own its actual package entry rather than inventing an executable main. Resolve exact paths in the accepted whitelist.
6. Create one peer role card per capability and applicable assembly role. Each card includes classification-only `group` / `组别` and its independent boundary. No group-lead object or group-duty field is created. Count accepted role definitions, not running contexts; multiple contexts for one `roleId` remain one role. Changing groups does not change write scope. Team Formation creates a new role only when its exact definition and boundary are authorized.

   Create separate concrete cards and boundaries for the default [scheduler](scheduler.md), [planning](planning-role.md), [project management](project-role.md), and [independent acceptance](acceptance-role.md). The scheduler owns intake, investigation and scheduling records; planning owns product/requirements proposals; project management owns technical architecture, implementation design/review, abstractions, project rules and shared code/tests/catalog; acceptance owns criteria and conclusions. Resolve actual paths, tool permissions and dispatch limits separately. Templates are not accepted roles or global write grants.
   Record planned feature ownership in governance proposals. The role card points to `feature-map.md`; after acceptance, its owner writes the map and one stable `docs/feature/<feature-id>.md` draft per owned feature. Label planned features as planned. A role without directly owned system features says so; do not turn coordination into a fake feature. Use [feature-point.md](feature-point.md).
7. Present all artifacts, including the separate scheduler, planning, management and acceptance definitions, as candidates for human acceptance (#3). Do not proceed to code changes until accepted.
8. **After role-definition acceptance, prepare a handoff to a fresh scheduler context.** Team Formation remains bound to Team Formation. The scheduler owns the global plan, per-role authorization/reservation and records; independent acceptance judges completion. Establish criteria before implementation. The scheduler directly authorizes/reserves and dispatches each role in a separate context, receiving its evidence directly. Accepted role cards do not approve a later code change: the relevant dated proposal still needs customer confirmation and an instruction to implement it. A standalone single-role task may omit scheduling records but runs in a separate context bound to its authorized owner with the same document and role-binding gates. Each role owns its code and evidence; no role gains another role's write scope.

## Path B: Existing project (brownfield)

For projects with existing source code that needs role mapping:

1. **Scan the full source tree.** List every file. Classify each by responsibility and architecture layer (I/P/S/Pv/M). Identify which existing capabilities exist based on actual code, not a desired design (#2).
2. For each capability, Team Formation creates a module boundary pair. `boundary.md` Section 1 lists the existing files this role owns — not files to create — and the adjacent same-name `boundary.yaml` mirrors it. Create or update both in the same governance delivery; the Markdown remains the only authorization source. Describe current architecture in `functional-description.md`, not extra sections in the capability boundary.
3. **Identify shared abstractions:** Find cross-module contracts, shared models, and public entry points used by multiple capabilities. Assign each to exactly one role as **primary owner**. Other roles that already use it become read-only dependents.
4. Create one peer role card per capability, referencing its boundary and recording only classification `group` / `组别`. Roles are peers and report directly to the scheduler. Do not migrate old group duties into dispatch or permission authority.

   Explicitly propose or migrate separate scheduler, planning, project-management, independent acceptance and test roles using [team formation](team-formation.md), [scheduler](scheduler.md), [planning](planning-role.md), [project-role.md](project-role.md), [acceptance-role.md](acceptance-role.md) and [test-role.md](test-role.md). Their cards include the classification field. Inventory active contexts, tasks, credentials and configuration; obtain the applicable authorization, reconcile old workers, then hand off to fresh fixed-role contexts. Do not silently extend an old PM or recognize old self-verification as independent acceptance. Team Formation owns cards and boundaries. Changing an existing role's group updates its card and leaves its boundary unchanged. When a new role is needed, Team Formation checks whether existing consent or approved configuration covers its exact definition and boundary. If covered, create the new peer card and independent boundary under that authorization; otherwise request the needed authorization first. Existing-project permissions are not expanded automatically. Propose common/shared ownership, its tests/catalog and independent test-role boundaries before requesting acceptance; keep existing utilities and test paths until migration is approved.
   Include the role's feature-map, memo, functional-description, applicable api-spec and actual bounded docs paths in proposed boundaries; project management also needs its own docs/architecture.md. Missing paths in existing accepted boundaries are not implied permission. Do not add architecture JSON or mandatory project-understanding SQLite scopes.
   Map actual features to one primary owner; its card links feature-map.md. After acceptance, the owner maintains that map and one stable `docs/feature/<feature-id>.md` per feature, including its Mermaid flow and links to actual history. Migrate old features/ pages only within approved scope; preserve dated feature history and correct links without fabricating past dates. Check entry points, branches and results in source and tests; mark unverified details instead of guessing from names. See [feature-point.md](feature-point.md).
5. **Full coverage scan:** Verify every source file is listed in or covered by exactly one role's Section 1. Treat duplicate ownership as a conflict to resolve before parallel work. Files not covered by any role are **unowned** — report them to the client for decision: add to an existing role, create a new role, or mark as orphaned and frozen.
6. Present all artifacts as candidates for human acceptance (#3). Do not proceed to code changes until accepted.
7. **After role-definition acceptance, prepare a handoff to a fresh scheduler context for global coordination**, or a separate specifically authorized owner context for a standalone task under [Role Binding and Handoff](../SKILL.md#role-binding-and-handoff). The Team Formation context retains its role. Before a code stage, the customer must also confirm that stage's proposal document and instruct implementation from it. Routine work happens under the owning role's Section 1. Cross-role changes follow the same dispatch rules.

After project management role and boundary acceptance, that role may investigate and establish the project engineering rules document at its accepted `docs/project-rules.md` path. This is not a prerequisite for role creation, project startup, or otherwise authorized work. Do not invent project-specific rules during bootstrap; mark missing or unconfirmed constraints and continue under applicable skill rules and confirmed project agreements. Each activated role creates and maintains its own `memo.md` within accepted documentation scope, or Team Formation includes that file during bootstrap.

## Check actual work-document permissions before handoff

For both paths and later role adjustments, Team Formation prepares the complete `roleDefinitions` content and role-permission definitions, not the configuration file. An accepted scheduler writes that content into the candidate execution configuration within its own accepted scope: actual `card` and `boundary`, exact `requiredWorkDocuments`, `apiSpec` (`required` or `not-applicable`) and a nonempty, verifiable `apiSpecReason`. The actual card/boundary common parent identifies the role root; role IDs and directory names may differ. Owners check applicability against accepted duties. Include all actual project roles, including non-executors, scheduler and acceptance; do not recursively include isolated example projects. The tool checks the supplied registration; Team Formation, scheduler and acceptance check its completeness against actual project roles.

The required list defaults to own feature-map, memo and functional-description, plus applicable API and actual work documents. Roles without system features or code say so; real exported/shared capabilities or assembly interfaces require API reports. Pure collaboration without such interfaces may declare reasoned non-applicability. The list checks expected permissions, grants none, and does not pre-enumerate every future dated document. Only Section 1 grants exact files or bounded directories. Governance card/boundary/YAML/root changelog remain exclusively Team Formation-owned; owner implementation history belongs in docs. Service/Provider abstract/public/impl rules continue; no unused layers or new generic architecture scanner are required.

For a new project, first accept the scheduler definition and activate a separate fixed scheduler context solely to prepare the candidate configuration within its accepted scope. Team Formation supplies registration content and permissions; it does not write application/configuration files. Run `python3 /path/to/skill/scripts/task_ops.py --root /path/to/project preflight-role --request -` against that candidate, then hand off/dispatch the remaining actual work only after permission coverage is complete. In an existing project, the existing scheduler writes the candidate configuration before the same preflight. This limited configuration-preparation handoff avoids requiring a configuration before anyone is authorized to prepare it; it does not authorize ordinary task execution before preflight or bypass customer configuration approval. See [the task contract and implementation status](task-operations.md). This branch requires no task or credential and creates no runtime, lock, log or task record. It reads actual Section 1 for every registered role, checks expected file coverage and protected/overlapping permissions, and reports role/path/reason. A missing work file can be reported as absent while its creation permission is complete; Team Formation hands off governance, and the accepted owner writes work content.

Permission failure returns to Team Formation for the necessary authorized correction and recheck; applicability uncertainty returns to the definition owner. Successful preflight is not customer approval, dispatch, document completion or acceptance. When roleDefinitions is enabled, init reuses the same checks before task creation. Later changed boundaries invalidate prior evidence through existing hash rules. Old configurations retain their existing scope; using the new document capability requires complete registration, a newly approved configuration and a new task, never retroactive widening.

## Architecture and Feature Handoff

After acceptance, project management maintains its own `docs/architecture.md`, showing the overall structure and role collaboration and linking each role's feature-map. The owner maintains its current feature flowcharts and design/change/fix links in the existing docs tree. At delivery, give links to those Markdown documents. Do not add a JSON-maintenance or HTML-rendering stage. Legacy viewers and Dashboard are opt-in only.

## Dependency-Aware Scheduling

The accepted project scheduler owns the global stage-task graph, authorization, reservations and recording/release based on current independent acceptance conclusions. Independent acceptance defines criteria before implementation and decides pass, rework or insufficient evidence. The scheduler dispatches directly to each authorized and reserved role. Team Formation defines role authority; capability and assembly workers do not assign peers. Read [the scheduler protocol](scheduler.md) for graph fields, state transitions and collision handling.

1. Identify cross-role contracts and their unique owners. Project management drafts or reuses the canonical integration design and checks it against actual role/API reports. Record accepted contract versions and release conditions in the task plan. Design revisions do not grant permission to change code or ownership.
2. Implement and verify shared contracts through their owning roles first. Consumers may prepare independent work against agreed contracts or doubles, but must not treat unavailable implementations as verified dependencies.
3. Run roles concurrently only when write scopes are disjoint, required contracts are agreed, and the work does not depend on an unfinished change. Each role runs in its own independently bound context. When parallel agents are unavailable, use separate contexts sequentially; never switch roles in the same context. If no separate context is available, prepare the handoff and report the pending stage. Limit concurrency to available capacity.
4. Assembly creates the minimal build/test configuration early enough for each role's tests, using actual approved dependency needs; extend it as dependencies become known. Assembly wiring/startup checks and the fixed test role's cross-role, full-flow and regression checks wait for their actual participating implementations, not all roles in the project.
5. When a shared contract changes, its owner reports the impact to the scheduler; project management assesses design impact, the scheduler arranges owner changes and retests, and independent acceptance reassesses affected evidence. Resume dependent work after the new contract is settled and rerun the required checks. Do not hide failed dependency tests behind parallel progress.

## Common rules

Both paths share these rules:

- Role names, file names, and document language follow explicit user requirements, then repository conventions, then language/toolchain conventions — see [role-card.md](role-card.md) and [module-boundary.md](module-boundary.md) for format details.
- The ANS Team Formation role creates governance artifacts only. It never writes application code.
- Bootstrap is complete only after human acceptance.
- When creating or updating project cards, place the [long-term maintainer stance](role-card.md#working-stance-for-every-role) near the beginning. Adapt its focus to each role's responsibility, including management, assembly and testing. This establishes a shared working perspective without adding technical checklists or expanding existing permissions.
- **Document placement:** Reuse each role's existing docs/ for its feature and history documents. Project management keeps overall architecture and cross-role design in its own docs/; participants link them. Existing root history is preserved, not automatically moved. Role-root feature-map, changelog, functional-description and api-spec retain their specific purposes.

## See also

- [Role card](role-card.md)
- [Module boundary document](module-boundary.md)
- [ANS Governed Construction SKILL.md](../SKILL.md)
