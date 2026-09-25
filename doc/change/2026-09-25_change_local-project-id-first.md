---
id: local-project-id-first-change
type: change
title: 本地项目 ID 先行登记云端项目
created: "2026-09-25"
updated: "2026-09-25"
timezone: Asia/Shanghai
status: verified
related:
  - key-creation-feedback-fix
events:
  - date: "2026-09-25"
    kind: changed
    summary: 管理员用本地项目 ID 创建 Key 时自动登记云端项目
  - date: "2026-09-25"
    kind: verified
    summary: 新项目创建 Key、首次同步、项目隔离及已有标题保留的回归测试通过
---

# 本地项目 ID 先行

业务项目先在本地确定稳定的项目 ID。管理员在 Dashboard 管理页输入该 ID 创建项目 Key；若服务器尚无对应项目，后端同时登记项目并创建空的项目 SQLite，页面显示“待同步”。本地同步器使用同一 ID 和 Key 发送展示快照后，项目名称、角色、任务与项目理解才出现在云端。首次同步可把占位名称更新为本地项目名称，但不会覆盖此前手工设置的名称。

后台只接受小写字母、数字和中划线组成的 ID。未持有有效 Key 的同步请求仍不能自行创建项目。已有项目可继续签发新 Key；不必迁移原有项目数据或 Key。
