# Interface Constraints

Use this reference with role-card.md's Required reading. Its global call direction, mutation scope, shared contract rules, incremental organization, verification gates, and evidence invalidation remain mandatory.

Interface owns boundary adaptation for HTTP, CLI, RPC, events, scheduled jobs, or GUI entry points. Adapt inputs and outputs and delegate orchestration to Pipeline.

## Organization and Dependencies

Create `abstract/` and `impl/` only when a distinct contract and implementation boundary is needed. Otherwise start with focused files and grow purpose-named directories for actual related responsibilities; do not create empty trees for symmetry.

Organize by transport, entry point, or feature, such as `interface/http/orders/`, `interface/cli/`, or `interface/events/`. Internal adapter modules may collaborate without cycles.

Call and construct Pipeline only. Do not directly call Service or Provider, acquire lower-layer capability objects, or move business orchestration into adapters. Shared Model and permitted helper use remain available. Additional subdirectories do not expand these permissions.

## Startup and Lifecycle Boundary

Expose a designated startup operation for the root application entry file with plain startup options and an explicit readiness result. Return an Interface-owned shutdown handle rather than Pipeline, Service, or Provider objects. Create and manage required Pipeline dependencies within the adjacent-layer rule; lower layers retain ownership of their resources.

Handle cleanup after partial startup failure and make shutdown safe to repeat, propagating cleanup through adjacent-layer lifecycle operations. Keep process signal registration and exit-status handling in main. Interface modules must not import main or start the application merely by being imported. See the [root-entry rules](entrypoint.md) for bootstrap tests and the real-start smoke test.

## Verification

Check that boundary parsing, mapping, output, and error behavior remain compatible unless changes are authorized. Verify affected adapters delegate to Pipeline and that new folders preserve dependency direction and acyclic internal organization.

## Required Layer Tests

Use the owning role's language-native test suite (see [testing.md](testing.md)); identify its Interface coverage explicitly. Exercise the changed HTTP, CLI, event, or GUI boundary with controlled Pipeline behavior. Assert input parsing and validation, correct delegation inputs, output formatting or status/exit codes as applicable, and mappings of relevant Pipeline failures. Invalid requests must not trigger execution when the boundary contract requires rejection first.

Run the exact Interface suite command recorded in the Mutation Contract and require passing results before declaring the entry point complete. Also verify the affected user-facing path through connected layers in a suitable local or isolated integration test.
