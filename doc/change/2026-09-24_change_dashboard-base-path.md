---
id: dashboard-base-path-change
type: change
title: Dashboard 支持部署到 URL 路径前缀
created: "2026-09-24"
updated: "2026-09-24"
timezone: Asia/Shanghai
status: verified
related:
  - shared-dashboard-feature
events:
  - date: "2026-09-24"
    kind: changed
    summary: 页面、登录、管理、项目 API 与同步请求统一支持可选路径前缀
  - date: "2026-09-24"
    kind: verified
    summary: 多段路径 HTTP 测试及浏览器登录、切换项目、管理页和退出验证通过
---

# Dashboard 路径前缀

服务端的 `--base-path` 接收 `/path` 或多段路径，默认空值维持根路径部署。HTML 静态资源与链接按同一前缀生成；前端请求和跳转、服务端路由及同步端 `--server-url` 使用相同路径。Docker Compose 从 `ANS_DASHBOARD_BASE_PATH` 传入该配置。

反向代理必须保留前缀，不能把 `/path/` 重写成 `/`。前缀之外的路由返回 404；项目登录、权限和 Key 校验继续按原规则执行。具体配置见 [Dashboard README](../../dashboard/README.md)。
