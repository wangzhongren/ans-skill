# 2026-10-22 五内置管理角色候选返工计划

- 计划任务 ID：`five-role-rework-2026-10-22`（调度计划标识，不是 `task_ops` 任务 ID；本轮不创建任务 ID、不写全局调度状态或验收凭证）
- 计划角色：统筹调度（`scheduler`，固定上下文）
- 计划日期：2026-10-22
- 依据：独立验收对“五个内置管理角色”候选第一轮结论 **返工**（2026-10-22，经协调方转达），以及本仓库 `角色卡/统筹调度/boundary.md` Section 1 的 `docs/scheduling/` 条件目录授权
- 性质：团队计划与返工派发依据；不修改任何被点名的角色卡、边界、角色定义或共享参考，只由各所有者在其 Section 1 内执行

## 1. 验收结论版本与候选范围

### 1.1 验收结论版本

- 第一轮结论：**返工**。返工项版本记为 `B1–B5、R1–R3、R5、R6`；本计划追加 `A1`（验收报告路径缺口）。
- 独立验收本轮回传时**没有正式验收报告文件路径**：`角色卡/验收/boundary.md` 的 Section 1 只列既有三组标准/结果，未包含本轮报告。该缺口不归验收自行扩权，作为 A1 先由招募补精确路径，复核完成后由验收写盘。
- 复核基线：与第一轮相同的五内置管理角色模型定义和同一版策划方案；不新增标准、不扩大范围、不把返工项解释成新需求。

### 1.2 候选范围

- 仓库根：`/Users/wangzhongren/code/vibeingcode/组内培训/ans-skill`
- 分支：`feat/five-role-model`；已提交基线：`f76127d`
- 工作区：`git diff --name-only HEAD` 共 54 个未提交修改文件；`git status --porcelain` 无未跟踪文件。范围包括入口文档（`SKILL.md`、`SKILL.zh.md`、`README.md`）、`references/` 共享与角色定义参考、`site/` 两语言页面、`角色卡/governance-boundary.md`/`.yaml`，以及策划、技能规范、统筹调度、项目管理、验收五个角色目录内的卡片、边界、YAML 和 changelog。
- 排除：`scripts/`、`dashboard/`、`.e2e-todo/`、已安装技能副本、public 镜像；不推送、不安装、不发布。
- 复核方式：全部修订完成后冻结工作区候选（记录 `git status --porcelain` 清单及关键文件哈希），由独立验收按同一版策划方案复核本计划全部返工项；本轮不 commit，复核对象是工作区整体候选。

## 2. 角色增减与权限结论

- **无角色增减**：本次不新增、删除、合并、拆分任何角色；不改变任何 `roleId`、组别或角色默认写权范围。项目管理角色仍为“按统筹团队计划建立”的 worker 角色，不因返工变成默认角色。
- **只修文档和治理记录**：不改业务代码、测试、构建、安装或发布；不修改 `scripts/`、`dashboard/`、`.e2e-todo/`。
- **只允许三类精确单文件路径新增**（无目录级扩权）：
  1. B4：技能规范的实际变更记录路径 `角色卡/技能规范/docs/change/2026-10-22_change_five-role-model.md`；
  2. R1：`references/project-context.md`、`references/role-architecture-viewer.md`、`references/dashboard.md` 的明确归属（推荐归技能规范）或明确废弃记录；
  3. A1：`角色卡/验收/docs/acceptance/2026-10-22_five-role-model-result.md`。
- **治理原则不变**：角色卡、边界、同名 YAML、changelog 和角色定义类参考只由 ANS 团队组建（招募）维护；任何角色不写自己的角色定义；项目管理、策划、技能规范只写各自 Section 1 内的工作文档；调度不修改被点名文档，只写本计划。

## 3. 分派表

| 项 | 所有者 | 主要写入范围（以各角色 Section 1 为准） | 交接输入 | 复核条件摘要 |
| --- | --- | --- | --- | --- |
| B1 | 项目管理 | `角色卡/项目管理/docs/architecture.md`、`角色卡/项目管理/docs/project-rules.md` | 本计划；招募在本轮确认的现行角色定义（`references/planning-role.md`、`project-role.md`、`scheduler.md`、`team-formation.md`、`acceptance-role.md`） | 不再默认拥有技术架构；纯角色职责表述与招募定义一致或改为链接；实现层/工程内容更新 |
| B2（PM 部分） | 项目管理 | `角色卡/项目管理/feature-map.md` | B1 完成后的 architecture.md、project-rules.md | 删除“负责技术架构”；导航反映实现设计与技术契约职责 |
| B2（策划部分） | 策划 | `角色卡/策划/feature-map.md`、`角色卡/策划/memo.md` | 本计划；现行角色定义参考 | 不再把技术架构/评审路由给项目管理；不重写历史方案 |
| B3 | 技能规范 | `角色卡/技能规范/docs/feature/role-authority-split.md` | 本计划；现行五角色流程定义 | 正文、表格、流程图不再写“项目管理做技术架构”默认路由 |
| B4（治理记录） | 招募 | `角色卡/技能规范/boundary.md`、`boundary.yaml`、`changelog.md`、`references/governance-changelog.md` | 本计划；实际 `git diff HEAD` | 记录与实际 diff 一致；`references/architecture.md` 正文修改如实记录；MD/YAML 同步 |
| B4（实际变更记录） | 技能规范 | 新增 `角色卡/技能规范/docs/change/2026-10-22_change_five-role-model.md`（先由招募加路径） | 招募补路径后的授权；实际 diff | 记录本候选内技能规范所属共享文档的真实正文修改与依据 |
| B5 | 招募 | `references/built-in-boundary.md`、`references/built-in-boundary.yaml`、`references/governance-changelog.md` | 验收项 B5；现行治理边界 | Section 1 收窄到角色治理资料或写明严格适用条件；MD/YAML 同步 |
| R1（归属授权） | 招募 | `角色卡/技能规范/boundary.md`、`boundary.yaml`、`changelog.md`、`references/governance-changelog.md` | 验收项 R1 | 三个旧参考有明确 owner 或明确废弃记录 |
| R1（内容更新） | 技能规范 | `references/project-context.md`、`references/role-architecture-viewer.md`、`references/dashboard.md`（归属确定后） | 招募的归属记录；现行模型 | 默认阅读路径不再默认项目管理为架构所有者 |
| R2 | 招募 | `角色卡/技能规范/boundary.md`、`boundary.yaml`、`changelog.md` | 验收项 R2；两个参考文件已存在的事实 | 去掉过期的“待新增/接入后方可创建”标记并补依据 |
| R3 | 技能规范 | `README.md`、`references/documentation.md` | 本计划；顶层历史 `doc/` 与新默认 `docs/` 的实际状态 | 明确“历史 `doc/` 保留、新默认 `docs/`、不回溯迁移” |
| R5（共享文档） | 技能规范 | `SKILL.md`、`SKILL.zh.md`、`README.md`、`references/workflow.md`、`references/documentation.md`、`references/action-policy.md` 等其 Section 1 内出现端到端时序的共享文档 | 本计划第 4.10 节统一文案 | 时序统一为“策划完成 → 统筹判断团队 → 必要时招募 → 客户确认/授权 → 派发” |
| R5（角色定义） | 招募 | `references/scheduler.md`、`references/communication-role.md`、`references/planning-role.md`、`references/team-formation.md`、`references/acceptance-role.md`、`references/project-role.md`、`references/test-role.md`、`references/built-in-boundary.md`/`.yaml`、`角色卡/统筹调度/role-card.md`、`references/governance-changelog.md` | 本计划第 4.10 节统一文案 | 去除“先收客户实施授权再判断团队”等不一致；不移除同版授权复用 |
| R6 | 招募 | `references/acceptance-role.md`、`references/test-role.md`、`references/governance-changelog.md` | 验收项 R6；现行 planning/project/scheduler 定义 | 明确“产品/架构设计交策划；实现设计交已建立的项目管理角色” |
| A1 | 招募（补路径）；验收（复核后写报告） | 招募：`角色卡/验收/boundary.md`、`boundary.yaml`、`changelog.md`、`references/governance-changelog.md`；验收：仅新增报告文件 | 协调方补充要求；本计划 | 报告路径列入 Section 1 且 YAML 同步后，验收才可写盘 |

## 4. 逐项写入范围与验收复核条件

### 4.1 B1 — 项目管理现行工作文档仍描述旧角色模型

- 所有者：项目管理。
- 写入范围：`角色卡/项目管理/docs/architecture.md`、`角色卡/项目管理/docs/project-rules.md`（均在其 Section 1 内）。
- 必须修正的事实：
  - `docs/architecture.md` 不再把“唯一内置岗位为 ANS 团队组建”“项目管理负责技术架构”作为当前模型；架构设计归策划，PM 仅在统筹团队计划建立后承接已确认架构，负责实现设计、技术评审、技术契约、工程法案和获准的 shared。
  - `docs/project-rules.md` 的 ROLE-01 等职责条目同步现行模型；文档头部的维护者/日期/版本按实际更新。
- 边界约束：**纯角色职责定义内容不由项目管理自行改写**。项目管理对这类段落只做两种处理之一：按招募在本轮确认的现行角色定义文案替换，或改为链接到招募维护的角色定义参考（如 `references/planning-role.md`、`references/project-role.md`、`references/scheduler.md`、`references/team-formation.md`、`references/acceptance-role.md`）。项目管理不得自行新增、删除或扩大任何角色职责/权限。
- 交接输入：招募在 B4/B5/R2/R6/R5 同批确认的现行角色定义；本计划第 4.10 节统一流程文案。
- 复核条件：全文检索无“项目管理（默认）负责技术架构/整体架构”“唯一内置岗位”等旧模型断言；职责表述与招募参考一致或明确链接；实现层架构、工程条目、链接和日期真实；未新增角色、权限或程序路径。

### 4.2 B2（PM 部分）— 项目管理功能导航仍写“负责技术架构”

- 所有者：项目管理。
- 写入范围：`角色卡/项目管理/feature-map.md`。
- 要求：删除“负责技术架构”的所有权表述；改为承接策划已确认架构，负责实现设计、技术评审、技术契约、工程法案和获准的 shared；导航链接指向更新后的 `docs/architecture.md`、`docs/project-rules.md`，并可链接策划的 `docs/planning/` 方案/架构。
- 复核条件：导航不再声称项目管理拥有技术架构；与 B1 更新后的正文一致；历史方案链接保留且不冒充当前职责。

### 4.3 B2（策划部分）— 策划导航与 memo 仍把技术架构/评审路由给项目管理

- 所有者：策划。
- 写入范围：`角色卡/策划/feature-map.md`、`角色卡/策划/memo.md`。
- 要求：
  - 技术架构/架构设计不再路由给项目管理；明确“策划负责产品方案、架构设计与共有业务契约；如统筹判断实现确实需要技术架构工作角色并按团队计划建立项目管理角色，才由该角色在已确认架构下做实现设计和技术评审”。
  - 把项目管理 `docs/architecture.md` 从“现行职责与后续方案路由”改为“如按计划建立时的实现层架构说明”；策划自己的方案/架构放在 `docs/planning/`。
  - 保留 2026-10-19 历史方案归属，不重写、不复制成策划方案。
- 复核条件：两文件不再默认把技术架构/评审交给项目管理；与 `references/planning-role.md`、`project-role.md` 一致；不虚构已建立的 PM 角色或路径。

### 4.4 B3 — 技能规范功能说明仍描述旧流程

- 所有者：技能规范。
- 写入范围：`角色卡/技能规范/docs/feature/role-authority-split.md`。
- 要求：正文、交接表和 Mermaid 流程图更新为现行流程：沟通接单 → 策划（产品方案、架构设计、共有契约、完成标准）→ 统筹判断团队 → 必要时招募按团队计划建卡/调边界 → 客户确认/实施授权 → 统筹派发 → 实施与测试 → 独立验收。项目管理只在按计划建立时承接已确认架构做实现设计/技术评审，不是默认架构所有者。
- 保留历史事件和旧日期记录，不篡改；需要时追加 2026-10-22 事件说明。当前状态按实际保持（复核通过前不得写成已验收通过）。
- 复核条件：文档中不再存在“项目管理做技术架构”的默认路由；流程图与第 4.10 节统一文案一致；历史段落保留并与当前段落区分；链接有效。

### 4.5 B4（治理记录）— 技能规范治理记录与实际 diff 不一致

- 所有者：招募。
- 写入范围：`角色卡/技能规范/boundary.md`、`角色卡/技能规范/boundary.yaml`、`角色卡/技能规范/changelog.md`、`references/governance-changelog.md`。
- 必须修正：
  - 现行记录称 `references/architecture.md`“只调整边界归属，不修改正文”，但本候选实际修改了正文（shared 归属、策划架构职责等）。如实更正为“正文已在本候选修改”，并记录修改范围/依据。
  - 技能规范所属共享文档（`SKILL.md`、`SKILL.zh.md`、`README.md`、`references/` 相关文件、`site/` 页面等）在本候选中的正文修改，需要有实际的变更记录或依据入口；招募在 changelog 中链接技能规范按 B4（实际变更记录）写出的记录，而不是声称“未修改”。
  - `boundary.md` 与 `boundary.yaml` 保持同步；changelog 按时间追加，不重写历史条目。
- 复核条件：三条记录与 `git diff HEAD` 逐项一致；`references/architecture.md` 的行级差异有对应说明；boundary MD/YAML 同步；无“未修改正文”与事实相反的说法。

### 4.6 B4（实际变更记录）— 技能规范补充 actual change 记录/依据

- 前置：招募先在 `角色卡/技能规范/boundary.md` 和 `.yaml` 增加单文件 `角色卡/技能规范/docs/change/2026-10-22_change_five-role-model.md` 并记录该治理变更。
- 所有者：技能规范。
- 写入范围：仅上述新增文件。
- 要求：列出本候选内技能规范所属共享文档的实际正文修改（以 `git diff --name-only HEAD` 对照技能规范 Section 1），逐项写变化摘要、依据（五内置管理角色模型、用户治理原则纠正、本次返工项）、哪些是边界归属变化、哪些是正文修改；不得把未发生的改动写成已发生，不得补造历史授权。
- 复核条件：记录覆盖实际修改文件；与招募更正后的 boundary/changelog 相互链接且不矛盾；不把 `references/communication-role.md` 等已移交招募的角色定义参考算作技能规范变更；记录本身不冒充验收通过。

### 4.7 B5 — 内置治理边界 Section 1 仍偏宽

- 所有者：招募。
- 写入范围：`references/built-in-boundary.md`、`references/built-in-boundary.yaml`、`references/governance-changelog.md`。
- 要求：收窄 Section 1 或写明严格适用条件，使其不再宽于“招募只写 `角色卡/` 治理资料”：
  - `references/` 目录级条目限定为角色定义类参考（精确职责范围），不覆盖共享格式、流程、宣传页等由其他 owner 维护的文件；
  - `docs/` 脚手架、`SKILL.md`/`SKILL.zh.md`、装配角色入口等宽条目，要么收窄为角色治理资料，要么写清“只在已授权的团队计划要求 bootstrap 该 worker 角色时适用，不适用于例行治理或功能开发”；
  - 不授权业务代码、执行配置、任务状态、活动调度记录或他人工作文档；项目本地治理边界覆盖仍优先。
  - Markdown 与 YAML 同步；治理变更记入 `references/governance-changelog.md`。
- 复核条件：Section 1 每条都能对应到角色治理资料或有明确触发条件；无目录级 `references/` 扩权；MD/YAML 一致；保留按计划 bootstrap worker 角色的能力，不因收窄而删除必要定义维护职责。

### 4.8 R1 — 三个旧共享参考不在任何边界内且仍有旧说法

- 涉及文件：`references/project-context.md`、`references/role-architecture-viewer.md`、`references/dashboard.md`。
- 第一步（招募）：在 `角色卡/技能规范/boundary.md` 和 `.yaml` 增加上述三个精确单文件路径（推荐归技能规范，因为它们是共享旧工具/格式说明，不属于角色定义），并在 `角色卡/技能规范/changelog.md`、`references/governance-changelog.md` 记录归属依据。若招募判定应废弃，则明确记录废弃决定，并仍给技能规范精确路径以标注“旧工具、仅按客户明确要求使用”。
- 第二步（技能规范）：更新三个文件的旧说法——默认阅读路径为策划 `docs/planning/` 的产品方案与架构设计；只有统筹团队计划建立项目管理角色时，才从该角色的 `docs/architecture.md` 看实现层结构；各角色 `feature-map.md` → `docs/feature/` 仍是功能阅读入口。`dashboard.md` 的英文默认路径表述同样修正。
- 复核条件：三个文件均进入某个已接受 Section 1 或有明确废弃记录；正文不再默认“项目管理的 docs/architecture.md 是当前入口/默认阅读路径”；旧工具仅按客户明确要求使用的限制保留；无角色因此获得业务代码或任务状态写权。

### 4.9 R2 — 技能规范边界中两个“待新增”标记过期

- 所有者：招募。
- 写入范围：`角色卡/技能规范/boundary.md`、`boundary.yaml`、`changelog.md`。
- 要求：`references/project-rules.md`、`references/role-memo.md` 已实际存在，去掉“待新增单文件/接入后方可创建”的过期标记，改为正常单文件条目并写清用途；核对文件实际内容与用途一致。若两文件此前的创建依据没有记录，如实补记“实际存在、此前授权依据待核实/已由本次记录确认”，不得补造日期或授权。
- 复核条件：boundary 中不再有这两个文件的“待新增”标记；MD/YAML 一致；changelog 有对应更正条目；条目与实际文件相符。

### 4.10 R5 — 客户授权与团队判断先后表述不统一

- 统一文案（所有文件一致）：**“策划完成（产品方案、架构设计、共有契约与完成标准）→ 统筹判断团队（不变/新招/拆分）→ 必要时招募按团队计划建卡与边界 → 客户确认/实施授权（经沟通）→ 统筹派发。”**
- 技能规范部分：
  - 写入范围：其 Section 1 内出现端到端时序的共享文档，至少核对 `SKILL.md`、`SKILL.zh.md`、`README.md`、`references/workflow.md`、`references/documentation.md`、`references/action-policy.md`。
  - 要求：按统一文案修正；保留“已有同版同范围有效授权直接复用、不重复询问”的规则；不把“团队判断/招募”写成需要客户逐项批准。
- 招募部分：
  - 写入范围：`references/scheduler.md`、`references/communication-role.md`、`references/planning-role.md`、`references/team-formation.md`、`references/acceptance-role.md`、`references/project-role.md`、`references/test-role.md`、`references/built-in-boundary.md`/`.yaml`、`角色卡/统筹调度/role-card.md`、`references/governance-changelog.md`。
  - 已知不一致点必须修正：`references/scheduler.md` 开篇“沟通把……客户实施授权交给调度后，调度先……判断团队”把授权放在判断团队之前；`角色卡/统筹调度/role-card.md` 开篇“接收客户已确认的……实施授权……先按方案和架构判断团队”同理。统一为“判断团队/必要时招募在前，客户确认/授权在派发前”。
- 复核条件：全库检索“判断团队”“团队判断”“实施授权”“客户确认”的邻近表述，未发现“先收客户实施授权再判断团队”“招募前先授权”或“未授权即派发”；通信、调度、策划、招募、验收五份角色定义和入口文档使用同一顺序；同版授权复用规则保留；招募变更记入 `references/governance-changelog.md`，技能规范变更并入 B4 实际变更记录。

### 4.11 R6 — 验收与测试角色定义中“架构问题交项目管理”需区分

- 所有者：招募。
- 写入范围：`references/acceptance-role.md`、`references/test-role.md`、`references/governance-changelog.md`。
- 要求：明确区分“**产品方案/架构设计问题交策划**；**实现设计/技术契约问题交已按团队计划建立的项目管理角色；未建立时不虚构该角色，由统筹安排**”。修正现有括号式表述（“如已建立技术架构工作角色，交该角色评估”）可能被读成“架构问题默认交项目管理”的问题。
- 复核条件：两文件均包含上述区分；不再出现默认把一般“架构问题/架构缺口”交给项目管理的表述；与 `planning-role.md`、`project-role.md`、`scheduler.md` 一致；治理变更记录完整。

### 4.12 A1 — 本次验收没有可写报告路径

- 所有者：招募（补路径）；验收（复核完成后写报告）。
- 招募写入范围：`角色卡/验收/boundary.md`、`角色卡/验收/boundary.yaml`、`角色卡/验收/changelog.md`、`references/governance-changelog.md`。
- 要求：在验收 Section 1 增加精确单文件路径 `角色卡/验收/docs/acceptance/2026-10-22_five-role-model-result.md`，用途写明“五内置管理角色候选返工复核的独立验收结果”；YAML 同步；changelog 记录治理变更。招募不写验收报告。
- 验收写入范围：仅上述报告文件，且必须在全部返工修订完成、候选冻结、独立复核完成后写盘。
- 报告至少包含：计划任务 ID `five-role-rework-2026-10-22`；第一轮返工结论版本与本轮复核基线；候选范围（分支、基线提交、工作区文件清单/摘要）；B1–B5、R1–R3、R5、R6、A1 逐项结论；证据入口；未解决问题；结论（通过/返工/证据不足）及理由。第一轮验收无正式报告的事实如实记录，不伪造前一轮文件。
- 复核条件：路径先进入 Section 1 与 YAML 后验收才写盘；报告只由验收写；报告结论匹配当前冻结候选；调度不代写、不改结论。

## 5. 执行顺序与依赖

1. **招募先做治理侧（第一批）**：B4（治理记录更正）、B5、R2、R6、R5（角色定义部分）、R1（归属/废弃决定与路径）；同时为技能规范补 B4 实际变更记录路径，为验收补 A1 报告路径，为 R1 补三个参考的归属路径。全部记入 `references/governance-changelog.md` 与对应角色 changelog。
2. **技能规范（第二批）**：B4（实际变更记录）、B3、R3、R5（共享文档部分）；R1 内容更新在招募完成归属后进行。
3. **项目管理（第三批）**：B1 与 B2（PM 部分）合并为同一写作轮次；输入为招募确认的现行角色定义和技能规范/招募已修正的时序文案。
4. **策划（第三批，可与 PM 并行）**：B2（策划部分）。
5. **候选冻结**：全部完成后记录 `git status --porcelain` 与关键文件摘要；不 commit。
6. **独立验收复核**：按同一版策划方案和本计划全部返工项复核，写 A1 报告，给通过/返工/证据不足。
7. **调度放行**：只消费匹配当前候选的有效通过结论；返工交原所有者；证据不足安排补证。调度不改结论。

写入隔离：招募与技能规范不得同时改同一文件；B1 中 PM 文档的角色定义段落由招募提供权威文案、PM 作为文档所有者落地或改为链接（招募不取得 PM 工作文档写权）；验收报告只能由验收写，招募与调度不代写。

## 6. 本轮明确不做

- 不新增/删除角色，不改变角色职责边界以外的默认写权，不新建程序路径。
- 不修改 `scripts/`、`dashboard/`、`.e2e-todo/`、已安装技能副本或 public 镜像。
- 不 commit、不 push、不 install、不发布、不启用真实项目任务记录。
- 不迁移顶层历史 `doc/`；本计划写入根目录新默认 `docs/scheduling/`，该目录和文件本身不构成对历史 `doc/` 的迁移或改名。

## 7. 计划冲突与处理记录

1. **B1 的职责定义与治理写权冲突**：PM 的 `docs/architecture.md`、`docs/project-rules.md` 在 PM Section 1 内，但其中纯角色职责定义不能由 PM 自行改写；招募的治理边界又不取得 PM 工作文档写权（2026-10-20 治理原则）。处理：招募提供现行角色定义文案或链接目标，PM 作为文档所有者落地；若需招募直接写入，须先由招募报告并取得治理授权，不在本计划内先行扩权。
2. **新增路径的前置依赖**：B4 实际变更记录、R1 内容更新、A1 报告都依赖招募先补精确路径；在这些路径进入对应 Section 1 前，相关 owner 不得提前写盘。顺序见第 5 节。
3. **R5 涉及统筹自己的角色卡**：`角色卡/统筹调度/role-card.md` 由招募维护，本调度上下文不自行修改；调度只提供统一文案和验收条件，避免“角色写自己定义”。
4. **R2 的授权依据缺口**：`references/project-rules.md`、`references/role-memo.md` 已存在而边界仍写“待新增”。招募需如实核对创建依据；若无法证明此前授权，记录事实并交验收判断，不补造授权。
5. **B5 收窄与通用 bootstrap 的平衡**：内置边界同时服务其他项目的角色 bootstrap；收窄时不能删除按已授权团队计划建立 worker 角色所需的定义维护能力。验收条件是“更窄且有明确适用条件”，不是简单删条目导致流程不可用。
6. **B2 与 B1 同文件导航依赖**：PM 的 feature-map 依赖 B1 正文最终状态；合并为同一写作轮次，避免先后不一致。
7. **A1 与前一轮报告**：第一轮验收没有正式报告文件，本轮不能补造前一轮报告；A1 报告只记录本轮复核结论，并在其中说明第一轮结论来源。验收边界补路径之前，任何角色不得代写验收报告。
8. **`docs/` 与历史 `doc/` 并存**：本计划文件是根目录新默认 `docs/scheduling/` 的第一个实例；R3 的说明必须与此事实一致，明确历史 `doc/` 保留、不回溯迁移，不产生第二套当前文档。

## 8. 复核放行条件

- 本计划全部返工项完成，且没有超出第 2 节的权限结论。
- 独立验收按同一版策划方案复核并给出**匹配当前冻结候选**的结论；报告已写入 A1 路径。
- 只有通过结论才释放本轮；返工交原所有者，证据不足安排补证；调度不代替验收判断，也不修改任何被点名文档。

## 9. 第二轮返工追加计划（2026-10-22）

- 追加性质：本节只追加第二轮返工安排，不改写第 1–8 节的第一轮计划与历史记录；计划任务 ID 沿用 `five-role-rework-2026-10-22`，不新增计划 ID。
- 依据：独立验收第二轮结论 **返工**（2026-10-22，报告文件 `角色卡/验收/docs/acceptance/2026-10-22_five-role-model-result.md`），经协调方转达；本轮不新增标准、不扩大范围。

### 9.1 验收第二轮结论

- 第二轮结论：**返工**。第一轮计划项 B1–B5、R1–R3、R5、R6、A1 已实质关闭；第二轮一致性扫描仍发现三处阻塞项（编号沿用验收报告）：
  1. K1：`角色卡/任务工具/role-card.md:22` 仍写“项目管理的技术架构/实现设计”；
  2. K2：`角色卡/测试/role-card.md:24` 同样写“项目管理的技术架构/实现设计”；
  3. K3：`角色卡/测试/role-card.md:31` 仍把一般“架构或设计问题”交项目管理评估。
- 两个非阻塞项：
  1. N2：`角色卡/项目管理/memo.md:7` 的“负责架构”未限定“实现层架构”，建议限定；本轮由项目管理自行修正。
  2. N1：`references/functional-description.md:5` 仍有旧句（“Project management owns overall architecture and role collaboration in its own docs/architecture.md.”），且该文件不在任何 Section 1 内、无所有者；作为残留记录，**不在本轮修**，留待后续治理轮次确定归属后处理。
- 定性：K1–K3 不是新需求，直接对应客户确认的基线第 5 条“架构设计归策划”和第一轮 R6 的“产品方案/架构设计与实现设计/技术契约”区分；N1 属残留，不阻塞。

### 9.2 候选范围

- 仓库根：`/Users/wangzhongren/code/vibeingcode/组内培训/ans-skill`；分支：`feat/five-role-model`；已提交基线：`f76127d`；与第 1.2 节相同，不产生新提交。
- 复核对象：当前工作区整体候选（不 commit）。当前 `git status --porcelain` 为 66 个已修改跟踪文件加 3 个未跟踪文件（本返工计划、技能规范变更记录、验收报告），共 69 条；验收报告记录的写盘前快照为 68 条（66 个已修改跟踪文件 + 计划 + 变更记录），差异仅为报告文件自身。
- 本轮实际修正只涉及三个既有文件：`角色卡/任务工具/role-card.md`、`角色卡/测试/role-card.md`、`角色卡/项目管理/memo.md`；不新增任何文件或路径。
- 本节追加只更新本计划文档自身；计划文件不是 K1–K3 的修正对象，其内容变化不改变“被验候选”的定义。

### 9.3 角色增减与权限结论

- **无角色增减**：不新增、删除、合并、拆分任何角色；不改变任何 `roleId`、组别、角色默认写权或既有 Section 1。
- 写入归属不变：`角色卡/任务工具/role-card.md`、`角色卡/测试/role-card.md` 属角色卡，由招募（ANS 团队组建）按治理职责修正，任务工具/测试角色不自写角色卡；`角色卡/项目管理/memo.md` 由项目管理在其自身 Section 1 内修正。
- **不新增路径**：三处修正都落在现有 Section 1 的既有文件内；验收定向复核写入其现有 A1 报告路径，不新增报告文件。不修改共享文档、角色定义参考、`scripts/`、`dashboard/`、`.e2e-todo/`、已安装副本或 public 镜像。

### 9.4 分派与定向复核

| 项 | 所有者 | 写入范围 | 必须修正 | 定向复核条件 |
| --- | --- | --- | --- | --- |
| K1、K2 | 招募 | `角色卡/任务工具/role-card.md:22`、`角色卡/测试/role-card.md:24` | 把“项目管理的技术架构/实现设计”改为：“策划负责产品方案/架构设计；项目管理仅在统筹团队计划建立时负责实现设计/技术契约；架构或设计问题按此区分。”可结合各卡列表上下文调整为通顺表述（如验收报告 K1/K2 建议的写法），但不得改变该区分。 | 两文件不再出现“项目管理的技术架构/实现设计”或等价所有权断言；与 `references/planning-role.md`、`project-role.md` 及 R6 修正后的 `references/test-role.md`、`acceptance-role.md` 一致。 |
| K3 | 招募 | `角色卡/测试/role-card.md:31` | 把一般“如涉及架构或设计问题，统筹再交项目管理评估”改为按区分路由：“产品方案/架构设计问题交策划；实现设计/技术契约问题交已按团队计划建立的项目管理角色；未建立时不虚构该角色，由统筹安排。” | 一般“架构或设计问题”不再默认交项目管理；与 R6 修正后的角色定义表述一致。 |
| N2 | 项目管理 | `角色卡/项目管理/memo.md:7` | 把“负责架构”限定为“负责实现层架构”（如“负责实现层架构、契约评审、项目法案及已获准的共享代码工作”），与本文件第 14 行现行模型表述一致。 | “架构”不再被读作整体/产品架构；不扩大职责；其余条目不动。 |
| 定向复核 | 验收 | 既有报告路径 `角色卡/验收/docs/acceptance/2026-10-22_five-role-model-result.md`（追加/更新，不新增文件） | 只检查 K1–K3 三处阻塞项及 N1、N2 两个非阻塞项；不重做第一轮全部检查（程序测试、全库链接、全边界覆盖、MD/YAML 全量比对等不再重复，除非定向检查中发现必须）。复核前记录当前 `git status --porcelain` 快照及三处修正文件哈希。 | 给出通过/返工结论；结论明确标注“定向复核”及其覆盖范围；N1 按“不在本轮修”的残留如实记录，不作为本轮阻塞条件。 |

### 9.5 执行顺序

1. 招募修正 K1、K2、K3（两个角色卡文件同一批）；项目管理修正 N2（可并行）。互不改对方文件。
2. 修正完成后冻结当前工作区候选（记录 `git status --porcelain` 及三处修正文件哈希），由协调方通知验收。
3. 验收按 9.4 定向复核，只检查三处阻塞项及非阻塞项，不重做全部检查；结论写入其既有报告路径。
4. 验收结论为通过则按第 8 节放行；仍返工则交回对应所有者；证据不足安排补证。调度只消费结论，不改结论、不代写。

### 9.6 本轮明确不做

- 不修 N1（`references/functional-description.md:5`）；N3（治理边界历史沿革）与 N4（站点根路径）按验收报告无需动作，本轮不处理。
- 不新增路径、不新增/删除角色；不修改 9.4 分派范围之外的任何文件；不修改共享文档、角色定义、`scripts/`、`dashboard/`、`.e2e-todo/`。
- 不 commit、不 push、不 install、不发布；不启用真实项目任务记录。
