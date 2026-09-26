---
id: plain-language-skill-change
type: change
title: 用入门者能理解的语言说明技能和流程
created: "2026-09-26"
updated: "2026-09-26"
timezone: Asia/Shanghai
status: verified
related:
  - flow-purpose-branch-graph-feature
events:
  - date: "2026-09-26"
    kind: created
    summary: 用户指出技能说明堆术语、流程介绍没有说明具体用途
  - date: "2026-09-26"
    kind: implemented
    summary: 重写中文入门说明，简化主规则和项目理解写法，并改进流程页面文字
  - date: "2026-09-26"
    kind: verified
    summary: 入口与新文档链接、代码示例和浏览器流程用语检查通过
---

# 把话说清楚

中文说明改为从“谁能改文件、代码怎么调用、改完怎么验证”开始，每个概念配具体文件和例子。主规则保留原有权限、依赖和测试要求，但减少抽象词。项目理解说明要求流程先回答“做什么、成功后怎样、失败时怎样”，把按钮、前置条件与 `if/else` 放到各自位置；不再把“从入口到结果”当作流程用途。

这次只是改说明方式，没有放宽角色边界、五层调用或验证门槛。技术字段如 `role_id`、`boundary.md`、`flow.intent` 首次出现时解释其用途，必要时仍保留原名，以便读者照命令和代码查到它们。

验证：`SKILL.md` 和 `SKILL.zh.md` 保留技能名称与有效 frontmatter；入口和新文档的本地链接、代码围栏均通过检查。浏览器预览核对了流程目的、成功/失败结果、触发条件、判断和异常节点的实际显示。五层权限、角色边界和测试要求未放宽。
