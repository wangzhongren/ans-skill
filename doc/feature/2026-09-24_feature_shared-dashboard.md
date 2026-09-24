---
id: shared-dashboard-feature
type: feature
title: 独立多项目 Dashboard 与本地展示快照同步
created: "2026-09-24"
updated: "2026-09-24"
timezone: Asia/Shanghai
status: implemented
related:
  - role-dashboard-feature
events:
  - date: "2026-09-24"
    kind: created
    summary: 将通用页面与后端抽取到 dashboard 目录，保留旧脚本入口
  - date: "2026-09-24"
    kind: implemented
    summary: 增加内置账号、项目授权、项目 Key、管理页与按项目同步的展示快照
---

# 独立多项目 Dashboard

1. **部署**：`dashboard/` 可单独复制到服务器，一份服务通过 `/p/<project-id>/` 提供多个项目视图。管理员在 `/manage` 创建项目、用户、授权和项目 Key。部署配置见 [README](../../dashboard/README.md)。
2. **数据**：业务项目本地运行同步器。它读取角色卡摘要、边界路径、共享项目理解库与协调记录，将页面需要的投影发给服务器。服务端无需业务仓库、完整角色文档或项目 SQLite 文件。同步的具体项目理解文字与字段对获授权用户可见。
3. **边界**：网页会话使用账号密码；每个项目 Key 只能同步其所属项目。管理员可撤销 Key 和停用用户。旧的 `scripts/serve_dashboard.py` 与 `scripts/context_store.py` 保留兼容入口；本地单项目模式继续直接读取本机文件。
4. **验证**：新增存储和 HTTP 测试，检查项目隔离、用户授权、管理写入的 CSRF 校验、Key 错配拒绝、撤销后失效及同步时的文档/绝对路径剔除。
