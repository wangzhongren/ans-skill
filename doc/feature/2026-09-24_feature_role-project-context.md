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
    kind: changed
    summary: 取消多级浏览，改为五类总览直达详情；流程记录输入输出和触发事件
  - date: "2026-09-24"
    kind: verified
    summary: 67 项测试、技能校验、页面脚本检查和五类总览浏览器验证通过
---

# 角色项目理解目录

项目根目录新增按需创建的 `project-context/context.sqlite3`。所有角色共用一套结构，以 `role_id` 区分总览与五类主题：流程、定义、事件、接口、数据。只有角色的已接受边界 Section 1 覆盖其逻辑行范围时，归属角色才能通过 CLI 修改；正式接口、数据结构与权限仍以已有契约、源码和边界为准。跨角色变更由项目角色协调各归属角色更新，不生成重复的全项目说明。

Dashboard 用只读连接读取实际项目数据库，增加独立的“项目理解”视图。点击角色卡进入该角色的流程总览；顶部并列展示流程、事件、数据、接口和定义总览，每类卡片点击后进入条目详情。流程详情直接展示触发事件、执行步骤、输入与输出数据、相关接口和产出事件；事件详情展示触发条件、执行动作与消费方。未建立总览时明确提示。写入工具要求角色匹配、记录版本匹配，并将删除保留为可恢复标记。它不替代客户授权或 OS 级身份验证。

实现位置：[项目理解规范](../../references/project-context.md)、[SQLite CRUD 工具](../../scripts/context_store.py)、[Dashboard 服务](../../scripts/serve_dashboard.py)、[Dashboard 页面](../../assets/role-dashboard/index.html)、[数据库测试](../../scripts/tests/test_context_store.py)与[Dashboard 测试](../../scripts/tests/test_dashboard.py)。

验证：技能结构校验通过；67 项测试通过，覆盖单库角色隔离、分类汇总、事件触发器、流程触发事件及输入输出关系、跨角色关联拒绝、版本 1→2 迁移、CRUD 版本冲突、可恢复删除与 Dashboard 只读接口；页面脚本语法检查通过。浏览器在临时项目中验证了流程总览→订单导出详情（触发事件、步骤、输入数据、输出数据、相关接口和产出事件），以及事件、数据、接口总览及各自详情。没有改动示例业务项目。
