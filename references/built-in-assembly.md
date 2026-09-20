# Application Assembly Role

This reference describes how ANS Governance defines a project's assembly capability role. It is not a blanket write grant: resolve concrete paths into the project's accepted `boundary.md` Section 1. Keep the instructions below in the role card or companion description, not extra sections in a capability boundary document.

## Files to Assign

| Responsibility | Required ownership decision |
| --- | --- |
| Application or package entry | The actual language/toolchain entry path; do not require `main.ts` or create an executable for a library |
| Layer-local assembly | Specific Interface/Pipeline wiring files where needed, with no duplicate owner |
| Build and test setup | Concrete manifest, configuration, and test-runner files needed by this project |
| Startup verification | Language-native startup/integration tests, assigned to this role |
| Usage instructions | The actual README or startup guide path |

Do not copy generic descriptions such as "Project config files" into a whitelist as if they were exact paths. Each source or configuration file must have a resolved owner and task scope.

## Reading and Construction

Read the project role's accepted integration designs and participating roles' current `api-spec.md` files to understand exports, dependency requirements, and lifecycle contracts. Read source when specifications are incomplete or verification requires it. Ownership documents may be inspected for routing; they do not grant this role mutation authority over another role's files.

Role ownership and architectural call authority are independent. The assembly role may own several wiring files, but each file can import or construct only capabilities allowed by its own layer:

```text
root startup entry -> Interface startup/lifecycle API
Interface wiring   -> Pipeline
Pipeline wiring    -> Service public entry
Service wiring     -> Provider public entry
Model              -> globally shared, without upward operational dependencies
```

The entry holds an Interface lifecycle handle, not Service or Provider objects. No central factory may import all layers to bypass these rules. Reading every relevant API specification is not permission for main to call every API. Cross-role scope changes return to governance and the owning roles.

## Scheduling and Verification

For coordinated work, the accepted project scheduler dispatches early setup and final integration as separate stages of this role. Assembly workers do not spawn agents or schedule other roles. Return candidate-specific evidence and dependency requests to Scheduler.

1. Prepare the minimal approved build and test environment early, so capability roles can run their required tests. Dependencies need not all be known in advance; update owned configuration as verified needs emerge.
2. Wait for agreed API contracts before writing dependent wiring. Work against compatible doubles can support isolated preparation, but does not establish integration success.
3. Integrate only after participating implementations pass their gates. Unrelated roles need not finish first. Apply [dependency-aware scheduling](bootstrap-workflow.md#dependency-aware-scheduling).
4. Follow [entrypoint.md](entrypoint.md) for startup, partial-failure cleanup, repeated shutdown, import safety, and the real-start smoke test. Verify cross-layer wiring with actual implementations in an appropriate isolated environment.

## See also

- [Role card](role-card.md)
- [API specification](api-spec.md)
- [Module boundary](module-boundary.md)
