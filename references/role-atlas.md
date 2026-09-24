# Role Graphs and Function Walkthroughs

Use only when the user requests a role graph, a feature walkthrough, or changes to a requested role visualization. Whole-project code atlas generation remains optional. This tool creates bounded per-role views, not a new default scanning obligation.

## Generate and Open

```sh
python3 scripts/role_atlas.py --root /path/to/project --flows doc/design/role-flows.json
python3 scripts/serve_dashboard.py --root /path/to/project --port 8768
```

This legacy walkthrough is optional and no longer appears in the default Dashboard. After explicitly generating it, open `/role-atlas` on the printed local server URL for standalone inspection. Use `--role ROLE_ID` to rebuild one role while preserving other index entries; `--roles relative/path` selects a nonstandard role directory. Default output is the project-root `doc/role-atlas/`, with index.json and one hashed filename per role. An explicit `--out` is available for exporting data elsewhere; the bundled server currently reads the default location.

The generator reads role cards and boundary Section 1, then only selected declared files, their direct known references, function-step evidence, and role functional descriptions. It does not invoke the whole-codebase scanner. Read-only references remain marked read-only; multiple ownership declarations are exposed as warnings rather than silently treated as valid permissions.

Functional descriptions may be at the role root or in existing nested docs folders. They are located and fingerprinted without moving the user's documents. With no flow definition, a role still has an honest file overview but no invented executable steps.

## Define Functions as Data

The owning project/design role reads the functional description and relevant implementation, then writes a declarative flow specification inside its authorized document scope. No generated sequence should be presented as a measured runtime trace.

```json
{
  "schemaVersion": 1,
  "roles": {
    "orders": [{
      "id": "create-order",
      "name": "创建订单",
      "description": "依据功能说明和当前源码解释创建路径。",
      "scenarios": [{
        "id": "success",
        "name": "正常输入",
        "inputs": {"itemCount": 1},
        "initialState": {"orderCount": 0},
        "steps": [{
          "title": "写入订单",
          "file": "src/services/orders.ts",
          "symbol": "Orders.create",
          "quote": "this.orders.set(order.id, order);",
          "occurrence": 1,
          "description": "示例订单写入容器。",
          "set": {"orderCount": 1}
        }]
      }]
    }]
  }
}
```

`roles` keys match actual role-directory IDs. Each scenario supplies explicit initial state and ordered steps. Steps must point to declared role files (including explicitly shown external role references) and exact source text; occurrence selects a match when a quote appears more than once. The generator locates line numbers and stores source hashes. A missing source anchor rejects generation before outputs are written.

`set` is a top-level data patch only. It cannot contain executable expressions, shell commands or browser code. Values such as “two updates” are authored examples, not independently calculated program results. Branches are separate selectable scenarios with clear preconditions; do not invent external API responses without labeling them assumptions. Use warning text when documentation differs from the current code, and show current code behavior rather than pretending a proposed fix already exists.

Step ordering is the described control-flow storyboard, not automatically derived from imports. File-overview edges are separately labeled heuristic static references. Source-anchored text verifies location and freshness, not every semantic conclusion; verify important calculations or error behavior with real tests when needed.

## Viewer Behavior

1. Project overview lists all generated roles. Role overview groups declared/read-only/direct-dependency files by layer and shows incoming/outgoing references for the selected file.
2. Function mode allows feature and scenario selection, previous/next, reset, direct step selection, and timed autoplay. Active and visited nodes are highlighted; state changes and a source quote are displayed beside the diagram.
3. Returning to an earlier step uses its stored state snapshot; resetting or switching features/scenarios restores the initial state. Playback stops when complete, when leaving the feature view, when the page becomes hidden, or when source freshness fails.
4. The local server checks the graph's recorded source hashes on requests; the viewer rechecks approximately every five seconds. Changed or removed source, role docs, or flow definitions pause the walkthrough until regenerated. Disconnection pauses playback and marks the displayed snapshot as stale.
5. The source-context endpoint exposes only files/documents in the chosen role graph, stays within the project, and rejects traversal/symlink escapes. Text is displayed as text, not HTML. The viewer never executes application code, sends real provider requests, modifies source, grants role permission, or updates scheduler state.

## Generated Artifacts and Tests

- [Generator](../scripts/role_atlas.py)
- [Viewer](../assets/role-atlas/index.html)
- [Read-only server](../scripts/serve_dashboard.py)
- [Tests](../scripts/tests/test_role_atlas.py)

Generated role data can be included in task artifacts when requested. Do not load every role JSON into the model's context: inspect only the role/function needed. Freshness is conservative; modifying a shared specification file can mark several roles stale.

The current example under `test/game-engine/doc/design/role-flows.json` covers eight roles, nine functions and fifty steps. It includes normal/error scenarios and a warning for the original timer resume-reset defect. These are source-anchored walkthroughs, not full execution recordings.
