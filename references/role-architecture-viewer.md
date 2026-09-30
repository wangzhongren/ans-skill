# 旧 JSON 架构 HTML：仅按需使用

这是保留给既有 JSON 数据的旧工具说明，不是当前默认流程。只有客户明确要求查看或重建旧页面时才使用下面的格式和命令；不为新任务创建 JSON，不要求各角色继续维护它。当前入口是项目管理角色的 docs/architecture.md，以及各角色的 feature-map.md → docs/feature/，见[功能文档](feature-point.md)。现有渲染器只读 JSON，不能读取 Markdown；如以后需要 HTML 展示，应以 Markdown 为输入，不能恢复双份维护。

## 谁维护什么

1. 只处理本次明确要求查看或修改的旧 角色卡/<角色>/architecture.json，英文项目跟随已有角色目录名称。不为新角色补建 JSON，也不把维护旧 JSON 加入日常交付。
2. 项目角色运行技能中的绘图工具，统一生成项目 HTML，任务结束后打开并交付链接。
3. 治理角色将各角色的 JSON 路径、项目角色的生成输出路径写进已接受的边界。工具本身不能授权写文件。
4. 不新增画图师。程序只检查、汇总和排版，不修改输入 JSON、源码、边界或设计结论。

架构 JSON 是当前结构的维护源。功能文档说明怎样用、完整流程和分支；日期文档解释某次设计或增改修的原因。接口字段和数据含义以正式契约、Model 和对应功能文档为准。**不再要求另行维护 content.json、context.sqlite3 或一份重复的项目理解索引。**既有 SQLite 查看和 Dashboard 工具保留为可选旧工具，不是角色交付门槛。

## JSON 格式

角色 ID 等于角色文件夹名。节点、功能和数据流 ID 使用“角色ID:稳定名称”，改显示名称时保留 ID。一个抽象只由所属角色定义，其他角色按 ID 引用。`common/shared/` 中的抽象归项目管理角色；各角色的私有 common 代码归自己。测试角色记录实际测试支撑结构，不编造业务功能。

~~~json
{
  "schemaVersion": 1,
  "roleId": "工单",
  "revision": 1,
  "updatedAt": "2026-09-29",
  "summary": "负责工单的草稿、提交和状态处理。",
  "abstractions": [
    {
      "id": "工单:DraftService",
      "name": "草稿处理约定",
      "description": "检查草稿内容，并使用存取约定保存它。",
      "kind": "contract",
      "layer": "service",
      "public": true,
      "status": "current",
      "sourceRefs": ["src/services/abstract/draft.ts"]
    }
  ],
  "relations": [
    {"from": "工单:DraftService", "to": "存储:DraftStore", "kind": "uses"}
  ],
  "features": [
    {
      "id": "工单:save-draft",
      "name": "保存草稿",
      "purpose": "保存当前填写内容，之后可以继续编辑。",
      "abstractionIds": ["工单:DraftService", "存储:DraftStore"],
      "sourceRefs": ["角色卡/工单/features/save-draft.md"]
    }
  ],
  "dataFlows": [
    {
      "id": "工单:send-draft",
      "featureId": "工单:save-draft",
      "from": "工单:DraftService",
      "to": "存储:DraftStore",
      "data": "检查后的草稿内容",
      "condition": "内容符合保存要求",
      "kind": "send",
      "sourceRefs": ["src/services/impl/draft.ts"]
    }
  ]
}
~~~

示例仅解释格式，不能复制成真实项目事实；对应的存储角色还需定义自己的 存储:DraftStore 节点，并记录由它发出的保存结果。

| 字段 | 写什么 |
| --- | --- |
| revision、updatedAt | 本角色实际更新后的正整数版本和 YYYY-MM-DD 日期 |
| abstractions | 稳定概念、模块、接口约定或 Model；不列每个文件、私有函数和临时变量 |
| kind | concept、contract、model 或 module |
| layer | interface、pipeline、service、provider、model；common 表示工具与基础框架的配套代码，不增加第六层 |
| public | 是否提供给其他角色使用；共享 Model 仍按已有全局共享规则处理 |
| status | current 表示当前记录，不等于测试通过；planned 表示计划中；needs-review 表示待核实 |
| relations | contains 组成、manages 管理、composes 组合、uses 使用、uses-model 引用数据、implements 实现约定 |
| features | 功能用途、相关抽象 ID 和功能文档依据；全局功能 ID 由主要负责角色定义一次 |
| dataFlows | 功能 ID、发出与接收的抽象、传递数据、实际条件；send 是传递，return 是结果返回 |
| sourceRefs | 项目内的依据路径；不复制源代码和整份文档 |

使用方记录自己依赖谁。数据传递由发出数据的角色记录，接收方记录自己的后续处理和返回。参与角色沿用同一功能 ID。对外关系引用公开约定，不能以绘图为理由允许越层调用。

组成关系形成思维导图主干，使用关系显示为引用。数据定义引用与能力调用分开标明。缺角色 JSON、引用或数据流时页面显示待补，不由工具推断。非法 JSON、重复 ID 或越权定义其他角色的节点会阻止生成，保留原页面。

项目管理角色有共享组件时，在自己的 JSON 中记录，使用 common 标签。测试角色只记录适合当前格式表达的真实结构；没有需要展示的模块时可以保留空列表并说明，不把测试框架或公共组件硬标成业务层，不为填图编造业务能力。

## 生成和打开

在技能目录运行，或使用脚本的绝对路径：

~~~sh
python3 scripts/render_architecture.py \
  --root /absolute/path/to/project \
  --out doc/architecture/index.html
~~~

输出是项目内已经批准的位置。跟随项目现有文档根目录：已有 doc/ 就复用它，使用 docs/ 的项目就改成 docs/architecture/index.html；不再新建第二套文档根。有自定义角色目录时加 --roles <项目相对目录>。

工具打印生成 HTML 的绝对路径和数量。通过可用的本地文件或浏览器工具打开它，并在聊天中附链接。它不需要联网、后端或安装前端依赖。

角色配合图只将已记录的抽象引用汇总为角色连线；数据流按功能显示传递关系；内部图可折叠、展开和查看抽象说明。生成时间、角色版本与缺失信息都能查看。HTML 是当次快照：修改 JSON 后重跑工具，浏览器刷新本身不会读取新的磁盘 JSON。

## 什么时候更新

公开约定、抽象组成、模块职责、跨角色依赖、功能归属或数据传递改变时，角色核对代码和契约后更新自己的 JSON，并增加版本。纯排版或不影响这些事实的私有实现调整不强制重画。

任务收尾时，项目角色汇总变更，运行工具并打开最新页面。绘图范围已授权时不反复索要重画许可。新的业务改动和选装仍先交文档确认。既有角色缺 JSON 权限时交给治理流程，不自行扩权。

旧 Dashboard、云端同步和项目理解查询按用户明确需要使用，不默认启动或要求填充它们。
