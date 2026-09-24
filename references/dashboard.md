# Local Role Dashboard

The [dashboard server](../scripts/serve_dashboard.py) serves the [local HTML viewer](../assets/role-dashboard/index.html) using Python 3 standard-library HTTP tools. It reads the [coordination records](coordination.md); it neither dispatches workers nor authorizes actions. Python is the tool implementation language, not a business-project requirement.

## Default Per-Project Workflow

1. After bootstrap acceptance, the default project role loads this reference and establishes a dashboard for the actual project. Reuse a known running URL only after its `/api/snapshot` projectRootUri matches the selected project. Do not probe arbitrary ports or reuse another project's page based only on the folder name.
2. If no matching session is known, launch the installed Skill's server with an absolute script path, `--root` set to the actual project and `--port 0` to choose a free port. Keep the process in the task's managed terminal/session. Record its printed URL and process/session identifier in the task handoff, and avoid starting another instance for each worker or turn.
3. Open the Dashboard with available app/browser tools and provide its URL. On resume, check the known session and reconnect or restart if needed. On completion, include the current URL and any hosting limitation; do not claim the process will survive app shutdown or reboot.
4. The project role maintains approved plan/state/event records through the task gateway. Execution roles send feedback, not separate dashboards. Missing records remain unreported. The UI includes role overview, tasks, events and role-function walkthroughs in one place.
5. Role graph content belongs to the actual project: generate its role overviews from accepted boundaries, and author function scenarios from its functional descriptions and real source once implementations exist. Keep generated graph/flow document paths in the project role's accepted design-output scope. Do not copy example functions or fabricate steps for source that does not exist. Only relevant role graph data is generated/loaded; the whole-codebase atlas remains opt-in.

This is a standard workflow for this Skill, not a game-engine feature or an extra application module. Do not copy dashboard code into the project's src/ or test/ directories. Reuse the installed assets and scripts, and let each project supply its own metadata. Respect an explicit user opt-out and unavailable hosting permissions; do not deploy remotely or add a persistent system service implicitly.

## Start and Stop

From the Skill directory:

```sh
python3 /path/to/installed-skill/scripts/serve_dashboard.py --root /path/to/project --port 0
```

Open the printed loopback URL, for example `http://127.0.0.1:<printed-port>`. Stop with Ctrl+C in its terminal. The server runs while that process is alive; this is not a scheduler, background automation, or persistent service installation. Use `--port 0` for an automatically chosen free port if needed.

`--root` is the project root containing role and documentation folders, not automatically `src/`. The server recognizes direct role directories under `角色卡/` or `role-cards/` and task directories under both `docs/scheduling/` and `doc/scheduling/`. Override with `--roles relative/role-directory` and `--scheduling relative/scheduling-directory`; both must resolve within the project. Each task directory contains plan.json, state.json and events.jsonl. No source scan or business program execution is performed.

Do not modify business records merely to make the dashboard look populated. Role cards without task states display as unreported; missing stage records are not evidence that a role is idle or complete.

The dedicated **项目理解** view shows role purpose and mutation paths from its role card and boundary document, plus five direct overview tabs: Flow, Event, Data, Interface, and Definition. Each tab shows its category summary. Data and Interface overviews additionally show each item's concrete fields; HTTP interfaces show their method and request URL. Clicking an item opens its detail. A Flow detail shows its triggering events, ordered steps, input and output data, related interfaces, and emitted events. An Event detail shows its trigger condition, action, and consumers. Related event/data/interface details appear directly inside the Flow detail without an extra click. Clicking a role card opens this view for that role. The index refreshes from the [shared SQLite store](project-context.md) with the dashboard snapshot; item details are read only when selected or referenced by a flow. Missing context is shown as missing, not synthesized from another role or from the sample project.

## Data Adapter

Plan and state require `schemaVersion: 1`, matching `taskId` and `planRevision`, and `nodes` as either an array or object keyed by node ID. Each plan node identifies `nodeId` (or `id`), `roleId` matching its role folder name, optional title/objective and stage. `dependsOn` is an optional array of node IDs or objects with `nodeId`.

State headers include nonnegative integer `stateRevision` and `lastEventSeq`, plus `updatedAt`. Node state follows coordination.md; the viewer currently displays these concrete field shapes:

```json
{
  "nodeId": "export-impl",
  "roleId": "export",
  "attemptId": "attempt-1",
  "status": "running",
  "assignedRevisions": {"requirement": "R2", "design": "D3"},
  "acknowledgedRevisions": {"requirement": "R2", "design": "D3"},
  "latestReport": {"reportId": "report-1", "summary": "Implementation in progress"},
  "nextAction": {"summary": "Run contract tests", "responsibleRole": "export"}
}
```

This is an illustrative node, not a claim of real execution. Events are newline-delimited JSON objects with unique `eventId`, contiguous `seq` starting at 1, `taskId`, optional known `nodeId`, `kind` (or `type`), summary, and received/reported timestamp. State.lastEventSeq must agree with the log. Empty history is an empty file with lastEventSeq 0. The protocol's other evidence/approval fields remain in source records; the viewer does not validate every contract or authorization condition.

## Display Behavior

1. Role cards show the actual names, descriptions and available boundary documents. Search matches names and descriptions. A role with multiple stages shows the highest-attention recorded state, with stage details available separately.
2. Stage rows show recorded status, requirement/design references, feedback and next action. Click a row for its current loaded record. Opening a detail is a snapshot of that moment; close/reopen it to inspect subsequent changes.
3. The event feed shows up to 100 recent entries across tasks. Requirements and design changes remain events, not invented execution states. Each task's sequence preserves its own order; timestamp sorting across tasks is for display only.
4. The page requests a fresh snapshot approximately every 2 seconds. Unchanged data does not rebuild role cards, preserving input and interaction stability. Network failure keeps the previous snapshot with an explicit stale/disconnected notice; a successful retry restores the connected display.
5. Invalid JSON, missing files, unknown roles/nodes, revision mismatches, or inconsistent event sequences produce visible warnings. Affected recorded statuses are not presented as verified. Source files are never repaired by the dashboard.

A green connection means the local record reader responded, not that worker processes are online. A displayed verified status reports the project role's stored decision, not an independent verification of code or test evidence. Records can be old even while polling works; inspect their own timestamps and versions.

## Local Read-Only Boundary

The server binds only to 127.0.0.1, serves no remote assets, and does not expose a write API. It checks loopback Host values, restricts Markdown document reads to named files in direct role folders, and reads project understanding through a role-filtered, read-only SQLite connection. Outside-root paths and symlink escapes are rejected. Dynamic text is rendered with textContent, not interpreted as HTML.

This is a local observation tool, not an authenticated multi-user deployment. Do not expose it through a public proxy without a separate authorization and security design. Records larger than 2 MiB are reported instead of loaded; it is intended for bounded task records, not unbounded production logs.

## Verification

```sh
python3 -m unittest discover -s scripts/tests -v
```

Dashboard tests cover disk rereading, missing and inconsistent state, node maps, role resolution, event sequencing, traversal/symlink rejection, and read-only HTTP behavior. Browser checks should cover search, role document viewing, tab navigation, polling changes, disconnection, and layout. Use isolated fixture records for simulated states; do not alter real project coordination records for testing.
