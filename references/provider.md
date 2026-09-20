# Provider Constraints

Use this reference with role-card.md's Required reading. Its global call direction, mutation scope, shared contract rules, incremental organization, verification gates, and evidence invalidation remain mandatory.

Provider owns capabilities for infrastructure and external effects: storage, network, filesystem, process, time, and messaging.

## Abstraction Before Implementation

After reviewing the relevant Model contracts, identify the capability consumers need independently of a vendor, SDK, or storage mechanism. Assess whether an existing capability contract can be reused, whether implementation differences fit one contract, or whether distinct semantics require separate contracts. Define the smallest useful inputs, outputs, error behavior, and relevant effect guarantees before implementing an adapter.

Keep vendor details behind the implementation and adapt them to the contract. A single implementation may still justify a capability abstraction. The required `abstract/` directory is not a reason to create inheritance hierarchies, one abstract class per file, or speculative extension points. Multiple implementations sharing a contract must preserve its behavioral guarantees.

## Required Structure

```text
provider/
  abstract/
  impl/
  public/
  # Declared public entry: a module in public/ or a root facade, per repository convention
```

When creating or explicitly restructuring this layer, require both `abstract/` and `impl/`. Define capability contracts in `abstract/` and concrete implementations in `impl/`. Apply the [shared contract and public-export rules](architecture.md). Existing conflicts must be reported and necessary moves and caller edits scoped; do not silently accept deep imports or migrate unrelated code.

## Callers and Exports

Service imports this layer only through the Provider public entry point, including creation functions that return this layer's own contract. A package alias is allowed only when it resolves to that designated public entry point. External consumers use only that declared entry, even when it resides in `public/`; other internal modules in `public/`, `abstract/`, or `impl/` remain off limits.

The designated public entry point explicitly exposes supported API from its own `public/`. Public exposure does not authorize callers from other operational layers. Keep concrete implementations internal and keep selection inside this layer.

## Implementation Growth and Dependencies

Access only authorized infrastructure. Do not call Service, Pipeline, Interface, or peer Providers as a workaround. Runtime loading of `resource/` assets belongs here; keep effectful helpers local rather than in `utils`. Shared Model and permitted helpers remain available.

Grow `impl/` according to the [incremental organization rules](architecture.md): reuse first, add distinct responsibilities or required strategies, and group related files only when useful. Keep private helpers near their implementation. Internal collaboration must be acyclic and cannot conceal cross-component calls. Internal splitting does not automatically expand contracts or public exports.

## Verification

Check contract satisfaction, public-entry-only external imports, explicit public API exposure, absence of import-time resource initialization, and no circular dependencies or leaked implementation classes. Verify affected implementation behavior and caller paths, refreshing evidence for changed contracts or dependencies.

For example, begin with a local-storage module in `impl/`. If an authorized S3 implementation needs related modules, group storage, client, and error modules under `impl/s3/`, using the project language's file extensions. Storage may depend on client and errors; those modules must not depend back on storage. Keep unrelated implementations in place.

## Required Layer Tests

Use the owning role's language-native test suite (see [testing.md](testing.md)); identify its Provider coverage explicitly. Exercise supported operations through the Provider public entry point, including successful results, external-error mapping, and applicable timeout, cleanup, or retry behavior. Run shared contract scenarios against each affected implementation of a capability.

Use controlled infrastructure doubles for unit tests and local or isolated integration checks for changed adapters and SDK mappings; mocks alone do not verify real infrastructure compatibility. Check that loading the public entry point has no resource-initialization effects. Run the exact Provider suite commands recorded in the Mutation Contract and require passing results before dependent Service implementation proceeds.
