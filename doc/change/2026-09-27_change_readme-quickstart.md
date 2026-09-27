---
id: readme-quickstart-change
type: change
title: README 改为从安装到手动同步的入门说明
created: "2026-09-27"
updated: "2026-09-27"
timezone: Asia/Shanghai
status: verified
related:
  - manual-versioned-sync-feature
events:
  - date: "2026-09-27"
    kind: created
    summary: 记录 README 混用旧定时同步和新版手动同步、篇幅过长的问题
  - date: "2026-09-27"
    kind: implemented
    summary: 重写根 README，保留两种安装方式，突出角色工作流和手动同步命令
  - date: "2026-09-27"
    kind: verified
    summary: 两个仓库的 README 链接、命令和空白检查通过，差异仅为安装地址与许可证
---

# README 入门路径

原根 README 同时放安装、角色权限、五层结构、Docker 部署、旧同步器、任务网关和测试回放，读者需要跨越许多段才能找到当前的同步命令。它还把旧版后台上传和新版手动同步放在同一条使用路径中。

现在根 README 依次说明“技能做什么 → 怎么安装 → 在项目里怎么用 → 本地 Dashboard → 可选的手动云端同步 → 测试与深入文档”。服务器部署、历史设计查询与冲突处理细节留在 `dashboard/README.md`。GitLab 版安装命令指向内部仓库；GitHub 版指向公开仓库并保留 Apache-2.0 许可证链接。没有修改同步器代码、角色授权或业务项目。

验证于 2026-09-27：核对 GitLab/GitHub 两个安装地址、公开版许可证、全部相对链接与当前 CLI 参数；两份 README 分别为 85/87 行，公开版仅在安装地址和许可证上不同；Markdown 空白检查及两个仓库的 `git diff --check` 均通过。只改文档，未重复运行代码测试或启动业务程序。
