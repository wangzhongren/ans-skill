---
id: role-feature-docs
type: change
title: 用角色现有 docs 保存功能流程，并链接设计修改修复历史
created: "2026-09-30"
updated: "2026-09-30"
timezone: Asia/Shanghai
status: verified
related: [role-common-and-testing, role-maintainer-stance]
events:
  - date: "2026-09-30"
    kind: created
    summary: 按用户确认，统一功能文档、导航和双向历史链接，取消默认架构 JSON 维护
  - date: "2026-09-30"
    kind: verified
    summary: 核对目录命名、规则一致性、Markdown 链接和 YAML；无程序改动
---

# 从一个功能文件看懂用途、流程和变化历史

以前角色根目录的 `features/` 解释当前功能，角色 `docs/feature/` 又保存新增记录，还要求维护架构 JSON。想了解一个功能，要在几处来回查。

现在直接沿用角色已有的 `docs/`。一个功能只有一份稳定的 `docs/feature/<功能名>.md`：上面讲用途，下面用流程图和短句讲怎么做，末尾链接设计、修改和修复历史。角色根目录的 `feature-map.md` 负责导航，角色卡只链接它。

## 新的阅读顺序

1. 项目管理角色在自己的 `docs/architecture.md` 说明整体架构、角色职责和配合关系，链接各角色的功能导航。
2. 用户从角色的 `feature-map.md` 找到功能，打开 `docs/feature/<功能名>.md`，先了解用途和结果，再看真实步骤、判断分支、输入输出和跨角色交接。
3. 想知道为什么变成这样，就查看功能末尾的演变历史。表里记录日期、类型、状态、变化摘要，链接该角色 `docs/design/`、`docs/change/`、`docs/fix/` 中的详细文档。
4. 历史文档反向链接当前功能；跨角色设计由项目管理角色在自己的 docs 中维护，参与角色链接同一份记录。
5. 功能改变后，负责角色更新当前文字和图，追加历史链接并更新导航。待实施方案只出现在方案和历史中，不提前替换当前行为。

## 改在哪里

| 位置 | 修改 |
| --- | --- |
| [功能文档规则](../../references/feature-point.md) | 稳定文件名、功能导航、Mermaid 示例、历史表、双向链接和已有文档迁移说明 |
| [公共文档规则](../../references/documentation.md)及四类写法 | feature 只保留当前说明；design/change/fix 保留带日期的历史；规定当前与计划的区别 |
| [角色卡模板](../../references/role-card.md)、[边界](../../references/module-boundary.md)、[初始化](../../references/bootstrap-workflow.md) | 角色目录沿用 docs，使用 feature-map，去掉新建 features/ 和架构 JSON 的要求 |
| [项目管理角色](../../references/project-role.md)、[共享组件](../../references/shared-directories.md)、[功能描述](../../references/functional-description.md) | 整体架构归项目管理，功能流程归开发角色，公共组件与参与功能互相引用 |
| [技能入口](../../SKILL.md)、[中文说明](../../SKILL.zh.md)、[README](../../README.md) | 默认阅读路径改为架构 Markdown → 功能导航 → 当前功能 → 历史 |
| [旧 JSON 查看器说明](../../references/role-architecture-viewer.md)与旧 Dashboard/项目理解说明 | 退出默认流程，只保留客户明确需要的旧数据用法 |

新功能不再生成日期版 feature 文档；稳定功能文档可以先标为计划中，再按同版方案确认与实施授权继续。原有带日期的新增记录保留为历史链接，不自动改名或删除。

这次只改技能说明和模板。没有修改业务源码、现有项目角色卡或旧数据，也没有改造 HTML 程序。当前 JSON 绘图器仍只读 JSON，不能说它已经支持 Markdown；日常工作不再运行它或为它维护数据。若以后需要 HTML 展示，应从这些 Markdown 读取内容。

## 验证

已检查当前工作区的 26 份 Markdown 改动（包含上一轮尚未提交的角色工作立场说明），170 个本地链接及章节引用有效，代码围栏闭合，技能和变更记录的 YAML 头部解析通过，`git diff --check` 通过。已检查默认流程不再要求角色维护架构 JSON，模板统一沿用角色的 docs/。

这次没有程序改动，不重复运行代码测试。流程图示例经文字核对，本轮没有运行 Mermaid 渲染器检查视觉效果。真实项目的旧文档迁移和流程内容核验需要在对应项目的授权范围内完成。仓库发布与本地技能更新另按用户的明确指令执行。
