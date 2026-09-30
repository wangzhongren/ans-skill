# Unified Task Operations

Use [task_ops.py](../scripts/task_ops.py) instead of editing coordination JSON by hand. The CLI validates role/scope policy, stage prerequisites, revision acknowledgments, feedback identity and evidence, then writes the journal, state and derived board through one locked store. It does not create agents, enforce OS file permissions, or independently authenticate customer identity.

## Trust and Scope

1. The customer/operator reviews a project configuration (version 1 uses JSON, usually `.ans/project.json`) and passes its exact SHA-256 when initializing a task. The digest pins reviewed content; computing a digest is not proof of customer consent. An AI must not generate a broader policy and describe its own hash as customer approval. Production integrations must obtain this pin/consent from a trusted host or actual customer approval workflow.
2. Configuration names each execution role, its card and boundary paths, exact `writeFiles`, permitted `operations`, automatic dispatch permission, and approved check commands. A configured file must either appear as a backtick path in Section 1 table rows or fall inside an accepted common/test subtree written with a trailing `/`, such as `src/common/orders/`, `src/common/shared/` or `test/qa/`. Whole `src/`, `common/` or test-root grants do not qualify. Duplicate or overlapping ownership among configured roles is rejected. Config `writeFiles` and plan `writeSet` still use exact paths, not directory patterns; directory ownership does not widen a running assignment. Governance assigns shared to project management and tests to their proper owners; the CLI checks the accepted paths, not role meaning inferred from names.
3. A plan's write set can only narrow that role scope. Config or role-definition changes invalidate subsequent operations. Without `autoDispatch: true`, dispatch needs a separately reviewed consent receipt and pinned hash matching this task, node, role, worker, operation, write set, plan revision and the next attemptNumber. Pass the receipt inline in a private standard-input request, or use an already approved consent file. A digest supplied by the AI is not customer consent. Explicit activation consent cannot be replayed for another attempt.
4. The process runs as the local OS user. Anyone able to rewrite trusted inputs and invoke the tool as that operator is outside its security boundary. Actual source writes occur in the worker's tools, not this CLI: use isolated checkouts and filesystem/tool restrictions for prevention. It checks declared changed paths but cannot attribute arbitrary filesystem edits to individual agents sharing the same OS account.

## Configuration and Plan

Illustrative configuration (replace every path and command with reviewed project values):

```json
{
  "schemaVersion": 1,
  "maxConcurrentWorkers": 2,
  "designFiles": ["docs/design/export.md"],
  "allowDesignRevision": true,
  "allowRequirementRevision": false,
  "roles": {
    "orders": {
      "card": "role-cards/orders/role-card.md",
      "boundary": "role-cards/orders/boundary.md",
      "writeFiles": ["src/services/orders.py", "tests/test_orders.py"],
      "operations": ["repair"],
      "autoDispatch": true,
      "checks": {
        "unit": {"argv": ["python3", "-m", "unittest", "discover", "-s", "tests"], "timeoutSeconds": 60}
      }
    }
  }
}
```

A plan has `schemaVersion: 1`, `taskId`, requirement/design references (`path`, human-readable `version`), and a node array. Each node includes `nodeId`, `roleId`, `stage`, `operation`, exact `writeSet`, `readSet` for relevant unchanged inputs, `requiredOutputs` (defaults to writeSet), `checks` (approved IDs), and `dependsOn` (node IDs). Hashes are calculated by the tool. Required outputs must belong to the write set. Relevant harnesses and fixtures should be in readSet so changing them invalidates evidence.

V1 prerequisites require the referenced stage to be verified with a current candidate. Model contract establishment can be a separate verified stage; do not encode an entire role as one unavoidable dependency. Unknown prerequisites and cycles are rejected.

## Command Interface

All operations use the same entry point. Read a JSON request from standard input without creating a task request file:

```sh
python3 /path/to/skill/scripts/task_ops.py --root /path/to/project --task repair-export init --request -
python3 /path/to/skill/scripts/task_ops.py --root /path/to/project --task repair-export status
```

The init request is `{"configPath":".ans/project.json","approvedConfigSha256":"<customer-reviewed digest>","plan":{...}}`. Initialization also returns a coordinatorToken, distinct from worker tokens. Keep it in the trusted host/private operator storage; do not send it to workers. A host can generate and securely save a random token of at least 32 characters before init and supply it as coordinatorToken to avoid losing the credential if delivery is interrupted. Paths inside configuration/plan are project-relative. Use `--request -` to read a JSON request from standard input without creating a request file; a private external request file remains possible when the caller needs one.

| Operation | Required request / result |
| --- | --- |
| `init` | Reviewed config pin and plan; creates the task only if no managed/unmanaged records would be overwritten; returns coordinatorToken |
| `dispatch` | coordinatorToken, nodeId, workerId, and when required inline `consent` or `consentPath` plus its approvedConsentSha256; returns narrowed assignment, attemptId, revisions and a one-time plaintext token |
| `ack` | Returned assignment fields; confirms the worker uses the assigned revisions |
| `run-check` | Assignment fields plus checkId; executes only a configured argv without a shell, within a 1–300 second configured timeout, and records actual output, exit code and candidate hashes |
| `report` | Assignment fields plus reportId, kind (`progress`, `issue`, `complete`), summary and changedPaths where relevant; rejects stale/out-of-scope feedback and deduplicates identical reports |
| `stop` | Assignment identity/token and summary confirming the old worker has stopped; releases the reservation, but does not kill a process or prove it stopped |
| `revise` | coordinatorToken, document (`design` default or `requirement`), new version, affected node IDs, reason, optional revised dependencies, and unaffectedReason when some nodes are excluded; requires the corresponding pinned policy permission and changed document content |
| `verify` | coordinatorToken, nodeId; requires a completion report, unchanged candidate, every approved check passing, unchanged evidence files and required outputs present |
| `status` | No request; returns recorded state with assignment token hashes/history removed |
| `recover` | coordinatorToken; verifies and returns the last complete task document after an interruption |

Coordinator-only commands (dispatch, revise, verify, recover) require the private coordinator credential. Worker credentials cannot invoke those commands; only token hashes are stored in state/history. Legacy pre-release tasks without coordinator hashes remain readable but require a new initialized task for mutations. No recovery command bypasses a missing credential.

Pass the returned assignment only to the designated worker. Store its token privately, never in public docs or logs. The task state stores token hashes; attempts and worker IDs remain fixed. Without an acknowledgment, a worker cannot run checks or submit current execution feedback. A dispatched worker remains reserved until accepted verification or a valid stop acknowledgment. Failed/blocked retries need a concrete retryReason.

`dispatch` is an authorization/reservation operation, not an agent launcher. The project role invokes the available subagent tool only after it succeeds, supplies the assignment and role documents, and records worker identity consistently. If launching fails, reconcile the reservation with a stop acknowledgment. Workers return reports through the project-controlled operation path; possession of a worker token does not grant coordinator commands or OS permissions.

Exit codes: 0 successful operation (including idempotent duplicate report), 2 rejection/error, 3 authenticated but rejected feedback, 4 executed check failed or changed the candidate. A failure can be durably recorded even when the command exits nonzero; read status before retrying.

## Revision and Integration Flow

1. Record an issue and stop relevant dependent dispatch. A design/requirement revision is a real document edit by its authorized owner; revise records the new hash/version and affected stages rather than editing the design itself.
2. The tool includes dependent nodes transitively. It can update prerequisites among existing stages, but cannot expand node permissions or change role/check definitions. Adding roles or task write authority requires reviewed configuration and a new task in v1. A new common/test file inside an already accepted directory needs no per-file role-boundary change, but it must be listed in the pinned configuration and task before execution.
3. Active affected stages become blocked with pauseRequested and retain their reservations. The operator must stop/reconcile the actual worker, then submit stop using the old assignment. Old-version reports are kept as rejected history and cannot mark the revised stage complete.
4. Redispatch creates a new attempt/token and requires a new revision acknowledgment. Re-run checks and report completion; coordinator verify marks the stage verified only for current evidence. Downstream dispatch rechecks prerequisite candidate hashes.

For partial revisions, unaffectedReason documents the semantic judgment. The tool follows the declared graph and cannot discover every hidden dependency; the project role must inspect actual impact. Separately passing stages do not replace the final assembly/integration stage.

## Persistence and Recovery

[coordination_store.py](../scripts/coordination_store.py) writes `docs/scheduling/<task-id>.md`: a readable plan and step table followed by an ordered, hash-linked machine event block in the same file. The program verifies event order, hashes and the rendered human section before any operation. An atomic file replacement commits the entire update; if writing fails before replacement, the previous complete record remains current. `recover` checks that record and reports its current state; it cannot invent an uncommitted event. Hash chaining detects inconsistent edits, not an operator who deliberately rewrites all hashes. The local OS lock and check output live under `.ans/runtime/`; its `.gitignore` keeps temporary files out of Git. Checks run while holding the writer lock; concurrent operations fail fast.

The Markdown record can be committed with the project. A Git merge conflict or manual edit invalidates its machine section and blocks new work until the project manager reconciles it. Different tasks have different files. A new checkout can read committed plans/history, but running assignments and local test logs are not automatically portable. Before dependent work continues, recheck source and required evidence; unavailable local check evidence blocks downstream dispatch. The trusted host must carry private credentials separately, or start a newly authorized task after reconciling the previous worker. Existing JSON task directories remain visible in the optional Dashboard, not writable by the new task tool.

The dashboard consumes the validated Markdown task record directly and can still display older JSON task directories. Its task view remains read-only and displays stored outcomes, not an independent permission verdict. The optional shared role channel may record messages and administrator decisions in its separate project database tables; these do not change task authorization, state or evidence. Task records contain complete snapshot events and can grow; use bounded tasks and retain/archive finished runs under project policy rather than treating this as a high-throughput distributed scheduler.

## Verified Case and Limits

The pause/resume regression harness at [timer_regression.cjs](../scripts/tests/helpers/timer_regression.cjs) runs actual game-engine Timer/GameLoop/Engine source using Node's TypeScript stripping in an isolated VM. It proves the original cumulative-time reset and checks the revised lifecycle. It is not a TypeScript compiler check or full browser/DOM integration test.

Run all tests with `python3 -m unittest discover -s scripts/tests -v`. Unit cases cover authorization, version pinning, dependency release, duplicate feedback, stale evidence, real check failures, locks, journal recovery and dashboard compatibility. A separate case report records the actual cross-role execution and its evidence.

## Reproduce the Full Validation

[validate_task_flow.py](../scripts/validate_task_flow.py) replays the real timer regression with the repair produced by a mainloop execution agent and independently checked by an assembly execution agent. It uses a new output directory, verifies the expected original baseline, and leaves original sources untouched. It does not spawn agents during replay.

```sh
python3 scripts/validate_task_flow.py --source test/game-engine --output output/new-validation-run --node /absolute/path/to/node
```

Node must provide `node:module.stripTypeScriptTypes` (the bundled Node runtime does). The run checks actual failures before the fix, revised design pause/stop/redispatch, stale-feedback rejection, dependency gating, worker self-verification rejection, current test evidence, final acceptance, and unchanged original source. It creates real plan/state/event/board records under the isolated output for dashboard inspection.
