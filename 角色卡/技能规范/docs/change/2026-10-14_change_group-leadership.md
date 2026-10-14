---
id: group-leadership-change
type: change
title: 增加组长协调与工作量评估规则
created: "2026-10-14"
updated: "2026-10-14"
timezone: Asia/Shanghai
status: verified
related: [role-groups-feature, group-leadership-design, group-leadership-validation]
events:
  - date: "2026-10-14"
    kind: created
    summary: 记录本轮组长职责、两级调度与负载评估变更
  - date: "2026-10-14"
    kind: implemented
    summary: 更新角色模板、组内会议、派发、汇报和当前功能说明
  - date: "2026-10-14"
    kind: verified
    summary: 文档一致性核对和三项独立只读情境判断通过
---

# 增加组长协调与工作量评估规则

用户已确认单角色组默认由该角色担任组长，多角色组由组长组织会议、组内安排和汇报；项目管理接到新需求时评估工作量，必要时提议增员。组长仍是原来的业务角色，权限继续按各角色自己的边界控制。

本轮从上轮未提交工作树和候选摘要 `33655e2c5832b8a1b9d58fb0665d8bd613b4cb521ad0c1a76a464a93e1b56960` 接续。上轮方案、变更和测试报告保留原样；上轮结果只覆盖角色平级、组别字段和逐角色写入范围，不验证本轮组长职责。本轮文档一致性核对和三项独立只读情境判断通过。

具体改动如下：

| 文档 | 修改前 | 修改后 |
| --- | --- | --- |
| `references/group-leadership.md` | 没有组长与组级协作规范 | 新增组员计数、单角色默认组长、增员保留原组长、权限授权、会议、两级调度、负载评估、增员提案、token 和汇报规则 |
| `references/role-card.md` | 模板只有组别字段，执行规则要求项目调度角色独自派发 | 增加 `groupDuty` 普通 Markdown 字段；明确组长是既有角色的额外职责，并允许其在 PM 逐角色授权预约后启动指定组员 |
| `references/project-role.md` | 项目管理统筹任务但未要求评估各组当前负载；项目管理独自主持全部会议 | 要求对新需求检查受影响组的任务、人手、依赖与阻塞，听组长反馈；按现有有效授权决定是否需要另请客户；项目/跨组会议仍由 PM 主持，组内会议可由组长主持 |
| `references/bootstrap-workflow.md` | 建卡流程只有组别字段；流程仅由 PM 调度角色 | 项目角色卡同时记录组内职责；按已接受角色定义而非运行上下文计算成员；明确组长归属、增员授权核对及 PM 全局安排与组长组内执行 |
| `references/module-boundary.md` | 说明组别不合并边界 | 同时说明 `groupDuty` 不扩大任何角色 Section 1 范围 |
| `references/test-role.md` | 测试角色流程未处理组长兼任 | 测试角色可填写组长职责并组织本组任务，同时保留自己的独立测试、报告与原始证据，不得改写测试失败或报告 |
| `references/scheduler.md` | 项目调度角色独自启动所有执行代理 | PM 仍控制全局计划、授权、预约、`task_ops` 与阶段释放；组长只启动已授权预约的本组成员 |
| `references/meeting.md` | PM 是所有会议唯一主持人和纪要写入者 | PM 主持项目/跨组会议，组长主持本组会议；实际主持人仅能在自己已授权的 `docs/meetings/` 写纪要 |
| `references/task-operations.md` | 旧指南说明项目管理按具体 `roleId` 授权、预约并启动交接，未说明组长接续启动 | PM/可信端保留 coordinatorToken 并按具体 `roleId` 授权预约；之后组长可启动指定上下文，worker token 只给目标执行者，PM 保留全局记录和验证 |
| `references/coordination.md` | 所有工作报告直接回项目管理，未描述组内汇总 | 组员将原始进展和证据交组长转报；PM 仍单写全局 task 记录，组长不改报告或记录 |
| `references/built-in-assembly.md` | 装配角色不得安排其他角色 | 装配角色承担组长职责时可组织获准的本组阶段；仍无 coordinator 凭证或他组调度权 |
| `SKILL.md` | 唯一派发规则只写项目调度角色 | 入口和路由说明 PM 的全局职责及组长的有限组内职责，维持每个上下文绑定一个角色 |
| `SKILL.zh.md` | 只说明项目管理负责跨角色安排 | 简短增加组长职责、独立上下文和逐角色预约要求 |
| `README.md` | 无组内职责字段示例；只写 PM 启动所有工作上下文 | 示例增加“组内职责：组长”；介绍 PM 评估负载及组长安排已获准组内任务 |
| `角色卡/技能规范/feature-map.md` | 功能状态反映上轮组别验证完成 | 反映本轮组长规则候选待独立检查 |
| `角色卡/技能规范/docs/feature/role-groups.md` | 当前流程只说明角色平级、组别和各自权限 | 扩展当前流程与 Mermaid，覆盖组长确定、工作量评估、增员授权、会议、两级调度、未获准待办及原始证据汇报；保留上轮验证历史，注明其不覆盖本轮 |

普通组员不调度同事；组长不模拟他人、不改组员文件、不继承他人边界。组内没有 Model、公开契约、私有 common 或 `common/shared/` 共享写权限。成员按已接受的角色定义计算，重复启动相同 `roleId` 不增加组员。新角色提案先核对现有有效客户授权或明确批准配置的覆盖范围，未覆盖时才请求客户授权，之后由 Governance 建卡和边界。

文档一致性核对和三项独立只读情境判断通过，详见[测试报告](../../../测试/docs/change/2026-10-14_change_group-leadership-validation.md)。官方 `quick_validate.py` 因缺少 PyYAML 未能运行；Ruby YAML 与文档检查通过。本轮未验证组长 CLI 行为、真实组员启动、实际会议或运行时权限防护。当前功能说明见[平级角色与组内协作](../feature/role-groups.md)，方案见[项目管理方案](../../../项目管理/docs/design/2026-10-14_design_group-leadership.md)。
