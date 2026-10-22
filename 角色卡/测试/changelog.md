# 测试角色变更记录

- 2026-10-19：按用户后续决定，移除测试角色卡的组员身份与组长汇报链；`group` 仅作分类，测试结果直接交统筹调度，最终验收仍由独立验收角色负责。Doc: [role-card.md](role-card.md)。

- 2026-10-19：依据用户确认的职责拆分与已确认方案，将独立验收结论交给新验收角色；固定测试角色保留独立跨角色流程和回归职责。本轮只新增 `scripts/tests/test_role_authority_flow.py` 单文件权限，开发单测 `scripts/tests/test_task_ops.py` 明确归任务工具角色。Doc: [role-card.md](role-card.md)、[boundary.md](boundary.md)、[boundary.yaml](boundary.yaml)。

- 2026-10-19：依据用户确认的角色权责拆分，增加一个本轮独立文档验收准备报告的精确白名单；仅文档准备，不开放程序测试文件或 `scripts/tests` 目录。Doc: [boundary.md](boundary.md)、[boundary.yaml](boundary.yaml)。

- 2026-10-16：按用户要求补充同名 boundary.yaml 同步副本及角色卡链接，增加本轮一致性验证报告的单文件范围；不授予源码权限。Doc: [boundary.md](boundary.md)、[boundary.yaml](boundary.yaml)。

- 2026-10-14：按客户确认的组长方案，标明项目协作组组员身份，新增本轮组长机制验证报告的单文件范围；仍独立验证，组长不能代写报告或把未通过结果改成通过。Doc: [role-card.md](role-card.md)、[boundary.md](boundary.md)。

- 2026-10-14：按客户确认的扁平角色分组方案，角色卡增加“组别：项目协作组”，添加本轮独立验证记录的单文件白名单。与项目管理同组不影响独立验证职责，也不授予源码修改权。Doc: [role-card.md](role-card.md)、[boundary.md](boundary.md)。

- 2026-10-10：本角色卡已接入[项目法案指南](../../references/project-rules.md)、[角色 memo 指南](../../references/role-memo.md)、共同的[项目工程法案](../项目管理/docs/project-rules.md)、本角色 memo 和[本地治理覆盖](../governance-boundary.md)；链接现有测试导航与受测功能说明。授权仍限本轮，不构成永久自动派发。Doc: [role-card.md](role-card.md)。
- 2026-10-10：创建本角色卡、边界与变更记录；授权依据为用户明确委派实施已确认方案并限定本轮角色范围。该授权不是永久自动派发授权。记录依据：[role-card.md](role-card.md) 与 [边界](boundary.md)。

## 2026-10-20 — 工作流缺口文档授权

依据用户 2026-10-20 授权，仅为本角色增加以下定点工作文档写入路径：`角色卡/测试/docs/design/2026-10-20_design_workflow-fixes-validation.md`, `角色卡/测试/docs/change/2026-10-20_change_workflow-fixes-validation.md`。其他角色路径及未列程序路径仍按原边界管理；本次不修改角色身份或组别。

## 2026-10-20：落实已确认的库存隔离复制准备范围

客户已确认 D1-final-1 第7节。仅补充该节唯一验证根内的有限材料复制与双基线清单准备例外；原项目、业务内容、治理内容与各角色新产物仍由其原责任和权限管理。Markdown 与同名 YAML 同步；此例外不作为 task_ops 跨根权限，不修改安全路径算法。

## 2026-10-22 — 返工 K2/K3：修正架构与设计问题的分流

依据 2026-10-22 返工计划 `docs/scheduling/2026-10-22_five-role-rework.md` 第 9 节 K2、K3，由 ANS 团队组建（招募，现人事）修正角色卡：必读资料不再默认把“技术架构/实现设计”交给项目管理，改为“策划负责产品方案和架构设计；项目管理仅在统筹团队计划建立时负责实现设计和技术契约，不拥有整体架构设计”；执行原则按 R6 区分“产品方案/架构设计问题交策划；实现设计/技术契约问题交已按统筹团队计划建立的项目管理（技术架构）角色；未建立时不虚构，由统筹安排”。不改变角色身份、边界或程序权限。Doc: [role-card.md](role-card.md)。

## 2026-10-22 — 运行架构与上下文隔离

客户窗口只加载沟通角色；本工作角色由统筹调度启动独立上下文，只接收自己的角色、边界、授权、任务输入和交付要求，不在同一上下文切换为其他角色；不直接接受沟通派活、授权或启动。角色卡执行原则同步本条；不改变角色身份、边界或程序权限。Doc: [role-card.md](role-card.md)。

## 2026-10-22 — 角色定义旧名修正

依据用户改名要求，`references/test-role.md` 中残留的“ANS 团队组建（招募）/招募”改为“ANS 人事（ANS People Operations，原招募）”；本角色卡与边界中的现行称呼已同步为 ANS 人事。历史记录保留旧名并注“（现人事）”。不改变角色身份、边界或程序权限。Doc: [test-role.md](../../references/test-role.md)、[role-card.md](role-card.md)。

## 2026-10-22 — 边界治理名称同步

将 `角色卡/测试/boundary.md` 与同名 YAML 中残留的“角色卡与边界由 ANS Governance 唯一维护”改为“由 ANS 人事（ANS People Operations）唯一维护”。仅同步现行名称，不改变角色身份、边界路径或程序权限。Doc: [boundary.md](boundary.md)、[boundary.yaml](boundary.yaml)。
