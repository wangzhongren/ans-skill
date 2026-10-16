---
id: boundary-yaml-change
type: change
title: 为边界文档增加同名 YAML 副本规范
created: "2026-10-16"
updated: "2026-10-16"
timezone: Asia/Shanghai
status: verified
related: [boundary-yaml-feature, boundary-yaml-design, boundary-yaml-validation]
events:
  - date: "2026-10-16"
    kind: created
    summary: 记录边界 YAML 副本格式及技能入口改动
  - date: "2026-10-16"
    kind: implemented
    summary: 增加集中规则、初始化说明和内置参考副本
  - date: "2026-10-16"
    kind: verified
    summary: 五组边界内容逐项一致；十个失配例被拒绝，同步更新正例通过
---

# 为边界文档增加同名 YAML 副本规范

客户要求边界文档同时交付同名 YAML，并由对应角色负责。本轮将其写成技能文档机制：每个边界 Markdown 旁有一个同 basename 的 YAML 文件，Markdown 仍是唯一维护和授权来源；副本不能改变路径或条件。本轮文档基于 `main` 的 Git `9cbd26b`，已存在的 Governance 准备改动作为受保护输入。

具体改动如下：

| 文档 | 修改前 | 修改后 |
| --- | --- | --- |
| `references/module-boundary.md` | 只规定 Markdown Section 1 表格格式和默认只读规则 | 集中规定同目录同名副本、`source`、逐行 `type/path/purpose`、可选真实 `condition` 与原文 `notes` 结构；明确不扩权、失配处理及现有工具限制 |
| `references/role-card.md` | 必读项仅指出边界 Markdown Section 1 | 明确 Markdown 是唯一授权源，同名 YAML 仅为同步副本 |
| `references/bootstrap-workflow.md` | 新项目或既有项目只建立边界 Markdown | 两种建卡流程都要求 Governance 同次交付 Markdown 与同名 YAML |
| `references/built-in-boundary.md` | 只有内置 Governance Markdown 参考 | 加入相邻 YAML 同步副本链接，并指向集中格式规则 |
| `references/built-in-boundary.yaml` | 尚无 YAML 参考副本 | 新增与内置边界表和表外约束一致的样例副本，保留原行类型、路径和用途 |
| `SKILL.md` | 只说明边界 Markdown Section 1 授权 | 在入口与内置角色路由简短说明 YAML 副本无独立权限 |
| `SKILL.zh.md` | 中文说明以 `boundary.md` 为准但未提副本关系 | 说明 Section 1 是唯一授权源，同名 YAML 仅同步 |
| `README.md` | 文件导航只有 `boundary.md` | 文件表增加 `boundary.yaml`，说明其不单独授权及当前执行仍按 Markdown |
| `角色卡/技能规范/feature-map.md` | 没有边界双格式功能入口 | 增加本功能导航，状态标为已验证并写明文档检查范围 |
| `角色卡/技能规范/docs/feature/boundary-yaml.md` | 尚无当前功能说明 | 新增用途、成功/失配/非边界文件分支、Mermaid 与方案/变更/测试历史 |

规范只覆盖真正的边界文件，不为所有 Markdown 文档生成 YAML。格式没有新增 schema version、权限配置、哈希体系、JSON 数据库或导出 CLI。治理角色负责实际角色边界对；本角色只负责技能规范与内置参考样例，未写任何实际角色 `boundary.md`、YAML 或本地 Governance 覆盖。`task_ops` 仍读取 Markdown，未更改工具、配置、依赖或测试源码。

本轮五组边界副本（68条目、15项 notes）逐项一致，十个失配负例均被拒绝，同步更新正例通过；详见[独立测试报告](../../../测试/docs/change/2026-10-16_change_boundary-yaml-validation.md)。检查使用 Ruby safe_load，官方 `quick_validate.py` 因环境缺少 PyYAML 未运行。没有验证 `task_ops` 解析 YAML、CLI 组级权限或文件系统拦截行为。当前流程见[边界文档的同名 YAML 副本](../feature/boundary-yaml.md)，客户确认和评审范围见[本轮方案](../../../项目管理/docs/design/2026-10-16_design_boundary-yaml.md)。
