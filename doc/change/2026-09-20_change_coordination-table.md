---
id: coordination-table-change
type: change
title: 项目与执行角色协同表及版本反馈规则
created: "2026-09-20"
updated: "2026-09-20"
timezone: Asia/Shanghai
status: verified
related:
  - project-integration-design-change
events:
  - date: "2026-09-20"
    kind: created
    summary: 统一完成、问题、需求变更和设计修订的同步方式
  - date: "2026-09-20"
    kind: implemented
    summary: 定义单写者协同表、版本反馈和派生视图规则
  - date: "2026-09-20"
    kind: verified
    summary: 格式、引用、锚点和场景一致性检查通过
---

# 角色协同表

1. **状态源**：复用 plan.json、state.json、events.jsonl。state 保存当前状态，events 保留有序历史；board.md 或聊天表格只作为生成视图。
2. **写入职责**：项目角色是共享记录唯一写入者，执行角色通过任务通信或自身范围内的报告文件反馈。每条报告带任务、阶段、执行批次、实际依据版本、证据与稳定报告 ID。
3. **状态与事件**：执行状态复用调度枚举；需求变更和设计修订单独记事件。报告完成进入待验收，不能自行标记已完成。旧批次、旧版本和重复报告不得覆盖当前结果。
4. **变更流程**：区分提议、接受、执行角色确认和验证。新版本只阻塞实际受影响的任务，保留旧证据，无影响的任务可继续。中断恢复先核对记录与执行者状态，不重复派发写入者。

新增 [coordination.md](../../references/coordination.md)，同步中英文主导航、[项目角色](../../references/project-role.md)、[调度协议](../../references/scheduler.md)与[执行角色模板](../../references/role-card.md)。本次新增的是协议、字段和表格模板，没有创建业务项目的任务记录、消息服务或表格生成脚本。

检查场景：正常完成需验收；缺少契约进入阻塞；设计更新后旧报告被保留但不放行；重复反馈幂等；状态文件与事件序列不一致时暂停调度；显示表过期不污染 JSON。Skill 格式、文件链接、章节锚点、代码围栏和 git diff --check 均通过。未修改业务工具，不重复其单元测试；尚未实测并发状态存储实现。

保留原有未提交修改，本次不提交、不推送、不覆盖已安装版本。
