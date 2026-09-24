---
id: dashboard-project-databases-change
type: change
title: Dashboard 项目快照改为每项目独立 SQLite
created: "2026-09-24"
updated: "2026-09-24"
timezone: Asia/Shanghai
status: verified
related:
  - shared-dashboard-feature
events:
  - date: "2026-09-24"
    kind: changed
    summary: 项目快照迁移到 projects/<project-id>.sqlite3；共享库保留账号与授权元数据
  - date: "2026-09-24"
    kind: verified
    summary: 旧版快照、管理员与项目 Key 迁移，以及双项目分库和权限测试通过
---

# 每项目独立 SQLite

服务器状态目录现在包含一份共享的 `dashboard.sqlite3`（账号、会话、项目登记、授权、Key、最近同步时间）和每项目一份 `projects/<project-id>.sqlite3`（该项目的展示快照与项目理解）。本地业务项目原有的 `project-context/context.sqlite3` 不上传。

升级旧版时，`CloudStore` 启动迁移旧 `projects` 表里的快照：先写入对应项目数据库，再清空旧字段；每项目写入与清空在一次 SQLite 附加数据库事务中完成。迁移可重复执行，未完成的项目保留旧记录。用户应在升级前停止服务并备份整个状态目录或卷。

项目 API 与页面链接不变。验证覆盖新项目双数据库隔离、旧共享库迁移、重启后的读取、未知项目拒绝和既有登录/Key 权限路径。
