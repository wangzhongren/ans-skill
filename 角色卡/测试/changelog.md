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
