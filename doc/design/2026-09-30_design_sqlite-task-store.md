---
id: sqlite-task-store
type: design
title: 已放弃：以 SQLite 作为项目任务记录
created: "2026-09-30"
updated: "2026-09-30"
timezone: Asia/Shanghai
status: blocked
related: [git-task-records, ans-project-role-plan]
events:
  - date: "2026-09-30"
    kind: created
    summary: 曾建议使用项目级 SQLite 保存任务状态
  - date: "2026-09-30"
    kind: blocked
    summary: 用户指出 SQLite 文件无法随着 Git 项目可靠合并，停止采用该方案
---

# 已放弃：项目级 SQLite 任务库

最初想把任务计划、状态、事件和检查结果集中写入 `.ans/tasks.sqlite3`，减少新项目里的 JSON 文件。

问题是这个数据库会成为项目任务历史的唯一来源，而项目需要跟着 Git 在不同机器和分支之间同步。SQLite 文件是二进制，Git 能传输它，却不能像文本那样核对和合并不同分支的修改。只在本地保留数据库，换机器后又读不到完整任务历史。

因此不实施这个设计。后续方案改为[随项目同步的任务记录](2026-09-30_design_git-task-records.md)：每个任务一份受 Git 管理的文本文件，执行工具按可验证的结构读取。这个记录只说明放弃原因，不是执行授权；原来的 `task_ops` 代码目前没有修改。
