---
id: dashboard-auto-update-feature
type: feature
title: 服务器定时跟随 GitLab 更新 Dashboard
created: "2026-09-25"
updated: "2026-09-25"
timezone: Asia/Shanghai
status: verified
related:
  - shared-dashboard-feature
events:
  - date: "2026-09-25"
    kind: implemented
    summary: 增加只读拉取、快进校验、健康检查与代码/镜像回退的 systemd 定时更新器
  - date: "2026-09-25"
    kind: verified
    summary: 临时 Git 仓库与模拟 Docker 验证无更新不重建、快进部署、脏工作区拒绝和失败回退
---

# Dashboard 自动更新

服务器端脚本 `dashboard/auto_update.sh` 只对干净的 `main` Git 克隆执行 `origin/main` 快进更新；没有新提交时不重建。新提交使用 Compose 构建并等待健康检查，失败时尝试恢复旧代码和镜像并以非零状态记录失败。`dashboard/install_auto_update.sh` 将更新脚本及 systemd 服务和定时器安装到服务器；不会由 Dashboard 网页触发 shell 命令。

现有手工复制的部署需先迁移到 GitLab 克隆，复制忽略的 `.env`，并复用固定 Compose 项目名对应的数据卷。Deploy Key 应为只读，主分支应受控。数据库状态不属于 Git，自动代码回退不能回滚已执行的数据库迁移；具体升级和备份步骤见 [Dashboard README](../../dashboard/README.md)。
