# Project Understanding Store

The project has one SQLite database at `project-context/context.sqlite3`. Each accepted project role, including the default project role and assembly role, has its own category summaries and topics selected by `role_id`. The Dashboard has direct Flow, Event, Data, Interface, and Definition overviews; clicking an item opens its detail. The AI uses the same role filter and reads only topics relevant to its task.

The database is a navigation aid, not a second specification. Canonical interfaces, event schemas, Model definitions, permissions, and implementation evidence remain in accepted designs, `api-spec.md`, Model/source, and `boundary.md`. Store short explanations and source/contract references, not copies of whole contracts. Mark proposed or uncertain claims in the text. Verify stored claims against current code before changing it.

## Shape and ownership

The shared database has `overview`, `category_summaries`, `topics`, flow steps/relations, event triggers, and reference tables. Each content row has a `role_id`; `topics` have one of five categories: `flows`, `definitions`, `events`, `interfaces`, `data`. Each category has its own short summary, independent of its topics. The Flow overview lists workflows; a flow detail identifies the events that trigger it, ordered steps, input data, output data, related interfaces, and emitted events. An Event topic is a trigger definition: **when it fires, what action runs, and which consumers receive it**. The Dashboard shows related event/data/interface records directly inside the flow detail, while each category has its own overview and item detail. Referenced topic IDs must already exist under the same role and expected category. The CLI returns JSON, so the AI can query one category, topic, or search result without loading the whole database.

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
python3 /path/to/skill/scripts/context_store.py --root PROJECT --role orders --actor-role orders migrate
python3 /path/to/skill/scripts/context_store.py --root PROJECT --role orders --actor-role orders set-category events --input category.json --expect-revision 0
python3 /path/to/skill/scripts/context_store.py --root PROJECT --role orders --actor-role orders set-overview --input overview-updated.json --expect-revision 1
python3 /path/to/skill/scripts/context_store.py --root PROJECT --role orders --actor-role orders upsert order-export --input topic.json --expect-revision 0
python3 /path/to/skill/scripts/context_store.py --root PROJECT --role orders --actor-role orders delete order-export --expect-revision 1
python3 /path/to/skill/scripts/context_store.py --root PROJECT --role orders --actor-role orders restore order-export --expect-revision 2
```

`init` creates the database on the first role and adds another role's overview on later calls. It does not overwrite existing rows. Creating a category summary or topic uses expected revision `0`; editing, deleting, or restoring uses the current revision from a fresh read. Delete is a reversible topic tombstone; ordinary list/get/search omit deleted topics. A stale revision stops the write so the AI must reread and reconcile the current content. `migrate` upgrades an existing version 1 database to version 2 without erasing its rows; it requires the same scoped authorization and does not invent trigger or flow details for old records.

Role overview input:

```json
{"title":"订单角色项目总览","summary":"从导出请求到文件交付，订单角色负责读取并组织结果。"}
```

Flow topic input (create referenced event, data, and interface topics first):

```json
{"category":"flows","title":"订单导出","summary":"读取订单并生成文件。","details":"订单主记录只读。","refs":["docs/design/2026-09-24_design_order-export.md"],"flow":{"triggeredBy":["export-requested"],"steps":[{"title":"读取订单","description":"按筛选条件查询","ref":"src/services/orders.py"},{"title":"生成文件","description":"写入导出文件"}],"inputs":["order-record"],"outputs":["export-result"],"interfaces":["order-api"],"emits":["export-finished"]}}
```

Event topic input:

```json
{"category":"events","title":"导出请求","summary":"用户提交导出条件。","details":"请求通过校验后启动导出流程。","trigger":{"when":"收到有效导出请求","action":"启动订单导出","consumers":["订单导出流程"]}}
```

Category-summary input is `{"summary":"导出请求触发导出流程；导出成功触发通知。"}`. Create the related event, data, and interface topics first, then create the flow topic with their IDs. Flow relation fields are `triggeredBy` and `emits` (Event topics), `inputs` and `outputs` (Data topics), and `interfaces` (Interface topics); `steps` must contain at least one ordered step. Event topics require a `trigger` with `when` and `action`; `consumers` may be empty. The Dashboard reads related details on demand and embeds them in the flow detail. Use the actual relationship rather than linking every topic to every flow.

The database records current understanding, not a timeline. Design, feature, change and fix history remains in dated Markdown records under `docs/`. After a verified change, the owning role updates only affected rows. A cross-role change is reported to the project role, which identifies impacted owners and versions; each affected owner refreshes its own rows after the canonical change is accepted. Missing or stale rows are navigation gaps, not proof that source behavior is absent.
