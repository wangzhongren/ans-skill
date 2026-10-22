---
id: role-groups-feature
type: feature
title: 平级角色与组别分类
created: "2026-10-14"
updated: "2026-10-19"
timezone: Asia/Shanghai
status: implemented-unverified
related: [role-groups-design, role-groups-change, role-groups-validation, group-leadership-design, group-leadership-change, group-leadership-validation]
events:
  - date: "2026-10-14"
    kind: created
    summary: 记录角色卡组别字段和独立权限的使用规则
  - date: "2026-10-14"
    kind: implemented
    summary: 完成组别字段、角色模板、建卡流程及调度说明
  - date: "2026-10-14"
    kind: verified
    summary: 上轮组别文档一致性与逐角色范围检查通过
  - date: "2026-10-14"
    kind: evidence-invalidated
    summary: 本轮新增组长与组内协作流程，旧验证不覆盖本轮变更
  - date: "2026-10-14"
    kind: implemented
    summary: 增加组内职责、两级调度、工作量评估与汇报规则
  - date: "2026-10-14"
    kind: verified
    summary: 文档一致性核对和三项独立只读情境判断通过
  - date: "2026-10-19"
    kind: evidence-invalidated
    summary: 用户去除组长对象，组别只分类；统筹直接逐角色调度和接收反馈，旧报告不覆盖新流程
---

# 平级角色与组别分类

组别帮助读者看出哪些角色常合作，只保留 `group` / 组别分类字段。当前不设置组长对象、组内职责或组内派发/汇报层级。每个角色保持平级，文件权限仍只看各自边界第 1 节。

## 当前过程

人事（原团队组建/招募）角色按已获准的职责和文件范围建立角色卡、边界及其同步 YAML。已有角色改组只改分类，不新增权限，也不按组迁移目录。角色数按已确认定义计数，同一 `roleId` 多个上下文不算增员。

统筹直接读取角色定义，询问每个受影响角色的现有任务、剩余工作、依赖和阻碍。缺信息就标待评估，不编造工时；任务确有讨论需要时才组织最小必要角色。现有职责能承接就复用，确需招聘或边界调整时交人事，核对已有授权覆盖后落实角色定义。

```mermaid
flowchart TD
  request[统筹接到请求] --> inspect[读取实际角色和边界，直接询问工作量与依赖]
  inspect --> enough{现有职责和范围能承接吗}
  enough -->|信息不足| pending[向相关角色补取事实，未清楚部分待办]
  pending --> inspect
  enough -->|需要角色或边界调整| formation[人事按授权提出并落实精确角色定义]
  formation --> authorize
  enough -->|可以| authorize[统筹核对具体角色授权、确认方案、依赖和写入冲突]
  authorize --> ready{全部条件满足吗}
  ready -->|否| wait[对应阶段待办，不扩大权限]
  ready -->|是| reserve[统筹逐角色预留范围并启动独立固定上下文]
  reserve --> work[各角色完成自己的工作和真实检查]
  work --> report[原始反馈直接交统筹，证据供独立验收核对]
  report --> judge[独立验收按标准判通过、返工或证据不足]
  judge --> result[工具单写记录，统筹按结论放行、返工或补证]
```

执行者只取得自己的工作凭证，统筹只持调度凭证，独立验收只持验收凭证。所有操作走同一个单写工具；组别、父子代理关系或读取他人卡都不能替代授权。没有工具也遵守逐角色授权、边界、依赖和独立上下文；无法新建上下文就报告待办，不切换身份。

同组不等于共享私有 common、Model、公开契约或 shared 写权。实现者保留自己的真实报告；测试实际执行检查，验收判断交付，统筹不能修改他人报告或自行判通过。更详细的当前规则见[人事](../../../../references/team-formation.md)、[统筹](../../../../references/scheduler.md)和[独立验收](../../../../references/acceptance-role.md)。

## 历史

- 2026-10-14 · 组别字段、角色平级与逐角色范围规则验证通过；详见[上轮变更](../change/2026-10-14_change_role-groups.md)与[上轮测试报告](../../../测试/docs/change/2026-10-14_change_role-groups-validation.md)。
- 2026-10-14 · 本轮文档一致性核对和三项独立只读情境判断通过；依据[当时项目管理方案](../../../项目管理/docs/design/2026-10-14_design_group-leadership.md)，规则变化见[变更记录](../change/2026-10-14_change_group-leadership.md)，检查范围与限制见[测试报告](../../../测试/docs/change/2026-10-14_change_group-leadership-validation.md)。

- 2026-10-19 · 当前流程按权责拆分更新，待本轮独立验证；见[拆分功能](role-authority-split.md)与[变更记录](../change/2026-10-19_change_role-authority-split.md)。
