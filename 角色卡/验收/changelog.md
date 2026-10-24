# 验收角色变更记录

- 2026-10-19：按用户后续决定删除组长/组员层级；验收与统筹、测试及实现角色平级，继续保持独立结论职责。Doc: [role-card.md](role-card.md)。

- 2026-10-19：依据用户确认的职责拆分及《角色职责拆分》方案新建独立验收角色。仅授予本角色导航、memo 及本轮验收标准/结果两份文档权限；不含测试、实现、调度或任务状态写入权。Doc: [role-card.md](role-card.md)、[boundary.md](boundary.md)、[boundary.yaml](boundary.yaml)。

## 2026-10-20 — 工作流缺口文档授权

依据用户 2026-10-20 授权，仅为本角色增加以下定点工作文档写入路径：`角色卡/验收/docs/acceptance/2026-10-20_workflow-fixes-criteria.md`, `角色卡/验收/docs/acceptance/2026-10-20_workflow-fixes-result.md`。其他角色路径及未列程序路径仍按原边界管理；本次不修改角色身份或组别。

## 2026-10-22 — 五内置管理角色模型下的验收基线

按用户确认的五内置管理角色模型，完成标准必须来自同一版已确认的策划方案（产品方案＋架构设计），实施后按同一版本判断当前候选；验收不自造标准、不增加需求，方案缺少可验收标准时退回策划补充。角色卡职责、必读资料与交接同步更新；Section 1 路径不变。Doc: [role-card.md](role-card.md)。

## 2026-10-22 — 五内置管理角色返工复核报告路径

依据 2026-10-22 返工计划 `docs/scheduling/2026-10-22_five-role-rework.md` 的 A1，为本角色增加精确单文件路径 `角色卡/验收/docs/acceptance/2026-10-22_five-role-model-result.md`，用途为五内置管理角色候选返工复核的独立验收结果；同名 YAML 同步。报告由独立验收在全部返工修订完成、候选冻结并独立复核后写盘；招募（现人事）只补路径，不代写报告，也不改结论。Doc: [boundary.md](boundary.md)、[boundary.yaml](boundary.yaml)。

## 2026-10-22 — 三道客户闸门中的验收基线

依据用户新增的流程要求，在角色定义中明确：验收基线是客户通过闸门 1（方案确认）确认的那一版策划方案，上位依据是客户通过闸门 0（意图确认）确认的意图；验收按该版本判断，不按策划草稿、未确认的团队计划或未经客户确认的角色指派判断。确认记录以 `docs/communication/` 为准，找不到记录时按证据不足处理并交沟通补确认。客户确认的意图或方案版本变更时，受影响部分重新判断。同步更新角色卡开篇、必读资料与执行原则；不改变角色身份、边界或程序权限。Doc: [role-card.md](role-card.md)、[acceptance-role.md](../../references/acceptance-role.md)、[communication-role.md](../../references/communication-role.md)。

## 2026-10-22 — 内置角色工作备忘录

依据用户新增要求，明确内置角色也维护自己的工作备忘录：验收默认路径为 `docs/acceptance/memo.md`，项目可通过已接受的治理边界覆盖到角色既有范围。memo 是角色私有的续接线索和已核事实，不是任务状态、不是角色定义，也不是验收标准或结论；不写其他角色文档，位于既有默认窄范围内，不扩大写权；验收完成工作后更新自己的 memo，属于交付的一部分。角色卡与边界路径不变。Doc: [acceptance-role.md](../../references/acceptance-role.md)、[role-card.md](role-card.md)。

## 2026-10-22 — 运行架构与上下文隔离

客户窗口只加载沟通角色；验收由沟通启动独立子代理上下文，只接收自己的角色、边界、授权、任务输入和交付要求，不在同一上下文切换为其他角色。验收不直接给工作角色派活、授权或启动；统筹把当前候选和证据交验收，结论回沟通和统筹。角色卡执行原则同步本条；不改变角色身份、边界或程序权限。Doc: [role-card.md](role-card.md)、[acceptance-role.md](../../references/acceptance-role.md)。

## 2026-10-22 — 验收表与风险分档

依据用户新增要求，验收改为“验收表 + 查看改动记录 + 按风险定向补测”，不再每次全量重跑。验收表列包括 ID、方案条目/标准、需要的证据、实际证据路径/哈希、候选版本、产出角色、结果和验收判断（pass / fail / insufficient evidence / not applicable）；验收读取统筹的变更包（候选哈希、改动路径、任务节点、证据链接、风险档位 T0-T3），按表核对证据覆盖。风险分档以 `references/testing.md` 为唯一定义：T0 纯文档（不涉及治理/权限变更）只做链接、锚点、一致性检查；T1 局部实现做受影响单元/层测试和冒烟并复用未受影响证据；T2 跨角色/契约/shared 做受影响单元、集成/契约和受影响完整流程；T3 发布/共享抽象/治理或权限变更做全量回归、集成和完整验收。全量回归只在 T3 或证据不足时使用。同候选、同输入/依赖、同命令证据可复用，变化时只补失效部分；缺证据或覆盖不足判证据不足。同步更新验收角色卡执行原则；不改变角色身份、边界或程序权限。Doc: [acceptance-role.md](../../references/acceptance-role.md)、[role-card.md](role-card.md)。

## 2026-10-22 — 策划方案复核实施的验收标准与结果路径

依据客户通过闸门 2 确认并给出独立实施授权的团队计划 [2026-10-22_planning-proposal-review.md](../../docs/scheduling/2026-10-22_planning-proposal-review.md)（确认记录见 [2026-10-22_communication_planning-proposal-review.md](../../docs/communication/2026-10-22_communication_planning-proposal-review.md)）第 9.2 节，为本角色增加两个精确单文件路径：`角色卡/验收/docs/acceptance/2026-10-22_planning-proposal-review-criteria.md`，用途为本轮策划方案复核实施的独立验收标准；`角色卡/验收/docs/acceptance/2026-10-22_planning-proposal-review-result.md`，用途为本轮策划方案复核实施的独立验收结果。这是两个精确单文件，不是 `docs/acceptance/` 目录级授权；验收仍只写这两个文件，不取得其他角色文档、角色定义、任务状态或代码写权。同名 YAML 同步。本路径先于标准与结果写盘生效，验收后续只按客户确认的 P1 方案版本判断，不把复核记录当验收基线。Doc: [boundary.md](boundary.md)、[boundary.yaml](boundary.yaml)。

## 2026-10-23 — 验收并行取证的验收标准与结果路径

依据客户通过闸门 2 确认并给出独立实施授权的团队计划 [2026-10-23_parallel-acceptance-evidence.md](../../docs/scheduling/2026-10-23_parallel-acceptance-evidence.md)（确认记录见 [2026-10-23_communication_parallel-acceptance-evidence.md](../../docs/communication/2026-10-23_communication_parallel-acceptance-evidence.md)）第 9.2 节，为本角色增加两个精确单文件路径：`角色卡/验收/docs/acceptance/2026-10-23_parallel-acceptance-evidence-criteria.md`，用途为本轮验收并行取证的独立验收标准；`角色卡/验收/docs/acceptance/2026-10-23_parallel-acceptance-evidence-result.md`，用途为本轮验收并行取证的独立验收结果。这是两个精确单文件，不是 `docs/acceptance/` 或 `角色卡/验收/docs/acceptance/` 目录级授权；验收仍只写这两个文件，不取得其他角色文档、角色定义、任务状态或代码写权。未新增权限、未修改 `references/authority-matrix.md`；同名 YAML 同步。N1a 只补路径与边界记录，标准和结果由验收后续按客户确认的 P2.2 版本与团队计划写入，本记录不表示标准或结果已存在。Doc: [boundary.md](boundary.md)、[boundary.yaml](boundary.yaml)。

## 2026-10-23 — 验收并行取证流程描述

依据客户确认的团队计划 [2026-10-23_parallel-acceptance-evidence.md](../../docs/scheduling/2026-10-23_parallel-acceptance-evidence.md)（确认记录见 [2026-10-23_communication_parallel-acceptance-evidence.md](../../docs/communication/2026-10-23_communication_parallel-acceptance-evidence.md)）与客户在闸门 1 确认的 P2.2 方案，在验收角色定义和本角色卡中明确：沟通启动唯一验收主上下文和全部只读取证子上下文；验收主上下文只合并证据、复核、处理冲突、作唯一判断并写唯一 B2，不启动子上下文；取证子上下文只读，没有 Section 1 写路径，不持有 `acceptanceToken`，不给 pass/fail，不派发，最多 4 个（E1–E4 是同一验收角色的上下文编号，不是角色、不是子验收）。完整规则只在[验收并行取证规则](../../references/acceptance-parallel-evidence.md)定义，其他文档只摘要和链接，不复制完整清单。同步更新本角色卡执行原则、[独立验收规则](../../references/acceptance-role.md)、[沟通角色](../../references/communication-role.md)和[统筹调度](../../references/scheduler.md)的相关流程描述；未新增权限、未修改[角色权力矩阵](../../references/authority-matrix.md)，五个内置管理角色、三道客户闸门、唯一验收结论和统筹唯一调度口不变。Doc: [role-card.md](role-card.md)、[acceptance-role.md](../../references/acceptance-role.md)、[communication-role.md](../../references/communication-role.md)、[scheduler.md](../../references/scheduler.md)、[acceptance-parallel-evidence.md](../../references/acceptance-parallel-evidence.md)。
