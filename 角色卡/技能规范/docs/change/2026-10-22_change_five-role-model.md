---
id: five-role-model-change
type: change
title: 五个内置管理角色：技能入口与共享参考的实际变更记录
created: "2026-10-22"
updated: "2026-10-22"
timezone: Asia/Shanghai
status: implemented-unverified
related: [role-authority-split-feature]
events:
  - date: "2026-10-22"
    kind: implemented
    summary: 记录本候选内技能规范所属共享文档的实际正文修改；按返工计划完成 B3、B4、R1、R3、R5 和内置角色 memo 例外说明；独立验收待复核
---

# 五个内置管理角色：技能入口与共享参考的实际变更记录

本记录对应当前分支 `feat/five-role-model` 上的未提交候选（已提交基线 `f76127d`），记录**技能规范角色 Section 1 内**共享文档的实际正文修改。逐行差异以 `git diff HEAD -- <文件>` 为准；治理归属、角色卡和角色定义类参考的修改由 ANS 团队组建（招募）另行记录，见[本角色边界](../../boundary.md)、[本角色 changelog](../../changelog.md)与[治理变更记录](../../../../references/governance-changelog.md)。

返工依据：[2026-10-22 五内置管理角色候选返工计划](../../../../docs/scheduling/2026-10-22_five-role-rework.md)。本记录不冒充验收通过；最终结论以独立验收报告为准，报告路径见第 8 节。

## 1. 覆盖范围

- 入口文档：`SKILL.md`、`SKILL.zh.md`、`README.md`。
- 宣传页：`site/index.html`、`site/en/index.html`。
- 共享参考：`references/architecture.md`、`role-card.md`、`bootstrap-workflow.md`、`module-boundary.md`、`documentation.md`、`proposal-review.md`、`workflow.md`、`feature-point.md`、`project-rules.md`、`role-memo.md`、`meeting.md`、`task-operations.md`、`shared-directories.md`、`api-spec.md`、`testing.md`、`evidence.md`、`coordination.md`、`group-leadership.md`，以及本轮加入归属的三个旧参考 `project-context.md`、`role-architecture-viewer.md`、`dashboard.md`。
- 不纳入本记录：`references/communication-role.md`、`planning-role.md`、`project-role.md`、`scheduler.md`、`team-formation.md`、`acceptance-role.md`、`test-role.md`、`built-in-boundary.md`/`.yaml` 等角色定义或治理文件。它们由招募维护，“角色不写自己的角色定义”，即使同在本候选内被修改，也不算技能规范变更。
- `references/action-policy.md`、`references/entrypoint.md` 本候选未改正文；`site/style.css`、`site/main.js` 未改。
- 边界归属变化与正文修改分开记录：本候选把 `references/architecture.md`、`references/project-context.md`、`references/role-architecture-viewer.md`、`references/dashboard.md` 和本记录路径加入本角色 Section 1，这是招募维护的**授权变化**，不等于正文变化；第 2–4 节列的是**实际正文修改**。逐项差异以 `git diff HEAD` 为准。

## 2. 入口文档与宣传页

| 文件 | 实际修改 |
| --- | --- |
| [SKILL.md](../../../../SKILL.md) | 把“项目角色 + 唯一内置团队组建”的旧入口改成五个内置管理角色（沟通、策划、招募、统筹、验收）：沟通是客户唯一接口并先交策划；策划写产品方案、架构设计与共有业务契约；统筹判断团队（不变/新招/拆分），需要时把团队计划写入 `docs/scheduling/` 交招募；客户确认/实施授权后再派发。新增五个内置角色的默认写范围表、五角色运行模型、按需建立项目管理（技术架构）角色的条件、角色绑定/交接与加载路由的对应修改；`common/shared/` 归属改为条件化。R5 返工统一了第 18、178、194 行附近及“团队判断后直接派发”的旧顺序，补上“角色就绪 → 客户确认/授权 → 派发”，并保留同版授权复用。 |
| [SKILL.zh.md](../../../../SKILL.zh.md) | 与英文入口同步：五个内置角色、默认写权、策划负责架构设计、项目管理按需建立、预检登记五个内置角色、`common/shared/` 条件归属。R5 返工修正第 10、21 行附近跳过客户确认/授权或把授权放在团队判断之前的旧表述，统一为“策划完成 → 统筹判断团队 → 必要时招募 → 客户确认/授权 → 派发”。 |
| [README.md](../../../../README.md) | 首段、角色分工表、日常开发步骤、新项目四步、文件表与“怎么查看”全部按五角色模型重写：策划给产品方案和架构设计，项目管理按需说明实现架构；团队组建只按统筹计划建卡；验收按同一版策划方案判断。R5 返工修正第 53、97 行附近的派发顺序。R3 新增“顶层历史 `doc/` 保留、新默认 `docs/`、两者并存”的说明（见第 5 节）。 |
| [site/index.html](../../../../site/index.html) | “职责清楚”角色说明改为五个管理角色开箱即用、策划先写方案与架构、统筹判断团队、项目管理按需建立；“开始工作”四步改为接单与策划 → 统筹判断团队 → 准备配置与预检 → 获准后开始；FAQ“在哪里查看五层和功能流程”改为策划方案/架构 + 按计划建立的项目管理实现架构。HTML 结构、样式、脚本未改。 |
| [site/en/index.html](../../../../site/en/index.html) | 与中文页对应的英文文案同步修改（角色说明、开始工作四步、FAQ）；页面结构、样式、脚本未改。 |

## 3. `references/architecture.md` 正文的实际修改

该文件本候选**确实修改了正文**，不是“只调整边界归属、不改正文”：

- 目录树说明：`common/shared/` 的拥有者从“项目管理”改为“按统筹团队计划建立的项目管理（技术架构）角色”；角色文档说明改为“策划拥有 `docs/planning/` 的产品方案与架构设计；只有统筹团队计划建立项目管理（技术架构）角色后，才由该角色拥有实现层 `docs/architecture.md` 与技术契约”。
- 模块成长规则：跨角色基础复用改为“当统筹团队计划建立项目管理（技术架构）角色时，经该角色和 `common/shared/` 处理；否则由统筹判断团队计划是否需要该角色”。
- 原“只调整边界归属、不修改正文”的治理记录已由招募在同一候选内更正；本记录以 `git diff HEAD -- references/architecture.md` 为实际依据。

五层运行时的调用方向、相邻层规则和 `abstract/`/`public/`/`impl/` 结构未改变；本次只改所有权与“策划架构 vs 实现层架构”的文字归属。

## 4. 其他共享参考的主要修改点

| 文件 | 主要修改 |
| --- | --- |
| [role-card.md](../../../../references/role-card.md) | 角色卡规则从“所有项目角色”改为“worker 角色”；五个内置管理角色直接使用参考文档、不需要项目卡；项目管理只在团队计划要求时建卡；架构问题分流为“架构设计交策划，实现设计交已建立的项目管理角色”；共享代码、评审路由和 `api-spec` 归属同步条件化。本轮补一句：普通项目里五个内置管理角色不需要项目卡和 memo；项目（包括本仓库）经已接受治理为内置角色采用项目卡/memo/功能导航时按该项目 Section 1 执行，不改变技能默认。 |
| [bootstrap-workflow.md](../../../../references/bootstrap-workflow.md) | bootstrap 只建立 worker 角色，五个内置角色开箱即用；流程改为沟通接单、策划出方案与架构、统筹判断团队并把团队计划交招募；`common/shared/`、实现层架构、工程法案、登记内容全部改为“团队计划建立项目管理角色时”的条件表述；worker 角色验收后交回统筹，R5 补上客户确认/授权后再派发。 |
| [module-boundary.md](../../../../references/module-boundary.md) | 边界文档结构只适用于 worker 角色；五个内置管理角色以参考文档自带默认范围；项目管理角色的 shared 与 `docs/architecture.md` 改为按团队计划建立时；跨角色复用需求交统筹判断。 |
| [documentation.md](../../../../references/documentation.md) | 章节改为“产品方案与架构先写，按团队计划审核”；策划写 `docs/planning/` 的产品方案、架构设计和共有契约；项目管理只在按计划建立时维护实现层架构和跨角色实现设计；R5 修正派发顺序；R3 增加历史 `doc/` 与新默认 `docs/` 并存的说明。 |
| [proposal-review.md](../../../../references/proposal-review.md) | 标题和正文改为“已建立技术架构角色时的方案审核”；审核者只在团队计划建立项目管理角色时存在，否则由统筹在派发前按已确认策划方案和架构核对；评审记录、角色隔离和同版复用规则保持。 |
| [workflow.md](../../../../references/workflow.md) | 新需求端到端流程改为沟通 → 策划（方案、架构、契约）→ 统筹判断团队 → 必要时招募 → 客户确认/授权 → 调度派发；R5 返工补齐客户确认与授权环节。 |
| [feature-point.md](../../../../references/feature-point.md) | 功能导航与职责变更改为“统筹判断并写入团队计划，再交团队组建”；架构设计问题交策划，实现设计问题交已按计划建立的项目管理角色；不虚构内置角色业务功能。 |
| [project-rules.md](../../../../references/project-rules.md) | 工程法案改为“如统筹按团队计划建立项目管理（技术架构）角色，由它维护”；未建立时不虚构法案路径，冲突交统筹按已有规则处理。 |
| [role-memo.md](../../../../references/role-memo.md) | memo 只属于 worker 角色；五个内置管理角色不建 memo，记录写各自默认范围。本轮补内置角色经项目治理采用 memo 的例外说明（同 role-card.md）。 |
| [meeting.md](../../../../references/meeting.md) | 主持人默认路径改为内置角色的 `docs/communication/`、`docs/scheduling/`；架构设计意见交策划，实现设计交已建立的项目管理角色；缺边界交统筹写入团队计划再交招募；会后审核按团队计划。 |
| [task-operations.md](../../../../references/task-operations.md) | 团队组建按统筹写入 `docs/scheduling/` 的团队计划准备登记；新项目不需要先接受调度定义；五个内置角色以参考文档和默认写权登记，不补造项目卡；预检失败交统筹写入团队计划再交招募修正；验收预检改为按同一版已确认策划方案核对目标与完成标准。 |
| [shared-directories.md](../../../../references/shared-directories.md) | `common/shared/` 唯一写者改为“团队计划建立的项目管理（技术架构）角色”；复用需求先交统筹判断；复用序列补上团队判断和客户确认/授权。 |
| [api-spec.md](../../../../references/api-spec.md) | 架构设计归策划；项目管理只在按计划建立时拥有跨角色集成设计；实现报告和契约差异路由同步条件化。 |
| [testing.md](../../../../references/testing.md) | shared 测试归已建立的项目管理角色；验收标准改为按同一版策划方案在实施前写明；工程法案检查条件化。 |
| [evidence.md](../../../../references/evidence.md) | 验收按已确认策划方案版本写标准；实现设计评审来自已建立的技术架构角色；边界证据认可“内置角色参考默认范围”。 |
| [coordination.md](../../../../references/coordination.md) | 项目管理只在团队计划建立时参与设计修订，否则由策划修架构；调度向沟通汇总、再转达客户。 |
| [group-leadership.md](../../../../references/group-leadership.md) | 招募与边界调整改为“调度判断并把团队计划写入 `docs/scheduling/`，招募只按计划写/改”，不再写“需要招募时直接交团队组建”。 |
| [project-context.md](../../../../references/project-context.md) | 保持旧工具定位；默认阅读路径改为策划 `docs/planning/` 的方案与架构，只有按团队计划建立项目管理角色后才看其 `docs/architecture.md`。 |
| [role-architecture-viewer.md](../../../../references/role-architecture-viewer.md) | 保持 legacy 定位；默认入口改为策划方案/架构 + 各角色 `feature-map.md` → `docs/feature/`；JSON 只作旧数据快照；shared 抽象归属和共享组件记录改为条件化。 |
| [dashboard.md](../../../../references/dashboard.md) | 保持可选旧工具定位；默认阅读路径、任务记录维护者（调度）、生成文档的输出范围按新模型修正。 |

## 5. R3：顶层历史 `doc/` 与新默认 `docs/` 并存

在 [README.md](../../../../README.md) 的“项目里维护哪些文件”之后和 [documentation.md](../../../../references/documentation.md) 的“放在谁的目录”中明确：

- 顶层历史 `doc/`（单数）保留原样，不迁移、不改名，历史设计与变更记录继续按原路径引用。
- 五个内置管理角色新默认写 `docs/communication/`、`docs/planning/`、`docs/scheduling/`、`docs/acceptance/`；招募写 `角色卡/` 治理资料。
- 两者并存，不产生第二套当前文档，也不为统一形式回溯搬迁。

## 6. 测试命令与结果

本角色在技能仓库根目录运行（2026-10-22）：

```sh
python3 -m unittest discover -s scripts/tests -q
```

结果：`Ran 236 tests in 70.150s`，`OK`，退出码 0。另运行 `git diff --check`，退出码 0，无空白错误。测试通过只说明当前脚本测试集通过，不代替独立验收，也不证明所有文档链接或页面渲染。

## 7. 返工项对照

| 返工项 | 本角色实际动作 | 主要文件 |
| --- | --- | --- |
| B3 | 功能说明正文、交接表和 Mermaid 流程图改为现行五角色流程；删除“项目管理默认做技术架构”“团队组建先建全部角色”等旧分工；保留历史事件并追加 2026-10-22 事件 | [role-authority-split.md](../feature/role-authority-split.md) |
| B4（实际变更记录） | 新建本记录，按实际 diff 列出共享文档正文修改；不把角色定义类参考算入本角色变更 | 本文件 |
| R1 | 三个旧参考保持 legacy 定位，默认阅读路径改为“策划 `docs/planning/` → 按计划建立的项目管理 `docs/architecture.md` → `feature-map.md` → `docs/feature/`”；shared 归属条件化 | `references/project-context.md`、`references/role-architecture-viewer.md`、`references/dashboard.md` |
| R3 | 在 README 和文档规则中写明顶层历史 `doc/` 保留不迁移、五个内置角色默认写 `docs/*`、两者并存 | `README.md`、`references/documentation.md` |
| R5（共享文档） | 统一为“策划完成 → 统筹判断团队 → 必要时招募 → 客户确认/授权 → 派发”，保留同版授权复用 | `SKILL.md`、`SKILL.zh.md`、`README.md`、`references/documentation.md`、`references/workflow.md`、`references/bootstrap-workflow.md` 等 |
| 内置角色 memo 例外 | 补充：普通项目里五个内置管理角色不需要项目角色卡和 memo；项目经已接受治理采用项目卡/memo/功能导航时按该项目 Section 1 执行，不改变技能默认 | `references/role-memo.md`、`references/role-card.md` |

## 8. 与验收报告和治理记录的链接关系

- 独立验收报告路径：`角色卡/验收/docs/acceptance/2026-10-22_five-role-model-result.md`（[链接](../../../验收/docs/acceptance/2026-10-22_five-role-model-result.md)）。由验收在候选冻结并完成复核后写盘；本记录不预写结论。
- 返工计划：[2026-10-22 五内置管理角色候选返工计划](../../../../docs/scheduling/2026-10-22_five-role-rework.md)（计划任务 ID `five-role-rework-2026-10-22`）。
- 功能说明：[团队组建、策划、统筹与独立验收](../feature/role-authority-split.md)。
- 治理侧记录：`references/architecture.md` 的归属增加、三个旧参考归属和本记录路径的边界授权由招募写入[本角色边界](../../boundary.md)、[同名 YAML](../../boundary.yaml)、[本角色 changelog](../../changelog.md)与[治理变更记录](../../../../references/governance-changelog.md)；本记录只负责实际正文修改，不重复或不改写治理授权。
- 状态：本候选尚未 commit、未安装、未发布；是否通过以独立验收报告为准。
