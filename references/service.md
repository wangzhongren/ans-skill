# Service Constraints

Use this reference with role-card.md's Required reading. Its global call direction, mutation scope, shared contract rules, incremental organization, verification gates, and evidence invalidation remain mandatory.

Service owns bounded business transformations.

## Abstraction Before Implementation

After reviewing Model contracts and available Provider capabilities, identify the business outcome, inputs, outputs, invariants, and failure semantics before coding the transformation. Assess whether an existing operation can be reused and whether varying business strategies genuinely share a contract. Keep distinct business meanings separate even when their code looks similar.

Define a narrow business-operation abstraction in `abstract/`, then implement it using permitted Provider contracts. One implementation can be sufficient; prefer composition or a simple callable contract when inheritance adds no value. Do not abstract a multi-Service workflow into a Service: that composition belongs to Pipeline. Finish the required Service capabilities before composing the workflow.

## Required Structure

```text
service/
  abstract/
  impl/
  public/
  # Declared public entry: a module in public/ or a root facade, per repository convention
```

When creating or explicitly restructuring this layer, require both `abstract/` and `impl/`. Define business-operation contracts in `abstract/` and concrete implementations in `impl/`. Apply the [shared contract and public-export rules](architecture.md). Existing conflicts must be reported and necessary moves and caller edits scoped; do not silently accept deep imports or migrate unrelated code.

## Callers and Exports

Pipeline imports this layer only through the Service public entry point, including creation functions that return this layer's own contract. A package alias is allowed only when it resolves to that designated public entry point. External consumers use only that declared entry, even when it resides in `public/`; other internal modules in `public/`, `abstract/`, or `impl/` remain off limits.

The designated public entry point explicitly exposes supported API from its own `public/`. Public exposure does not authorize callers from other operational layers. Keep concrete implementations internal and keep selection inside this layer.

## Implementation Growth and Dependencies

Call declared or already authorized Providers only, through the Provider public entry point. Do not orchestrate peer Services or call Pipeline or Interface. Multi-Service composition belongs to Pipeline. Do not access infrastructure directly or expose Provider objects to Pipeline. Shared Model and permitted helpers remain available.

Grow `impl/` according to the [incremental organization rules](architecture.md): reuse first, add distinct responsibilities or required strategies, and group related files only when useful. Keep private helpers near their implementation. Internal collaboration must be acyclic and cannot conceal cross-component calls. Internal splitting does not automatically expand contracts or public exports.

## Verification

Check contract satisfaction, public-entry-only external imports, explicit public API exposure, absence of import-time resource initialization, and no circular dependencies or leaked implementation classes. Verify affected implementation behavior and caller paths, refreshing evidence for changed contracts or dependencies.

## Required Layer Tests

Use the owning role's language-native test suite (see [testing.md](testing.md)); identify its Service coverage explicitly. Exercise business operations through the Service public entry point with contract-compatible Provider doubles. Assert expected business results, invalid-input or business-rule failures, and handling of relevant Provider failures. Check requested effects and their meaningful inputs when the operation performs them, rather than asserting call counts alone. Apply shared business-contract cases to each affected strategy.

Run the exact Service suite command recorded in the Mutation Contract and require passing results before dependent Pipeline implementation proceeds. Add integration coverage when Service-to-Provider wiring or contracts change.
