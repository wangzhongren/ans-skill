# 技能规范角色备忘录

## 2026-10-10 — 已完成：项目法案与角色 memo 指南

- 状态：规范文档与五种情境推演已验证；最终报告确认 35 份 Markdown、238 个本地链接与锚点、5 份元数据及围栏检查通过。本功能文档新增的 YAML 元数据经本轮单独核验。GUI、线程与应用性能行为未测。见[最终独立测试报告](../测试/docs/change/2026-10-10_change_project-rules-memo-validation.md)。
- 依据：已确认方案 `doc/design/2026-10-10_design_project-plan-role-memo.md` 与本轮管理评审 `角色卡/项目管理/docs/design/2026-10-10_design_project-rules-memo-review.md`。
- 关键约定：唯一项目法案由项目管理角色在自身角色目录的 `docs/project-rules.md` 维护，其他角色引用同一实际路径；每条规则使用稳定编号或名称，理由按需补充。角色 memo 由各角色自己维护，仅记录少量有日期、有来源的工作线索。初始化不以法案先存在为条件。GUI `THREAD-01` 只是写法示例；单纯加 `async` 不会把重计算移到后台，且只有项目确认相应 GUI 模型和约束后才适用。
- 继续：本轮没有待处理的技能规范文档项。最终复核确认首轮发现的管理元数据及历史状态问题已关闭；它们作为报告中的修复历史保留。后续修改遵守本角色 `boundary.md`。具体规则见 [项目法案指南](../../references/project-rules.md) 和 [角色 memo 指南](../../references/role-memo.md)。

## 2026-10-10 — README 更新

- 状态：README 已补充独立的项目法案与 memo 说明、本仓库本轮实际角色分工及现有示例树中的 `memo.md`。法案由项目管理维护、全角色共读；每条规则说明范围、要求、正确做法和检查，只有项目确认后适用。
- 依据：本轮用户请求；实际角色与职责见 [项目管理架构说明](../项目管理/docs/architecture.md)，独立验证结果见[测试报告](../测试/docs/change/2026-10-10_change_project-rules-memo-validation.md)。
- 检查：README 的 25 个本地链接目标存在，`git diff --check` 通过；没有运行程序测试。本条不记录 GitHub/GitLab 发布或推送结果。
