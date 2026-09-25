---
id: key-creation-feedback-fix
type: fix
title: 创建项目 Key 时就近显示错误并选择已有项目
created: "2026-09-25"
updated: "2026-09-25"
timezone: Asia/Shanghai
status: verified
related:
  - dashboard-admin-simplified-change
events:
  - date: "2026-09-25"
    kind: fixed
    summary: 线上创建 Key 返回 Project not found，原页面只在顶部显示错误
  - date: "2026-09-25"
    kind: verified
    summary: 400 响应、表单就近提示与项目选择器结构测试通过
---

# 项目 Key 创建反馈

创建 Key 的 `projectId` 必须先存在于项目列表。实际提交 `dkds` 时，服务器返回 400 `Project not found`；旧管理页虽然发出了请求，但错误只显示在页首，用户在页面下方看起来像没有反应。

管理页现在从服务器返回的项目列表生成“所属项目”选择器；表单原生校验失败或 API 返回错误时，就近显示文字并滚动到提示。创建成功后，Key 的一次性展示区滚动进入可见范围。Key 后端验证逻辑不放宽；先创建项目，再创建它的 Key。旧容器需要复制新版 `dashboard/` 并重建后才会显示此改动。
