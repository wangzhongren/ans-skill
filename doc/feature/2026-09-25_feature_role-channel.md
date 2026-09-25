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
    summary: 角色凭证隔离、版本与写入范围校验、权限决定及浏览器收件箱测试通过
---

# 多角色协作收件箱

共享 Dashboard 增加独立角色凭证，绑定项目和已同步的角色；项目 Key 仍只负责展示快照。角色凭证可向当前项目的其他角色发送任务消息、提交权限申请，并读取自己的消息与申请。管理员可在网页管理凭证、给角色发消息、查看所有申请和审计记录，并对当前任务版本的申请作一次批准或拒绝决定。普通项目用户只能查看。

权限申请固定任务、节点、角色、worker、操作、精确写入路径、计划版本、下一批次及需求/设计/边界版本；申请和批准时均与最新同步快照对比。相同客户端 ID 的同内容重试幂等，改内容会被拒绝。消息、申请、决定与审计按项目存于 `projects/<project-id>.sqlite3`，角色凭证只在共享元数据库中存哈希。

Dashboard 审批是一条协作决定，一小时后显示过期；它不自动生成 `task_ops` 同意文件、不放行本地写入、不启动代理，也不把任务标为已验收。现有客户同意或预授权配置门禁保持不变。接入命令和 JSON 格式见 [Dashboard README](../../dashboard/README.md#role-channel)。
