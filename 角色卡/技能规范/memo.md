# 技能规范角色备忘录

## 2026-11-03 — P1 四类工作与修复窄快速通道实施

- 状态：按客户选定的 P1 首版实施四类工作（新建/修复/变更/重构）、五条指定转换和修复窄快速通道；技能规范写集 10 个文件已修改，未 commit/push。P1 方案与复核记录本轮未改。
- 依据：客户选择与实施原话见[沟通记录](../../docs/communication/2026-11-03_communication_four-work-types.md)；统筹计划见[P1 直接实施](../../docs/scheduling/2026-11-03_p1-direct-implementation.md)；实施基线为[P1 方案](../策划/docs/design/2026-11-03_design_four-work-types.md)（912 行，SHA-256 `1ab5e0593f0c92e5389deefdcea7c2c324cd3de44fec387c0e945a2634f3daab`）。
- 单一来源：O5 未实施，不创建 `references/work-types.md`；本轮四类工作、五条转换和修复窄通道的详细规则只在 [references/workflow.md](../../references/workflow.md) 定义，其余入口/参考只做摘要并链接。
- 本轮改动：`SKILL.md`、`SKILL.zh.md`、`README.md`、`references/workflow.md`、`references/action-policy.md`、`references/proposal-review.md`、`references/documentation.md`、`site/index.html`、`site/en/index.html`、本 memo。
- 保留缺口：D1 非窄修复没有可执行路径；D2 修复基线“已接受”未定义；两者按 P1 原样保留，不自行补规则。未创建 `references/work-types.md`、未改四份 `documentation-*` 类型指南、未写 `docs/change/`/`docs/fix/` 新路径、未建 B1/B2、未改任何边界或角色定义。

### D3 最小措辞调整（只处理直接冲突句）

| 文件 | 原句 | 改后句 | 理由/P1 条款 |
| --- | --- | --- | --- |
| `SKILL.md` | “passes it through three separate customer gates; never merge or skip them:” | “passes it through three separate customer gates; never merge or skip them for new work, changes and refactors:”；并在闸门列表后新增“A fix inside already-confirmed behavior is the one narrow fast path…” | 修复窄通道不产生新的闸门 1/2 对象；P1 4.2.4、8.2、C23 |
| `SKILL.md` | “Until the customer agrees, People Operations writes no role cards and the Scheduler dispatches no development.” | “For new work, changes and refactors, until the customer agrees, People Operations writes no role cards and the Scheduler dispatches no development.” | 同上 |
| `SKILL.md` | “Until the customer confirms it, no team planning or recruiting starts.”（Gate 1 描述段末） | “For new work, changes and refactors, until the customer confirms it, no team planning or recruiting starts.” | 该句只描述新建/变更/重构的闸门 1；修复窄通道由闸门 0 同轮记录和既有指派覆盖，不产生新的闸门 1/2 对象；P1 4.2.4、8.2、C23 |
| `SKILL.md` | “This document-level confirmation is separate from the three workflow gates and never substitutes for the role-assignment confirmation (gate 2) before dispatch.” | “This document-level confirmation is separate from the three workflow gates and, in the normal flow, never substitutes for the role-assignment confirmation (gate 2) before dispatch; under the fix narrow fast path it confirms the fix record while the owner, scope and write set stay unchanged, so no new gate 2 object arises.” | P1 4.2.5 |
| `SKILL.md` Task Routing | 段落只描述“确认意图→策划方案→闸门 1→团队计划→闸门 2→派发”正常流程 | 段末新增“A fix inside confirmed behavior follows the narrow fix path instead of the Planning proposal and role-assignment rounds.” | P1 4.2.3、4.2.4 |
| `SKILL.zh.md` | “客户确认按三道独立闸门推进：” | “新建、变更、重构按三道独立闸门推进（已确认行为内的窄修复是唯一有界例外，见下文“四类工作与修复窄快速通道”）：” | P1 4.2.4、8.2 |
| `SKILL.zh.md` | “客户未同意，人事不写卡、调度不派发。”（两处） | “新建、变更、重构中客户未同意，人事不写卡、调度不派发。” | 同上 |
| `SKILL.zh.md` | “这份文档级确认不等于三道流程闸门，尤其不能代替角色指派确认（闸门 2）；派发前仍按闸门顺序核对。” | “这份文档级确认不等于三道流程闸门，正常流程中不能代替角色指派确认（闸门 2）；修复窄快速通道下所有者、范围和写集不变，客户修复指令覆盖修复记录，没有新的闸门 2 对象，派发前按 F1–F9 核实。” | P1 4.2.5 |
| `references/workflow.md` | “This document-level confirmation is separate from the three workflow gates and never substitutes for the role-assignment confirmation (gate 2).” | “This document-level confirmation is separate from the three workflow gates and, in the normal flow, never substitutes for the role-assignment confirmation (gate 2); under the fix narrow fast path, the customer's fix instruction covers the fix record while owner, scope and write set stay unchanged, so no new gate 2 object arises.” | P1 4.2.5 |
| `references/workflow.md` | 新需求段“including the assignment when the roster stays unchanged… (gate 2)” | 段末新增“This is the normal new-work path; the fix narrow fast path is the only bounded exception because it creates no new gate 1 or gate 2 object.” | P1 4.2.4、C23 |
| `references/action-policy.md` | “Customer confirmation happens only at the three explicit gates … plus any task-level implementation instruction” | 保留原句，后加“Under the narrow fix fast path, the defect record plus the explicit fix instruction satisfy gate 0 in the same round, and no new gate 1 or gate 2 object arises; new work, changes and refactors keep all three gates.”；同意清单加入“tool success” | P1 3.3、4.2.2 |
| `references/proposal-review.md` | “the customer's role-assignment confirmation (gate 2), accepted role boundaries and actual task scope” | “the customer's role-assignment confirmation (gate 2) where a new assignment object exists, accepted role boundaries and actual task scope”；并加“Under the narrow fix fast path no new assignment object exists…” | P1 4.2.4、8.2 |
| `references/documentation.md` | “这份文档级确认不等于三道流程闸门，也不能代替角色指派确认（闸门 2）。” | “这份文档级确认不等于三道流程闸门，正常流程中也不能代替角色指派确认（闸门 2）；修复窄快速通道下所有者、范围和写集不变，客户修复指令覆盖修复记录，没有新的闸门 2 对象（见工作流规则）。” | P1 4.2.5 |
| `README.md` | “客户确认按三道独立闸门推进：” | “新建、变更、重构按三道独立闸门推进（已确认行为内的窄修复走快速通道，见四类工作与修复窄通道）：” | P1 4.2.4、O12 |
| `site/index.html` | 标题“三道客户确认闸门，再安排实际工作。”；正文“客户未同意，人事不写卡、不派发开发” | 标题改为“三道客户确认闸门，加上一条窄修复通道。”；正文改为“新建、变更、重构中客户未同意…”；新增窄修复与五条转换说明段 | P1 4.2、4.5、O12 |
| `site/en/index.html` | 标题“Three customer gates, then the work.”；正文“Without the customer's agreement there is no recruiting…” | 标题改为“Three customer gates, plus one narrow fix path.”；正文改为“For new work, changes and refactors, without the customer's agreement…”；新增窄修复与五条转换说明段 | 同上 |

### 验证与续接

- 验证：`git diff --check` 退出码 0；本角色改动路径与统筹计划第 3.1/3.2 节技能规范写集一致；工作区同时存在人事并行批次（A1–A6、A14–A19、A21）的改动，不属于本角色写集。修改文件做了相对链接和目标锚点核对；检索确认未并入 P2/P3 专属内容（“普通修复”“基线优先级”“21 处”“判断权归策划”“闭环不变量”“转换矩阵”均未出现）。
- 未做：未 commit/push；未伪造闸门 1/2、独立验收通过或实施授权；本角色未修改 P1、复核记录、角色定义类参考、任何角色卡/边界、代码或测试。
- 续接：后续若客户确认 O5，可把四类工作详细规则迁入 `references/work-types.md`，本文件的摘要改为链接；若补齐四份 `documentation-*` 指南边界，再按确认方案把类型指南补上。

## 2026-10-10 — 已完成：项目法案与角色 memo 指南

- 状态：规范文档与五种情境推演已验证；最终报告确认 35 份 Markdown、238 个本地链接与锚点、5 份元数据及围栏检查通过。本功能文档新增的 YAML 元数据经本轮单独核验。GUI、线程与应用性能行为未测。见[最终独立测试报告](../测试/docs/change/2026-10-10_change_project-rules-memo-validation.md)。
- 依据：已确认方案 `doc/design/2026-10-10_design_project-plan-role-memo.md` 与本轮管理评审 `角色卡/项目管理/docs/design/2026-10-10_design_project-rules-memo-review.md`。
- 关键约定：唯一项目法案由项目管理角色在自身角色目录的 `docs/project-rules.md` 维护，其他角色引用同一实际路径；每条规则使用稳定编号或名称，理由按需补充。角色 memo 由各角色自己维护，仅记录少量有日期、有来源的工作线索。初始化不以法案先存在为条件。GUI `THREAD-01` 只是写法示例；单纯加 `async` 不会把重计算移到后台，且只有项目确认相应 GUI 模型和约束后才适用。
- 继续：本轮没有待处理的技能规范文档项。最终复核确认首轮发现的管理元数据及历史状态问题已关闭；它们作为报告中的修复历史保留。后续修改遵守本角色 `boundary.md`。具体规则见 [项目法案指南](../../references/project-rules.md) 和 [角色 memo 指南](../../references/role-memo.md)。

## 2026-10-10 — README 更新

- 状态：README 已补充独立的项目法案与 memo 说明、本仓库本轮实际角色分工及现有示例树中的 `memo.md`。法案由项目管理维护、全角色共读；每条规则说明范围、要求、正确做法和检查，只有项目确认后适用。
- 依据：本轮用户请求；实际角色与职责见 [项目管理架构说明](../项目管理/docs/architecture.md)，独立验证结果见[测试报告](../测试/docs/change/2026-10-10_change_project-rules-memo-validation.md)。
- 检查：README 的 25 个本地链接目标存在，`git diff --check` 通过；没有运行程序测试。本条不记录 GitHub/GitLab 发布或推送结果。
