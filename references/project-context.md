# Project Understanding Store

Each project has one SQLite database at `project-context/context.sqlite3`. Content rows are filtered by `role_id`; role purpose and mutation paths come directly from `role-card.md` and `boundary.md`. The default Dashboard shows four role-specific overviews: **Flow, Data, Interface, Definition**. It does not need a separate Event overview to explain how a flow starts.

The store is a navigation aid. Canonical interfaces, Model definitions, permissions and implementation evidence remain in accepted designs, `api-spec.md`, source and `boundary.md`. Keep summaries short, link to the current source/contract, and verify claims before changing code.

## Flow triggers and relationships

A Flow topic describes its own trigger conditions, ordered steps, input data, output data and related interfaces. Put a UI button click, keyboard activation, incoming request, schedule or upstream-flow completion directly in `flow.triggers` when it starts that flow. The button control belongs to Interface; the HTTP call it makes for the same user action is a Flow/Interface step, not another trigger record.

For example, `订单导出` can have `when: "用户点击导出按钮"`; `导出完成通知` can have `when: "订单导出流程成功完成"` and `sourceFlow: "order-export"`. Data and Interface topics are referenced by ID and shown directly inside Flow detail. Every accepted Flow should have at least one actual trigger and step. `validate` reports active flows without triggers. Use `sourceFlow` only for a real upstream flow of the same role.

```json
{
  "category": "flows",
  "title": "订单导出",
  "summary": "读取订单并生成导出文件。",
  "flow": {
    "triggers": [{"when": "用户点击导出按钮", "ref": "src/interface/export_button.py"}],
    "steps": [
      {"title": "提交请求", "description": "Interface 调用 POST /api/orders/export"},
      {"title": "读取订单", "description": "按条件查询", "ref": "src/services/orders.py"},
      {"title": "生成文件", "description": "写入导出结果"}
    ],
    "inputs": ["order-record"],
    "outputs": ["export-result"],
    "interfaces": ["order-api"]
  }
}
```

Data topics declare an owner and concrete fields. Interface topics declare an entry, input/output fields and, for HTTP, a method plus request URL. The Dashboard shows those fields in their overviews as well as Flow detail. Referenced topic IDs must already exist under the same role and expected category. For non-HTTP interfaces omit both `method` and `requestUrl`.

```json
{"category":"data","title":"订单记录","summary":"导出的只读输入。","data":{"owner":"订单角色","fields":[{"name":"orderId","type":"string","required":true,"description":"订单编号"}]}}
```

```json
{"category":"interfaces","title":"订单导出接口","summary":"接收条件并返回任务。","interface":{"entry":"orders.export","method":"POST","requestUrl":"/api/orders/export","inputs":[{"name":"status","type":"string","required":false,"description":"状态筛选"}],"outputs":[{"name":"taskId","type":"string","required":true,"description":"导出任务编号"}]}}
```

## AI read and write commands

Use the installed Skill script. All commands require `--root PROJECT --role ROLE`; writes also require `--actor-role ROLE` matching the target role. Reads are filtered to this role. The role's accepted `boundary.md` Section 1 and current task must authorize its logical `role_id` row scope. This CLI checks scope arguments and revisions, but does not authenticate the active AI or human; it is not an OS permission boundary.

```sh
python3 /path/to/skill/scripts/context_store.py --root PROJECT --role orders outline
python3 /path/to/skill/scripts/context_store.py --root PROJECT --role orders list --category flows
python3 /path/to/skill/scripts/context_store.py --root PROJECT --role orders get order-export
python3 /path/to/skill/scripts/context_store.py --root PROJECT --role orders search export
python3 /path/to/skill/scripts/context_store.py --root PROJECT --role orders validate

python3 /path/to/skill/scripts/context_store.py --root PROJECT --role orders --actor-role orders init --input overview.json
python3 /path/to/skill/scripts/context_store.py --root PROJECT --role orders --actor-role orders set-category flows --input category.json --expect-revision 0
python3 /path/to/skill/scripts/context_store.py --root PROJECT --role orders --actor-role orders upsert order-export --input flow.json --expect-revision 0
python3 /path/to/skill/scripts/context_store.py --root PROJECT --role orders --actor-role orders delete order-export --expect-revision 1
python3 /path/to/skill/scripts/context_store.py --root PROJECT --role orders --actor-role orders restore order-export --expect-revision 2
```

`init` creates the database on first use or adds a new role's overview; it does not overwrite existing rows. A new category summary or topic uses expected revision `0`; updates, deletion and restore require the current revision from a fresh read. Delete is a reversible tombstone. `migrate` upgrades version 1–4 databases to version 5 without erasing legacy Event rows; old Event links remain readable and can be converted to direct Flow triggers during an authorized update. Schema changes require the governance workflow, not an execution role's routine content task.

The database records current understanding, not a timeline. Dated design, feature, change and fix history stays in Markdown under `docs/`. After a verified change, the owning role updates affected rows only. Missing or stale rows are navigation gaps, not proof that source behavior is absent.
