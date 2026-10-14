---
id: role-groups-change
type: change
title: 增加平级角色组别规范
created: "2026-10-14"
updated: "2026-10-14"
timezone: Asia/Shanghai
status: verified
related: [role-groups-feature, role-groups-design, role-groups-validation]
events:
  - date: "2026-10-14"
    kind: implemented
    summary: 为技能规范、模板和建卡派发流程增加描述性组别规则
  - date: "2026-10-14"
    kind: verified
    summary: 文档一致性与现有逐角色范围检查通过
---

# 增加平级角色组别规范

用户已确认角色保持平级、角色卡增加组别、权限继续按每个角色自己的边界控制。本次将该约定写入技能文档，明确既有角色调整组别只维护原卡，新增角色才建立独立角色卡和边界。本轮文档以 Git 基线 `54ff933` 为起点。独立检查确认文档一致性与现有逐角色范围检查通过。

具体修改如下：

| 文档 | 修改前 | 修改后 |
| --- | --- | --- |
| `references/role-card.md` | 角色卡识别角色和边界，没有通用组别字段 | 新增 `group` / `组别` 模板字段及集中规则：角色平级；已有角色调整组别只维护原卡，新角色由 Governance 建立独立卡和边界；旧卡缺字段不阻断已有授权任务 |
| `references/project-role.md` | 项目管理角色卡要求工作立场，但未要求组别 | 要求项目管理卡也填写描述性组别，且不因此取得额外权限 |
| `references/test-role.md` | 固定测试卡说明工作立场和测试职责 | 明确测试角色卡填写组别，角色仍平级、权限仍按自身边界 |
| `references/bootstrap-workflow.md` | 能力、项目管理、测试角色的建卡步骤没有统一字段要求 | 新建各角色卡均要求组别；既有角色调整组别不复制角色或边界，确需新角色时由 Governance 建立独立卡和边界 |
| `references/module-boundary.md` | 说明 Section 1 是唯一写入白名单 | 补充角色卡组别不会合并或扩大各自写入范围 |
| `references/scheduler.md` | 调度写明角色卡和独立权限，但没有说明如何处理组别 | 明确派发到具体 `roleId`；组别不是工具授权字段，工具继续按独立边界处理 |
| `SKILL.md` | 技能入口没有说明组别是描述性字段 | 入口简要说明组别字段、角色平级、各自边界权限，并链接集中规范 |
| `SKILL.zh.md` | 中文入口没有说明组别字段的实际边界 | 增加对应中文简要说明，链接集中规范 |
| `README.md` | 项目说明没有角色组别规则 | 增加简短组别说明和角色卡示例，并链接模板 |
| `角色卡/技能规范/feature-map.md` | 只导航项目法案与 memo 功能 | 增加平级角色组别功能入口 |
| `角色卡/技能规范/docs/feature/role-groups.md` | 尚无当前功能说明 | 新增用途、完整使用分支、Mermaid 流程和方案/变更/测试历史链接 |

项目管理和测试建卡分别在 `project-role.md`、`test-role.md` 有明确落点，初始化中的新项目和既有项目路径也要求字段。本机制只记录协作标签。组别不是工具授权字段；工具仍按具体 `roleId` 和独立边界运行。

本轮文档一致性与现有逐角色范围检查通过；详见[测试报告](../../../测试/docs/change/2026-10-14_change_role-groups-validation.md)。报告记录文档比对、链接与元数据检查，以及现有 `roles_valid` 按具体角色和 Section 1 检查写入范围的结果。官方 `quick_validate.py` 因缺少 PyYAML 未能运行；Ruby YAML 与文档检查通过。报告没有验证组别相关的程序执行行为或真实 AI 权限服从。当前功能说明见[平级角色组别](../feature/role-groups.md)，确认方案见[项目管理方案](../../../项目管理/docs/design/2026-10-14_design_role-groups.md)。
