# Project Understanding Store

The project has one SQLite database at `project-context/context.sqlite3`. Each accepted project role, including the default project role and assembly role, has its own overview and topics selected by `role_id`. The Dashboard opens a role's overview first; readers then click through category, topic, and detail. The AI uses the same role filter and reads only topics relevant to its task.

The database is a navigation aid, not a second specification. Canonical interfaces, event schemas, Model definitions, permissions, and implementation evidence remain in accepted designs, `api-spec.md`, Model/source, and `boundary.md`. Store short explanations and source/contract references, not copies of whole contracts. Mark proposed or uncertain claims in the text. Verify stored claims against current code before changing it.

## Shape and ownership

The shared database has `overview`, `overview_steps`, `category_summaries`, `topics`, and reference/link tables. Each content row has a `role_id`; `topics` have one of five categories: `flows`, `definitions`, `events`, `interfaces`, `data`. `overview` gives a concise flow from entry through this role to the next role or output. Each category has its own short summary, independent of its topics. A topic expands one subject. Flow steps and flow topics can link to event, data, and interface topic IDs. The Dashboard shows those linked records directly in the flow, while each category remains browsable on its own. All linked IDs must already exist under the same role. The CLI returns JSON, so the AI can query one category, topic, or search result without loading the whole database.

One file is shared, but content ownership is by row. A role may change only rows with its own `role_id`, through the provided CLI, when its accepted `boundary.md` Section 1 includes that logical row scope and the current task authorizes the change. The CLI requires `--actor-role` to match `--role` on writes and checks the expected record revision. This is a workflow guard, not identity authentication or an OS permission boundary; do not edit the SQLite file directly or issue raw SQL. Schema changes belong to Skill governance, not to an execution role's content task.

`flows` records participating workflows and upstream/downstream roles; `definitions` clarifies terms; `events` names triggers, producers and consumers; `interfaces` indexes provided/consumed public entries and contract IDs; `data` records read/write effects and the primary owner. Use only categories with real evidence. `functional-description.md` continues to explain a role's own implementation in detail.

## AI CRUD entry point

Use the installed Skill script. All operations need `--root PROJECT --role ROLE`; writes additionally need `--actor-role ROLE`. `--role` must name a direct role folder with a role card. The input path may be `-` for stdin.

```sh
python3 /path/to/skill/scripts/context_store.py --root PROJECT --role orders outline
python3 /path/to/skill/scripts/context_store.py --root PROJECT --role orders get-category events
python3 /path/to/skill/scripts/context_store.py --root PROJECT --role orders list --category flows
python3 /path/to/skill/scripts/context_store.py --root PROJECT --role orders get order-export
python3 /path/to/skill/scripts/context_store.py --root PROJECT --role orders search timeout

python3 /path/to/skill/scripts/context_store.py --root PROJECT --role orders --actor-role orders init --input overview-initial.json
python3 /path/to/skill/scripts/context_store.py --root PROJECT --role orders --actor-role orders set-category events --input category.json --expect-revision 0
python3 /path/to/skill/scripts/context_store.py --root PROJECT --role orders --actor-role orders set-overview --input overview-linked.json --expect-revision 1
python3 /path/to/skill/scripts/context_store.py --root PROJECT --role orders --actor-role orders upsert order-export --input topic.json --expect-revision 0
python3 /path/to/skill/scripts/context_store.py --root PROJECT --role orders --actor-role orders delete order-export --expect-revision 1
python3 /path/to/skill/scripts/context_store.py --root PROJECT --role orders --actor-role orders restore order-export --expect-revision 2
```

`init` creates the database on the first role and adds another role's overview on later calls. It does not overwrite existing rows. Creating a category summary or topic uses expected revision `0`; editing, deleting, or restoring uses the current revision from a fresh read. Delete is a reversible topic tombstone; ordinary list/get/search omit deleted topics. A stale revision stops the write so the AI must reread and reconcile the current content.

Initial overview input (before linked topics exist):

```json
{"title":"订单角色项目总览","summary":"请求进入后读取订单，再生成导出结果。","steps":[{"title":"入口","description":"接收导出请求","ref":"src/interface/orders.py"}]}
```

After the referenced topics exist, `set-overview` can add their IDs to the relevant step:

```json
{"title":"订单角色项目总览","summary":"请求进入后读取订单，再生成导出结果。","steps":[{"title":"入口","description":"接收导出请求","ref":"src/interface/orders.py","links":["order-created","order-record","order-api"]}]}
```

Topic input:

```json
{"category":"flows","title":"订单导出","summary":"订单服务读取数据并生成文件。","details":"此角色只读取订单主记录。","refs":["docs/design/2026-09-24_design_order-export.md","角色卡/订单/api-spec.md"],"links":["order-created","order-record","order-api"]}
```

Category-summary input is `{"summary":"订单创建事件由订单角色产生，导出流程消费它。"}`. Create the linked event, data, and interface topics first, then update the overview or flow topic with their IDs. The Dashboard reads their details on demand and embeds them in the flow; it also displays the same records through the separate category pages. Use the actual relationship rather than linking every topic to every flow.

The database records current understanding, not a timeline. Design, feature, change and fix history remains in dated Markdown records under `docs/`. After a verified change, the owning role updates only affected rows. A cross-role change is reported to the project role, which identifies impacted owners and versions; each affected owner refreshes its own rows after the canonical change is accepted. Missing or stale rows are navigation gaps, not proof that source behavior is absent.
