---
id: readme-architecture-first
type: change
title: README 按本地架构页面的使用流程重写
created: "2026-09-29"
updated: "2026-09-29"
timezone: Asia/Shanghai
status: verified
related: [role-architecture-viewer-design]
events:
  - date: "2026-09-29"
    kind: created
    summary: 重排 README，让安装、开发与本地绘图成为主线
  - date: "2026-09-29"
    kind: verified
    summary: 核对链接、目录、安装地址和绘图参数，文档格式检查通过
---

# README 按本地架构页面的使用流程重写

技能已经改为各角色维护 JSON、本地 HTML 看架构，但 README 仍像旧 Dashboard 的入口，还占用不少篇幅讲云端命令。第一次读的人容易以为必须部署服务、维护项目理解库才能开始开发。

现在开头先讲实际用途，再依次说明安装、开发流程、各类文件和生成架构页面。必要改动与选装的确认规则也写进开发步骤。每个角色维护自己的架构 JSON，正式契约与功能文档继续说明字段和用法；不另维护 content.json、context.sqlite3 等重复索引。

旧 Dashboard 和云端工具集中在可选部分，详细命令链接原指南。明确新的架构 HTML 尚未接入旧 Dashboard，避免把本地生成误读成已经云端同步。GitLab 和 GitHub 版保留各自安装地址，公开版保留 Apache-2.0 许可证说明。

这次只改 README 和本记录，没有改绘图程序、业务代码或数据库。已核对相对链接、实际目录、安装地址与绘图工具的帮助参数，Markdown 格式检查通过；只改说明，没有重复运行代码测试。
