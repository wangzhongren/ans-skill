---
id: local-dashboard-config-feature
type: feature
title: 本机按项目显式配置 Dashboard 连接
created: "2026-09-25"
updated: "2026-09-25"
timezone: Asia/Shanghai
status: verified
related:
  - local-project-id-first-change
events:
  - date: "2026-09-25"
    kind: added
    summary: 每个项目在用户配置目录保存项目 ID、业务目录、服务器地址和 Key
  - date: "2026-09-25"
    kind: verified
    summary: 私有文件权限、更新保护、同步和角色通信共用配置的回归测试通过
---

# 本地显式配置

`python3 -m dashboard.local_config init` 交互读取项目 Key，并将配置写入用户目录的 `ans-dashboard/projects/<project-id>.json`。文件仅当前用户可读写；不会写入技能目录或业务仓库。`show` 只显示项目 ID、业务目录和服务器地址，不展示 Key；更新已有配置须显式加 `--replace`。

同步器和角色通信 CLI 用 `--project-id` 读取同一份配置，不再要求每次传服务器地址或粘贴 Key。原有环境变量和显式参数保留，方便临时运行和机密管理器接入；环境变量中的 Key 优先。
