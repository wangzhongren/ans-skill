---
id: role-channel-feature
type: feature
title: 多角色消息与权限申请收件箱
created: "2026-09-25"
updated: "2026-09-25"
timezone: Asia/Shanghai
status: verified
related:
  - shared-dashboard-feature
  - task-operations-feature
events:
  - date: "2026-09-25"
    kind: implemented
    summary: 每项目 SQLite 增加角色消息、精确权限申请、管理员决定和审计事件
  - date: "2026-09-25"
    kind: verified
    summary: 单项目 Key 多角色通信、版本与写入范围校验、权限决定及浏览器收件箱测试通过
---

# 多角色协作收件箱

共享 Dashboard 使用每项目同一个 Key。各角色在自己的执行上下文中用该 Key 自行发送任务消息和权限申请，并声明自己的角色 ID；Key 可读取该项目收件箱，但不能审批。管理员可在网页管理项目 Key、给角色发消息、查看所有申请和审计记录，并对当前任务版本的申请作一次批准或拒绝决定。普通项目用户只能查看。

权限申请固定任务、节点、声明的角色、worker、操作、精确写入路径、计划版本、下一批次及需求/设计/边界版本；申请和批准时均与最新同步快照对比。相同客户端 ID 的同内容重试幂等，改内容会被拒绝。消息、申请、决定与审计按项目存于 `projects/<project-id>.sqlite3`，共享元数据库只保存项目 Key 哈希。因为 Key 在项目内共用，服务器不能独立证明声明角色的身份；本地角色/任务门禁仍负责严格切换与执行范围。

Dashboard 审批是一条协作决定，一小时后显示过期；它不自动生成 `task_ops` 同意文件、不放行本地写入、不启动代理，也不把任务标为已验收。现有客户同意或预授权配置门禁保持不变。接入命令和 JSON 格式见 [Dashboard README](../../dashboard/README.md#role-channel)。
