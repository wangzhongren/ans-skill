# Model Constraints

Use this reference with role-card.md's Required reading. Its global call direction, mutation scope, shared contract rules, incremental organization, verification gates, and evidence invalidation remain mandatory.

Model owns globally shared schemas, types, value objects, events, contracts, and pure behavior that maintains their invariants. It owns neither orchestration nor infrastructure effects.

## Abstraction Before Representation

Design or reuse Model concepts first in the bottom-up construction sequence. Identify shared meaning, identity, units, valid states, and invariants before choosing concrete fields or classes. Consider whether schemas, value objects, or a common contract can express the shared concept while preserving meaningful differences. Abstract Model concepts need not use inheritance or an `abstract/` directory.

Reuse a suitable existing definition; introduce a shared abstraction only when its semantics are clear. Do not merge unrelated data shapes solely because their fields look alike or copy infrastructure-specific representations into the global domain contract without adaptation. Concrete variants must preserve the guarantees of any shared contract.

## Organization and Dependencies

Create `abstract/` and `impl/` only when a distinct contract and implementation boundary is needed. Otherwise start with focused files and grow purpose-named directories for actual related responsibilities; do not create empty trees for symmetry.

Organize by domain or data responsibility, such as `model/order/` or `model/events/`. Reuse shared definitions instead of making copies for each consuming layer. All operational layers may directly use Model; Model must not depend on or call any operational layer. Internal dependencies remain acyclic. Shared access does not authorize mutable global business state.

## Verification

Check that new folders preserve these responsibilities and do not duplicate shared contracts. Validate invariant behavior and compatibility with affected consumers. Changes to shared contracts invalidate affected consumer evidence under the [evidence invalidation protocol](evidence.md).

## Required Layer Tests

Use the owning role's language-native test suite (see [testing.md](testing.md)); identify its Model coverage explicitly. Test valid construction or validation, invalid and boundary values, and the invariants of changed schemas or value objects. Test serialization round trips and compatibility of variants when those are part of the contract. Shared abstractions must have tests demonstrating that concrete variants preserve their guarantees. Keep tests free of infrastructure dependencies.

Run the exact Model suite command recorded in the Mutation Contract and require passing assertions before dependent implementation proceeds.
