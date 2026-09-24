---
id: role-project-context-feature
type: feature
title: 角色项目理解目录与 Dashboard 联动
created: "2026-09-24"
updated: "2026-09-24"
timezone: Asia/Shanghai
status: verified
related:
  - role-dashboard-feature
events:
  - date: "2026-09-24"
    kind: created
    summary: 定义每个角色按流程、定义、事件、接口和数据维护项目理解
  - date: "2026-09-24"
    kind: implemented
    summary: 增加角色项目理解入口和 Dashboard 逐层查看
  - date: "2026-09-24"
    kind: changed
    summary: 改为项目级单一 SQLite，按角色筛选并提供 AI 增删改查入口
  - date: "2026-09-24"
    kind: changed
    summary: 分类增加独立汇总，流程步骤和主题直接展开关联事件、数据与接口
  - date: "2026-09-24"
    kind: verified
    summary: 66 项测试、技能校验、页面脚本检查和浏览器流程内联演示通过
---

# 角色项目理解目录

项目根目录新增按需创建的 `project-context/context.sqlite3`。所有角色共用一套结构，以 `role_id` 区分总览与五类主题：流程、定义、事件、接口、数据。只有角色的已接受边界 Section 1 覆盖其逻辑行范围时，归属角色才能通过 CLI 修改；正式接口、数据结构与权限仍以已有契约、源码和边界为准。跨角色变更由项目角色协调各归属角色更新，不生成重复的全项目说明。

Dashboard 用只读连接读取实际项目数据库，增加独立的“项目理解”视图。点击角色卡进入总览，流程步骤、分类和主题摘要以卡片呈现；流程步骤与流程主题直接展开关联的事件、数据、接口记录。五类汇总分别可打开，逐层进入主题和详情，使用面包屑返回。未建立总览时明确提示。写入工具要求角色匹配、记录版本匹配，并将删除保留为可恢复标记。它不替代客户授权或 OS 级身份验证。

实现位置：[项目理解规范](../../references/project-context.md)、[SQLite CRUD 工具](../../scripts/context_store.py)、[Dashboard 服务](../../scripts/serve_dashboard.py)、[Dashboard 页面](../../assets/role-dashboard/index.html)、[数据库测试](../../scripts/tests/test_context_store.py)与[Dashboard 测试](../../scripts/tests/test_dashboard.py)。

验证：技能结构校验通过；66 项测试通过，覆盖单库角色隔离、分类独立汇总、同角色主题关联、跨角色关联拒绝、CRUD 版本冲突、可恢复删除、CLI 写入角色检查与 Dashboard 只读接口；页面脚本语法检查通过。浏览器在临时项目中验证了订单流程内直接显示接口、数据、事件的摘要和详情，也验证了事件的独立汇总页。该预览只使用临时数据，没有改动示例业务项目。
