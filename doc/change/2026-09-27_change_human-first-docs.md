---
id: human-first-docs-change
type: change
title: 四类文档各回答一个具体问题
created: "2026-09-27"
updated: "2026-09-27"
timezone: Asia/Shanghai
status: verified
related: []
events:
  - date: "2026-09-27"
    kind: created
    summary: 用户指出文档规则过于像公文，要求按文档类型讲清写作重点
  - date: "2026-09-27"
    kind: implemented
    summary: 重写共同规则，并分别说明设计、新增、修改和修复文档怎么写
  - date: "2026-09-27"
    kind: verified
    summary: 两个仓库的技能入口与四篇写法说明均可互相导航，链接和空白检查通过
---

# 文档先让人看懂

以前的文档规则把目录、日期、状态和验证字段放得很靠前。AI 容易照着这些字段写“背景、范围、实施、验收”的公文，却没有先解释功能到底做什么。

现在四类文档各回答一个问题：[设计](../../references/documentation-design.md)讲为什么这样做，[新增](../../references/documentation-feature.md)讲怎么用，[修改](../../references/documentation-change.md)讲前后差别，[修复](../../references/documentation-fix.md)讲问题与解法。共同的[文档规则](../../references/documentation.md)只保留位置、日期和时间线所需的简短元数据；正文从具体场景开始，详细测试日志仍放任务记录。

已有日期文档不因此批量改写。下一次写文档时按读者的问题选相应说明，能用短例子讲清楚就不用堆层次和文件清单。2026-09-27 已检查两个仓库各 11 个相关文件的链接和空白，`git diff --check` 通过；没有改动测试或同步代码，因此未重跑业务测试。
