---
id: role-authority-split-change
type: change
title: 默认由统筹接待，招聘和验收各自独立
created: "2026-10-19"
updated: "2026-10-19"
timezone: Asia/Shanghai
status: implemented-unverified
related: [role-authority-split-feature, role-authority-split-design]
events:
  - date: "2026-10-19"
    kind: implemented
    summary: 更新技能入口和现行参考，按用户后续要求去除组长并定义独立内置团队组建；实际工具字段已核对，独立验证待交付
  - date: "2026-10-19"
    kind: changed
    summary: 按用户追加决定明确策划产品方案与PM技术设计的交接，原技术方案和CLI契约保留
---

# 默认由统筹接待，招聘和验收各自独立

以前默认项目管理同时接需求、安排角色、写 shared 并协调验收，任务工具的协调凭证还可以把阶段记通过。现在技能把这些工作分开：**统筹安排，策划写后续产品方案，项目管理做技术设计与评审，测试真实执行，独立验收判断完成；招聘与文件边界交独立内置 ANS 团队组建。**当前规范见[功能说明](../feature/role-authority-split.md)，技术设计见[项目管理方案](../../../项目管理/docs/design/2026-10-19_design_role-authority-split.md)。

## 用户决定与具体改动

用户先确认职责拆分并要求实施，随后明确“组长对象去除掉”，再明确招聘和边界调整由单独内置角色负责。后续要求替代原先保留组长的安排：只保留 group 分类，统筹直接逐角色授权、预留、派发和收反馈。ANS 团队组建承接原 ANS Governance 职责与固定身份，不新建第二个重叠治理所有者。用户随后追加独立策划：后续需求先形成产品方案，再交项目管理做技术架构、实现设计与技术评审，已有同版同范围授权复用，本轮原技术方案不重写。

| 实际入口/位置 | 前后变化 |
| --- | --- |
| [英文入口](../../../../SKILL.md)、[中文入口](../../../../SKILL.zh.md)、[README](../../../../README.md) | 默认 PM 接待改为新统筹上下文；明确团队组建、架构、测试和独立验收边界 |
| [初始化](../../../../references/bootstrap-workflow.md)、[角色模板](../../../../references/role-card.md)、[边界格式](../../../../references/module-boundary.md) | 新项目落实分开的真实项目卡与范围；去除 groupDuty 和组长机制；旧项目显式迁移 |
| [团队组建](../../../../references/team-formation.md)、[内置边界](../../../../references/built-in-boundary.md)及同名 YAML | 新招聘与边界入口承接原治理身份，保持原 Section 1 范围，不变成全局源码写权 |
| [策划](../../../../references/planning-role.md) | 新增独立产品/需求方案职责、文档范围与技术设计交接；不写代码或调度/验收 |
| [项目管理](../../../../references/project-role.md)、[方案审核](../../../../references/proposal-review.md)、shared/API 指南 | 保留架构、抽象、质量审核和 shared 及其测试；派发与最终判断交其他角色 |
| [统筹](../../../../references/scheduler.md)、[会议](../../../../references/meeting.md)、[协调记录](../../../../references/coordination.md) | 直接逐角色安排与汇报；讨论只邀必要角色，单写记录保持 |
| [测试](../../../../references/test-role.md)、[验证门禁](../../../../references/testing.md)、[证据](../../../../references/evidence.md)、[独立验收](../../../../references/acceptance-role.md) | 真实测试结果与完成判断分开；标准前置，结论区分通过、返工、证据不足 |
| [旧组长链接](../../../../references/group-leadership.md)、[当前组别说明](../feature/role-groups.md) | 旧链接留简短兼容说明；当前流程取消组长对象和层级，历史记录保留 |

任务程序位于 `scripts/task_ops.py` 与 `scripts/coordination_store.py`，由任务工具角色实施；本角色维护 [task-operations.md](../../../../references/task-operations.md) 的准确说明，已按当前代码补齐配置、请求示例、状态和限制。真实角色卡、边界和治理 changelog 由团队组建角色维护，本角色没有代改它们。

## 迁移与范围

旧项目先盘点卡、边界、活动写入者、配置与任务，取得现有授权未覆盖的必要决定后再迁移；旧 PM 上下文保留架构身份，新统筹和验收分别在新上下文承接。旧任务只作为原流程历史，所需新版任务重新授权并收集必要证据。不能仅靠改名或重算哈希算完成。

本次不改五层运行时调用规则，不引入新云端角色 Key；默认仍读 Markdown 架构和功能文档，云端同步仍手动，安装 URL 与 MIT 保留。没有选装实现。本角色未 push、安装或发布。

## 验证状态

规范已修改。2026-10-19 本角色静态核对 32 份当前文件的 276 个本地链接/锚点，无缺失；`git diff --check` 通过，内置边界 Markdown 与 YAML 的 5 项范围一致。skill-creator 的 `quick_validate.py` 在系统及应用捆绑 Python 都因缺少 PyYAML 未能运行，未安装额外依赖。

接口已按实际 `task_ops.py` 和 `coordination_store.py` 核对：配置/计划 schema 仍为 1，任务状态为 2；统筹用 `schedulerToken`，验收独立用 `acceptanceToken`。指南补齐 `acceptanceAuthority`、前期预检与逐项验收字段，明确阶段通过不等于最终完整流程通过、旧 JSON 只读加载范围及环境快照能检测的范围。

实际 API 对齐后，本角色仅复核本阶段变动的 8 份文件：49 个本地链接/锚点无缺失，限定路径 `git diff --check` 通过，真实 CLI `--help` 列出本文命令。

开发者[原报告](../../../任务工具/docs/change/2026-10-19_change_task-authority.md)记录 49 项开发单测及隔离 timer 回放通过；[固定测试原报告](../../../测试/docs/change/2026-10-19_change_role-authority-split-validation.md)承载其实际运行与最终候选证据，当前正在整理；独立验收尚未给终验结论。新增策划及后续需求路由按[方案补充第 11 节](../../../项目管理/docs/design/2026-10-19_design_role-authority-split.md#11-用户新增决定后续需求先由独立策划形成产品方案)和[标准 v2](../../../验收/docs/acceptance/2026-10-19_role-authority-split-criteria.md)同步，只影响协作 C8，不增加 CLI 字段或改代码标准。

新增策划路由后，本角色最后核对 21 份本阶段文件均在 Section 1：272 个本地链接/锚点无缺失，限定路径 diff 检查通过，内置边界 Markdown/YAML 的 5 项范围一致。未重跑源码全套测试。

本角色的规范与接口文档交付完成。实际执行事实由原测试报告记录，最终结论由独立验收报告给出，并从验收导航和统筹交接索引查阅；不为复制结果再次改动本产品候选。源码核对或中途静态检查不代表完整功能通过。
