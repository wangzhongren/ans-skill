---
id: dashboard-container-feature
type: feature
title: 共享 Dashboard 的 Docker Compose 部署
created: "2026-09-24"
updated: "2026-09-24"
timezone: Asia/Shanghai
status: implemented
related:
  - shared-dashboard-feature
events:
  - date: "2026-09-24"
    kind: created
    summary: 增加非 root 镜像、持久状态卷、回环端口映射与容器初始化说明
---

# Docker Compose 部署

1. `dashboard/Dockerfile` 只复制 Dashboard 运行文件，以非 root 用户启动；业务项目源码和状态不进入镜像。
2. `dashboard/compose.yaml` 挂载持久 `dashboard-state` 卷、以只读根文件系统运行，并将端口仅映射到宿主机 `127.0.0.1`，供 HTTPS 反向代理使用。
3. 服务器增加仅云端模式可用的 `--listen-host 0.0.0.0`。本地单项目模式仍只监听回环地址；容器监听所有容器接口时必须声明可信 Host，且不能启用不安全本地预览 Cookie。
4. 首次管理员通过临时 `docker compose run` 容器创建到同一状态卷。部署步骤见 [Dashboard README](../../dashboard/README.md)。
