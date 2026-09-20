---
id: optional-code-atlas-change
type: change
title: 代码图谱退出默认开发和验收流程
created: "2026-09-20"
updated: "2026-09-20"
timezone: Asia/Shanghai
status: verified
related: []
events:
  - date: "2026-09-20"
    kind: implemented
    summary: 移除默认扫描、图谱加载和强制快照验收，保留明确请求时使用的工具
  - date: "2026-09-20"
    kind: verified
    summary: 检查默认入口、角色模板、调度与验收规则，不再依赖代码图谱
---

# 代码图谱默认关闭

1. 主入口和角色卡不再要求加载图谱参考，调查通过定向源码搜索、调用堆栈与对接契约完成。
2. 删除角色完成阶段的自动扫描、快照同步和打开步骤，删除验收对代码图谱新鲜度的要求。
3. 调度保留阶段任务依赖，Dashboard 保留协同状态读取；两者无需代码图谱。现有图谱工具与文件未删除，仅在用户明确请求时使用。
4. README 和中英文主文件已同步。按需角色视图是后续讨论方向，本次没有实现或启用每角色自动生成。

涉及 SKILL.md、SKILL.zh.md、references/role-card.md、evidence.md、scheduler.md、project-role.md、code-atlas.md 和 README.md。格式、链接和默认规则检索检查通过；未改动可执行工具，不运行图谱扫描或重复工具回归。修改尚未提交或同步已安装版本。
