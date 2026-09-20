# API Specification Format

The default project role owns the canonical inter-role integration design under [project-role.md](project-role.md). Each capability role maintains `api-spec.md` as an implementation report alongside its card and boundary: actual exports, compatibility with the design, and test evidence. It does not independently redefine the shared contract. Assembly reads both the accepted design and these reports, verifying unclear details in source.

## Template

Use the project's actual programming language and naming conventions. Replace the illustrative descriptions with real signatures and paths; do not invent an exported class or function.

```markdown
# API Specification: <Role name>

## Design Reference
- Canonical integration document, contract ID/revision, and acceptance reference.
- Implementation status and unresolved deviations; a proposed API is not a completed export.

## Exports
- Declared public entry path, operation/signature, input/output types, and allowed caller layer.
- Error behavior, relevant lifecycle guarantees, and implementation readiness.

## Dependencies
- Required capability/contract, its owning role, entry path, and readiness/version.
- Shared Model contracts as read-only references; identify their primary owner.

## Public Types
- Supported types exposed through the declared public entry or shared Model API.
- Do not require consumers to import private abstract or implementation files.

## Assembly Notes
1. Identify the wiring file's architectural layer and authorized owner.
2. Describe how that file obtains only its immediately lower-layer capability.
3. State required initialization order and resource ownership.
4. Describe readiness, shutdown, and failure propagation through adjacent layers.

## Verification
- Relevant contract/integration test commands and current results or pending checks.
```

A game project's Pipeline may register steps in a game loop, but that is a project-specific example, not a universal startup contract. Likewise, `.ts` signatures or any specific framework API are examples only.

## Rules

- The implementation owner maintains its report within its accepted documentation scope. Propose shared-contract changes to the project role before implementing a deviation; the project role coordinates the design revision and Governance handles any permission changes.
- Assembly reads only the participating API specifications before dependent wiring; access to a specification does not permit cross-layer imports.
- Incomplete implementations or stale tests must be marked explicitly. Update affected consumers and invalidate evidence when contracts change.

## See also

- [Role card](role-card.md)
- [Application assembly](built-in-assembly.md)
