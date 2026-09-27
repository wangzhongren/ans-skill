---
id: remove-role-sync-preflight-change
type: change
title: 角色启动不再检查云端同步服务
created: "2026-09-27"
updated: "2026-09-27"
timezone: Asia/Shanghai
status: verified
related:
  - manual-versioned-sync-feature
events:
  - date: "2026-09-27"
    kind: created
    summary: 用户决定云端同步由自己手动触发，角色卡不再需要检查同步进程
  - date: "2026-09-27"
    kind: implemented
    summary: 从角色激活和模板中移除同步预检，保留按需使用的状态命令
  - date: "2026-09-27"
    kind: verified
    summary: 完整测试 121 项通过，检查角色模板和文档不再要求同步预检
---

# 角色启动不再检查同步服务

以前每张角色卡在首次修改前都要求运行 `scripts/check_dashboard_sync.py`，项目角色与技能入口还会把已配置但未运行的同步进程当成需要恢复的状态。现在同步默认由用户手动发起；进程不运行是正常的，不应打断本地开发。

本次从 `SKILL.md`、`SKILL.zh.md`、`references/role-card.md`、`references/project-role.md` 和 `references/bootstrap-workflow.md` 移除了角色激活时的必做同步检查，更新了 Dashboard 参考、根 README 和入门总览。`scripts/check_dashboard_sync.py` 仍是只读兼容命令；用户主动想看待上传数量或冲突时可运行 `python3 -m dashboard.versioned_sync --root <项目目录> --status`。这次没有修改角色边界、任务授权或业务源码。

验证于 2026-09-27：搜索技能入口和角色模板，已无“首次修改前必须运行同步预检”的规则；`python3 -m unittest discover -s scripts/tests -q` **121 项通过**，Python/JavaScript 语法检查、文档链接与元数据检查、`git diff --check` 通过。`skill-creator` 自带的快速校验器因当前运行环境缺少 PyYAML 未能启动；改用上面的元数据、链接和语法检查，不把它写成已通过。
