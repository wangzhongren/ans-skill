---
id: flow-purpose-branch-graph-feature
type: feature
title: 流程用途、条件分支图与故障排查点
created: "2026-09-26"
updated: "2026-09-26"
timezone: Asia/Shanghai
status: verified
related:
  - role-project-context-feature
events:
  - date: "2026-09-26"
    kind: created
    summary: 用户指出流程只列步骤，既看不出用途，也看不到 if/else 和失败路径
  - date: "2026-09-26"
    kind: implemented
    summary: 增加流程用途、成功失败结果、可点击分支图和异常检查点
  - date: "2026-09-26"
    kind: verified
    summary: 107 项技能测试通过，临时项目浏览器验证用途与异常节点，旧库仍可读
---

# 流程先说清“在干嘛”

以前流程详情只有触发条件和线性步骤。像“从入口到处理结果”这样的摘要虽然占了位置，却没说清用户为什么要用这个功能、成功后哪里变了、失败时该看哪里；判断分支也被压成一条直线。

现在**新建流程必须**在 `flow.intent` 写用途与成功结果；失败结果有源码依据时也写明。页面先显示这些内容，再显示触发条件与流程图。图中的判断节点通过写明 `condition` 的线连接 `if/else` 路径；异常节点必须记录用户可见的失败结果、源码位置和至少一项排查方法。点击节点可看它的上下游与检查点。AI 用原有 `context_store.py get` 读取同一份结构，不需要重新生成全仓库代码图谱。

项目理解 SQLite 升至第 7 版，新增 `flow_intents` 和 `flow_graphs`。第 6 版数据保持可读；旧流程无结构化用途时，流程卡和详情页都明确显示“用途待补充”，`validate` 列出缺失的流程 ID。只有线性步骤时只画线性图，不猜不存在的分支。要给旧库写入用途或分支图，须先备份并确认共享数据库升级已获授权，再执行 `migrate`。云端只接收原有 JSON 展示快照，后端不需改数据库结构，但页面需部署新版前端才能画图。

验证：Python 3.14.7 下 `python3 -m unittest discover -s scripts/tests` 共 107 项通过；测试覆盖分支图来回读取、无效条件与错误节点拒绝、第 6 版旧库读取及迁移到第 7 版、Dashboard HTTP 详情和云端展示快照。临时项目浏览器中，标题下先显示用途和成功/失败结果；可见 `if/else` 连线，点击异常节点显示来源条件、代码位置与两条排查方法。旧第 6 版项目的角色和线性流程仍可读取。示例文字仅用于说明格式，实际项目的用途和分支必须来自已核对的源码与测试。
