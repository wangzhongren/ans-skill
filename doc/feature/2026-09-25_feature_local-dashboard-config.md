---
id: local-dashboard-config-feature
type: feature
title: 项目目录显式配置 Dashboard 连接
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
  - date: "2026-09-25"
    kind: changed
    summary: 配置移至业务项目根目录，并自动加入 Git 的本地排除规则
---

# 本地显式配置

`python3 -m dashboard.local_config init` 交互读取项目 Key，并将配置写入业务项目根目录的 `.ans-dashboard.local.json`。文件仅当前用户可读写；Git 项目会自动写入本地 `.git/info/exclude`，使它不进入提交。`show` 只显示项目 ID、业务目录和服务器地址，不展示 Key；更新已有配置须显式加 `--replace`。曾使用旧版用户目录配置的项目应重新初始化；旧文件不会自动删除。

同步器和角色通信 CLI 从 `--root` 指定的项目目录读取同一份配置；从项目根目录运行时可省略 `--root`。原有环境变量和显式参数保留，方便临时运行和机密管理器接入；环境变量中的 Key 优先。
