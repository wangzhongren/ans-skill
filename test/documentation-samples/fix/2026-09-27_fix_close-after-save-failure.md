---
id: sample-close-after-save-failure-fix
type: fix
title: 保存失败后工单详情仍被关闭
created: "2026-09-27"
updated: "2026-09-27"
timezone: Asia/Shanghai
status: draft
related:
  - sample-save-exit-feedback-change
events:
  - date: "2026-09-27"
    kind: created
    summary: 写作示例：从症状、原因和处理说明修复
---

# 保存失败后工单详情仍被关闭

> 教学示例；以下故障和修复是为演示文档写法而设定的，不是本仓库的真实缺陷。

客服填完工单，点“保存退出”。明明没存上，页面却关了。再次打开，刚输入的内容也不在。没存上时应该留在原页，让客服看到原因并重试。

问题出在关页的位置：不管保存成功还是失败，代码都会关掉详情页。就算弹出错误提示，页面也马上消失。

只改关页条件：存上了才关。没存上就提示原因，保留表单内容。保存接口和审核提交都不改。

以后要让保存接口分别返回成功和失败：成功时退出；失败时不退出、输入仍在。现在还没做，也没测。
