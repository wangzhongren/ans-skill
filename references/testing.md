# Layer Tests and Verification Gates

Use with role-card.md's Required reading. These rules retain the global mutation and architectural boundaries.

### Who Owns Tests

Development roles own and run their unit and layer-contract tests. An established project-management role owns the tests for `common/shared/`. The assembly role owns runner setup and startup/wiring smoke checks. The project's [fixed test role](test-role.md) owns cross-role integration, complete user-flow and regression tests. The scheduler arranges repairs and testing; the test role reports actual results instead of editing another role's code. Independent acceptance writes completion criteria from the confirmed planning proposal version and judges pass, rework, or insufficient evidence from current reports. Neither scheduler dispatch nor a self-test is an acceptance verdict. Passing unit tests does not replace required integrated tests, and a dedicated test role does not remove per-layer verification.

### Risk-Based Verification and Change Packages

Acceptance is risk-based, not a full rerun by default. The scheduler gives Independent Acceptance a **change package** for the current candidate: candidate hash/version, changed paths, task nodes, evidence links and the risk tier. Acceptance reviews the change record and the acceptance table, reuses evidence that is still valid for unaffected paths, and adds only missing, invalidated or higher-risk checks. Full regression is reserved for **T3** changes — release, shared-abstraction, governance or permission change — or insufficient evidence.

| Tier | Change | Default verification |
| --- | --- | --- |
| **T0** | Pure documentation, comments, formatting or other non-behavioral text, with no governance or permission change | Link, format and consistency checks plus the affected document checks; no code regression |
| **T1** | Local implementation inside one role with no cross-role contract change | That role's affected unit/layer tests and the narrowest changed-path checks |
| **T2** | Cross-role, interface/contract, data model, pipeline, integration or shared-code change | Affected roles' tests plus integration checks across the changed contract; affected callers retested |
| **T3** | Release, shared-abstraction change (Model, public entry, cross-module contract), governance or permission change, or an uncertain/insufficient evidence basis | Full applicable regression plus release/shared-abstraction checks |

Selection rules:

- Map each changed path to its owning role, layer and affected contract; run the checks that cover those paths.
- Governance or permission changes are T3, never T0, even when the edited files are documentation.
- Reuse evidence only for unchanged paths and the same candidate/version. A changed input, dependency, contract, fixture or configuration invalidates affected evidence.
- Do not rerun unrelated suites merely because a task exists. Do not skip a required check because another role ran something different.
- If the change package is incomplete, the candidate hash is unclear, or evidence is missing or invalidated, classify the gap and request targeted evidence. If targeted evidence cannot establish the result, escalate to the next tier, up to full regression.
- Record the tier, selected checks, reused evidence links and the reason for any full regression in the acceptance report.

### Layer Tests in `test`

Use a root `test/` directory organized by role — `test/<role>/<language-native test file>` — mirroring the role structure under `角色卡/`. It is supporting verification infrastructure, not an operational layer:

```text
test/
  <role>/
    <language-native test file>
```

Use the language and existing runner's real discovery rules: for example `test_order.py`, `order.test.ts`, or colocated Go `order_test.go`. Where the runner requires colocation, record role ownership without moving tests into an undiscoverable folder. These are examples, not required extensions.

Create actual test files as layers are implemented; empty directories do not count as tests. When a repository already uses an established test layout, map role ownership and layer coverage to it rather than migrating unrelated tests. Use its existing runner and conventions; for a new project, configure a suitable runnable test command. Do not invent command results or treat illustrative command names as working commands.

- Every implemented or behaviorally changed layer must have explicit, executable tests for its observable contracts. Reuse sufficient existing coverage or add and update tests for missing behavior; tests must assert results, errors, invariants, or effects, not merely mirror private code or count calls without checking outcomes. Each layer reference specifies its required scenarios.
- Define the relevant test files, exact runnable commands, expected behavior, and pass condition in the Mutation Contract before implementation. Include necessary test and fixture edits in the authorized write set.
- At each layer milestone, run its applicable static checks and tests before considering the layer complete or integrating dependent implementation with it. Independent preparation against agreed contracts and compatible doubles does not count as integration verification. Follow the construction order for affected layers; do not defer all testing to the final integration stage. Independent work may continue while a dependency is blocked, but cannot treat that dependency as verified.
- Record the layer, final candidate or diff identity, command, environment, test result, and any skipped or unavailable checks in a concise progress update or existing test report. A layer passes only when its required checks pass for the current candidate. Missing dependencies, skipped tests, and unresolved failures mean unverified, not passed.
- Isolate immediate lower-layer dependencies with contract-compatible test doubles for unit tests. Provider tests isolate external infrastructure. Add integration tests at real boundaries when adapters, wiring, or shared contracts change; mocks alone cannot establish real adapter compatibility. Use local or isolated environments, subject to existing authorization for external effects.
- Test code may construct fixtures and doubles across layers without granting production code additional call authority. Public API tests for Provider and Service import through their designated public entry point; focused internal tests may inspect internals. Keep test-only helpers out of production imports.
- After connecting affected layers, run a regression or integration test through the changed user-facing path. Any later code, contract, fixture, or relevant configuration change invalidates affected prior evidence and requires rerunning the corresponding checks. Layer test success does not replace the final static and dynamic gates.

## Gate 1: Static Structural Verification

Check implementation against relevant, confirmed entries in an established project-management role's `docs/project-rules.md` when available. Report the rule identifier and concrete evidence. A missing file, draft entry or rule without a check method is a documented gap, not a pass or a blocker to unrelated verification. Do not claim a project-specific thread, resource or performance rule was tested unless the corresponding behavior was actually checked.

Run the checks appropriate to the repository and risk. The static gate must verify, at minimum:

### Mutation authority

- Every changed path is in the allowed write set.
- No protected artifact was changed.
- No unrelated user change was overwritten or absorbed into the candidate.

### Architectural capability

- Check all applicable layer-reference constraints, including required structure, exports, responsibility, and caller boundaries.
- **Responsibility review:** Check each changed behavior against the [ownership decision table](architecture.md). Existing-capability reuse must not silently add unrelated responsibilities; modifications belong to the existing owner, and new independent responsibilities have focused owners. Review semantic cohesion and reasons to change rather than imposing file-count or line-count targets.
- **Dependency review:** Independently check the permitted edges between those owners, including public entry points, Pipeline composition of Services, and reviewed Pipeline infrastructure operations. Reject per-feature wrappers without a contract responsibility and reject unapproved skipped-layer shortcuts or Provider implementation imports. A valid ownership split cannot compensate for an illegal call, nor can a legal call graph justify an incoherent module.
- Check that main calls Interface only, owns process bootstrap and lifecycle duties without business logic or lower-layer construction, and does not auto-start when loaded or linked for tests.
- Verify the default adjacent-layer rule and the narrow Pipeline-to-Provider-public infrastructure exception for imports and runtime calls, including factories, injection, callbacks, and re-exports. Model remains globally shared without operational-layer dependencies.
- Check that affected module dependencies are acyclic, added directories serve the task, and internal splitting does not silently expand public contracts.
- Verify shared contract and public-export rules, including public-entry-only external imports where required and no import-time resource initialization.
- Verify [common and resource rules](shared-directories.md): private role directories have no foreign consumers; shared code is owned by the established project-management role, cataloged and tested; common code does not proxy forbidden calls. Resource references and packaging must be valid, and runtime loading belongs to Provider.

### Contract compatibility

- Required `docs/` records exist, follow the naming convention, contain the applicable type-specific content, and match the final candidate and actual verification evidence. Check referenced files and document links.
- Inputs, outputs, schemas, types, configuration, and error behavior remain compatible unless the task authorizes a contract change.
- Required migrations, callers, and generated artifacts are accounted for when a contract changes.
- No test, assertion, permission boundary, lint rule, or validation policy was weakened solely to admit the candidate.

Use machine-decidable checks when available: changed-path inspection, compiler or type checker, linter, schema validator, dependency rule checker, formatter check, and static policy tests.

If the static gate fails, revise only within the current Mutation Contract. A failure does not authorize a broader rewrite.

## Gate 2: Dynamic Evidence Verification

Apply this gate at each affected layer milestone as defined in the layer-test rules above, and again for final acceptance using current evidence. After the applicable static gate passes, gather finite execution evidence proportionate to the change:

1. Run the narrowest relevant tests first.
2. Run broader regression checks when the change affects shared contracts, dependencies, orchestration, or public behavior.
3. Exercise the changed path with representative inputs when automated coverage is absent or insufficient.
4. Record relevant environment facts such as runtime version, target platform, configuration mode, and unavailable dependencies.
5. Distinguish a failed check from a check that could not run.

Dynamic evidence supports only this statement:

> Under the recorded environment, candidate, inputs, and validation policy, the required observations were satisfied.

It is not proof of universal correctness.

Do not report the dynamic gate as passed when required checks were skipped, unavailable, flaky without resolution, or run against a different candidate.
