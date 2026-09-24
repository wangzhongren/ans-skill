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
    summary: 增加目录规范和 Dashboard 角色详情分类浏览
  - date: "2026-09-24"
    kind: verified
    summary: 技能校验、63 项测试、页面脚本检查与浏览器交互通过
---

# 角色项目理解目录

角色目录新增按需维护的 `project-context/`：`README.md` 是角色视角的短索引，五类主题文件夹分别记录流程、定义、事件、接口和数据。只有角色的已接受边界 Section 1 覆盖该目录时，归属角色才能修改；正式接口、数据结构与权限仍以已有契约、源码和边界为准。跨角色变更由项目角色协调各归属角色更新，不生成重复的全项目说明。

Dashboard 从实际项目的直接角色目录读取索引和五类直接 Markdown 文件，在角色详情按分类列出，并按需只读显示文件内容。未建立该目录时明确提示。服务端拒绝其他目录、嵌套文件、非 Markdown 文件和符号链接。

实现位置：[项目理解规范](../../references/project-context.md)、[Dashboard 服务](../../scripts/serve_dashboard.py)、[Dashboard 页面](../../assets/role-dashboard/index.html)、[Dashboard 测试](../../scripts/tests/test_dashboard.py)。

验证：技能结构校验通过；63 项测试通过，包括角色文档动态列出、HTTP 读取与越界拒绝；Dashboard 页面脚本语法检查通过。浏览器使用临时项目实测角色详情展示五类主题、展开流程、读取纵览与流程正文，页面按只读内容显示。
