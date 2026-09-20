# Pipeline Constraints

Use this reference with role-card.md's Required reading. Its global call direction, mutation scope, shared contract rules, incremental organization, verification gates, and evidence invalidation remain mandatory.

Pipeline owns sequencing, branching, iteration, retry, parallelism, and composition of Services.

## Organization and Dependencies

Create `abstract/` and `impl/` only when a distinct contract and implementation boundary is needed. Otherwise start with focused files and grow purpose-named directories for actual related responsibilities; do not create empty trees for symmetry.

Pipeline may grow files and folders directly, without an `impl/` wrapper. Start with a workflow file and group related steps, branches, retries, and coordination helpers in workflow directories when useful.

Internal workflow modules may collaborate without cycles. Calls outside Pipeline target Service only, through the Service public entry point. Do not call Provider, external infrastructure, or Interface from workflow steps. Model and permitted shared helpers remain available. Keep business transformations in Service and infrastructure effects in Provider. Obtain Service implementations through their exported creation entry points without exposing them to Interface.

## Verification

Check workflow imports and runtime calls for bypasses, including injected capabilities. Verify affected sequencing, branching, retry, and failure paths as appropriate. Directory growth must preserve acyclic dependencies and the adjacent-layer boundary.

## Required Layer Tests

Use the owning role's language-native test suite (see [testing.md](testing.md)); identify its Pipeline coverage explicitly. With contract-compatible Service doubles, exercise the changed workflow's normal path and relevant branches, failure propagation, retry limits, sequencing, and parallel coordination. Assert final results and meaningful intermediate data flow. For retries, verify termination and resulting behavior; for parallel work, avoid assuming an order the contract does not promise.

Run the exact Pipeline suite command recorded in the Mutation Contract and require passing results before dependent Interface implementation proceeds. Add integration coverage for changed Service composition and wiring.
