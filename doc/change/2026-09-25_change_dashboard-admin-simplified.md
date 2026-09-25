---
id: dashboard-admin-simplified-change
type: change
title: 简化 Dashboard 管理页与访问模型
created: "2026-09-25"
updated: "2026-09-25"
timezone: Asia/Shanghai
status: verified
related:
  - role-channel-feature
events:
  - date: "2026-09-25"
    kind: verified
    summary: 全量测试、管理页资源与必需控件校验通过
---

# 管理页与访问模型

管理页改为项目、成员账号、项目 Key 三个分区，提供概况指标、清晰的记录列表和独立创建表单。项目 Key 在同一项目内由各角色共用：角色各自发送消息或权限申请，并声明自己的角色 ID；服务器只验证项目 Key 与声明角色存在，管理员账号仍是唯一审批入口。

所有启用的网页用户默认可以查看全部项目及其协作收件箱；普通用户不能管理项目、账号、Key 或审批。删除“授权项目”和单独“角色凭证”的页面/API 路径。旧数据库中若有 `memberships` 或 `role_tokens` 表，会原样保留但不再参与鉴权，新代码不会再创建它们。

管理页与看板共用深色侧栏、浅色工作区和青绿色操作色，窄屏改为横向导航和单列内容。验证覆盖默认全项目可见、项目 Key 按项目隔离、角色自报身份、管理员审批门禁及管理页面资源。
