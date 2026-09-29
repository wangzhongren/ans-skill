---
id: readme-architecture-first
type: change
title: README 说明角色优先的设计原因与本地使用流程
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
    summary: 核对论文原文、引用、目录、安装地址和绘图参数，文档格式检查通过
---

# README 说明角色优先的设计原因与本地使用流程

技能已经改为各角色维护 JSON、本地 HTML 看架构，但 README 仍像旧 Dashboard 的入口，还占用不少篇幅讲云端命令。第一次读的人容易以为必须部署服务、维护项目理解库才能开始开发。

现在先讲为什么采用这种设计，再解释角色与五层代码组织的关系，用工单与存储的例子说明一个角色可以跨多个技术层。明确角色是一份职责和权限定义，由 AI 执行并维护 JSON，不要求客户手工填写。之后说明安装、开发流程、各类文件和本地绘图。个人安装与项目子模块分别说明更新方式。

设计来源引用 Wang, Zhongren 于 2026-09-18 发布的 [Role-First Software Governance 预印本](https://zenodo.org/records/22824700)，DOI 为 10.5281/zenodo.22824700。已读取该记录元数据和所附 12 页 PDF；关于责任角色、按需跨模块阅读和由拥有者修改的说明依据原文第 3、4、7–10、22 节。引用题名采用 Zenodo 记录中的正式题名。

README 将论文启发与 ANS 的工程选择分开说明，没有把五层目录、客户确认流程或本地 JSON/HTML 当成论文规定，也没有把论文提出的潜在收益写成本项目已验证的性能结论。必要改动与选装仍需按已确认范围实施；不另维护 content.json、context.sqlite3 等重复索引。

旧 Dashboard 和云端工具集中在可选部分，详细命令链接原指南。明确新的架构 HTML 尚未接入旧 Dashboard，避免把本地生成误读成已经云端同步。GitLab 和 GitHub 版保留各自安装地址，公开版保留 Apache-2.0 许可证说明。

这次只改 README 和本记录，没有改绘图程序、业务代码或数据库。已核对相对链接、实际目录、安装地址与绘图工具的帮助参数，Markdown 格式检查通过；只改说明，没有重复运行代码测试。
