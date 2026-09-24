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
  - date: "2026-09-24"
    kind: changed
    summary: 数据与接口总览直接显示字段和请求 URL，项目理解显示角色职责与边界，默认移除角色图谱
  - date: "2026-09-24"
    kind: verified
    summary: 68 项测试、技能校验、页面脚本检查与移动端字段视图验证通过
  - date: "2026-09-24"
    kind: clarified
    summary: 明确按钮点击和键盘激活属于 Interface 来源事件，并链接触发流程
  - date: "2026-09-24"
    kind: verified
    summary: 临时预览中确认按钮事件出现在事件总览及订单导出触发事件中
  - date: "2026-09-24"
    kind: changed
    summary: 事件改为仅描述发生内容，按钮点击与同次 HTTP 请求合为一个逻辑事件，所有事件须触发流程
  - date: "2026-09-24"
    kind: changed
    summary: 默认移除独立事件总览，流程直接维护触发条件与上游流程关系
  - date: "2026-09-24"
    kind: verified
    summary: 71 项测试、技能校验、脚本语法检查和四类总览浏览器验证通过
---

# 角色项目理解目录

项目根目录新增按需创建的 `project-context/context.sqlite3`。所有角色共用一套结构，以 `role_id` 区分流程、定义、接口和数据。只有角色的已接受边界 Section 1 覆盖其逻辑行范围时，归属角色才能通过 CLI 修改；正式接口、数据结构与权限仍以已有契约、源码和边界为准。跨角色变更由项目角色协调各归属角色更新，不生成重复的全项目说明。旧事件数据保留兼容，不再用于普通流程的触发条件。

Dashboard 用只读连接读取实际项目数据库，增加独立的“项目理解”视图。点击角色卡进入该角色的流程总览；顶部并列展示流程、数据、接口和定义总览。角色职责与修改边界从角色卡和边界文档读取。数据与接口总览直接展示具体字段，HTTP 接口展示请求方法与 URL；点条目可看完整说明。流程详情直接展示触发条件、执行步骤、输入与输出数据和相关接口。按钮点击或键盘激活若启动行为，直接写为流程触发条件；同次 HTTP 请求是流程步骤。SQLite 版本 5 新增直接触发条件，旧事件行及关联保留读取兼容；`validate` 检查活动流程是否缺少触发条件。默认 Dashboard 移除角色功能图谱入口。写入工具要求角色匹配、记录版本匹配，并将删除保留为可恢复标记。它不替代客户授权或 OS 级身份验证。

实现位置：[项目理解规范](../../references/project-context.md)、[SQLite CRUD 工具](../../scripts/context_store.py)、[Dashboard 服务](../../scripts/serve_dashboard.py)、[Dashboard 页面](../../assets/role-dashboard/index.html)、[数据库测试](../../scripts/tests/test_context_store.py)与[Dashboard 测试](../../scripts/tests/test_dashboard.py)。

验证：技能结构校验通过；71 项测试通过，覆盖单库角色隔离、流程直接触发条件与上游流程、数据/接口字段、请求 URL、版本 1/2/3/4→5 迁移、旧事件兼容、无触发条件流程检查、CRUD 版本冲突、可恢复删除与 Dashboard 只读接口；页面脚本语法检查通过。浏览器在临时项目中确认项目理解只显示流程、数据、接口、定义四类总览，订单导出详情直接显示按钮点击触发条件，HTTP 请求列在流程步骤中；通知流程通过 `sourceFlow` 指向订单导出。没有改动示例业务项目。
