---
id: skill-project-rules-memo
type: change
title: 增加项目工程法案与角色备忘录支持
created: "2026-10-10"
updated: "2026-10-10"
timezone: Asia/Shanghai
status: verified
related: [skill-project-rules-memo-feature, project-rules-memo-validation-result]
events:
  - date: "2026-10-10"
    kind: implemented
    summary: 编写法案与 memo 指南并接入技能工作流
  - date: "2026-10-10"
    kind: verification
    summary: 独立检查法案与 memo 指南的五种情境及文档链接、围栏；修正状态与规则身份要求，真实应用行为未测
  - date: "2026-10-10"
    kind: verification
    summary: 最终独立复核确认文档结构问题已关闭；链接、锚点、元数据和围栏检查通过
  - date: "2026-10-10"
    kind: implemented
    summary: README 增加法案与 memo 独立说明及本仓库实际角色分工
  - date: "2026-10-10"
    kind: verification
    summary: README 25 个本地链接均指向存在的目标，git diff --check 通过
---

# 增加项目工程法案与角色备忘录支持

用户需要技能明确指导项目如何维护共同工程约束，以及各独立角色如何记住下次工作有用的事实。新增 `references/project-rules.md` 与 `references/role-memo.md`，并把它们接入中英文入口、README、角色与项目管理模板、初始化、边界、文档、方案评审、测试、调度和治理变更记录。README 新增独立章节，说明全项目工程法案、各角色 memo 的读取与维护方式，以及 ANS 本轮实际角色和各自职责；现有安装命令和 GitLab 地址保留。

项目管理角色在自己的角色目录下维护唯一的 `docs/project-rules.md`，各角色引用同一实际路径。每条规则有稳定编号或名称，理由按需补充；同时说明范围、要求、正确做法和检查方式。精简 GUI `THREAD-01` 例子明确单纯加 `async` 不会把重计算移到后台。该例只在具体项目确认采用 GUI 主线程模型和相应约束后适用，不默认禁止所有项目的主线程工作。各角色只维护自己的简短 memo。初始化先建立项目管理角色与边界，随后才可整理法案；法案缺失不阻止启动。路径仍需进入已接受的边界，冲突由项目管理处理，不要求全项目迁移。

当前路径属于技能规范角色的已授权文档范围。相关行为说明见[项目法案与角色备忘录支持](../feature/project-rules-memo.md)。

**验证：**最终独立复核完成五种情境推演，并确认 35 份 Markdown、238 个本地链接与锚点、5 份元数据及代码围栏检查通过；详见[最终独立测试报告](../../../测试/docs/change/2026-10-10_change_project-rules-memo-validation.md)。本轮另补齐并检查本功能文档的 YAML 元数据。README 的 25 个本地链接均指向存在的目标，`git diff --check` 通过。此 change 状态 `verified` 仅表示规范文档和情境分析及文档链接检查通过；真实应用行为未测。没有在本轮重新运行 157 项程序测试，也没有验证 GUI、Worker/线程、资源生命周期或应用性能。
