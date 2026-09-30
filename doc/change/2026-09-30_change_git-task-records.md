---
id: git-task-records-change
type: change
title: 新任务用一份可随 Git 同步的 Markdown 保存计划和进度
created: "2026-09-30"
updated: "2026-09-30"
timezone: Asia/Shanghai
status: verified
related: [git-task-records]
events:
  - date: "2026-09-30"
    kind: created
    summary: 修改任务存储、Dashboard 读取和使用说明
  - date: "2026-09-30"
    kind: verified
    summary: 157 项回归及跨角色计时修复回放通过
---

# 新任务的记录可以随项目提交到 Git

以前一个任务会在 `docs/scheduling/<任务ID>/` 里生成计划 JSON、状态 JSON、事件 JSONL 和展示表。任务多了，项目里出现很多执行文件；换机器时也难以从这些文件看清任务经历。

现在新任务写到 `docs/scheduling/<任务ID>.md`。打开它，先看到需求和设计版本、由谁处理哪一步、目前状态，以及按时间排列的变化。工具在文件末尾保存可核对的机器记录；角色通过 `task_ops` 更新，不能直接编辑任务状态。

## 只改了这些位置

1. [任务存储](../../scripts/coordination_store.py)：一次操作只原子更新一份 Markdown。事件编号和哈希链仍在；中途写失败时保留上一份完整记录。锁与检查日志留在 `.ans/runtime/`。
2. [任务入口](../../scripts/task_ops.py)：新任务拒绝覆盖同名旧 JSON 任务；命令行支持从标准输入接收请求和已审核的同意凭据；换机器缺少检查证据时阻止依赖步骤继续派发。
3. [Dashboard](../../dashboard/server.py)：读取新任务 Markdown。原有 JSON 任务目录仍能只读查看；检查日志不在本机时，已验收的历史状态标为需核对。
4. [任务使用说明](../../references/task-operations.md)、[调度说明](../../references/scheduler.md)、[协调说明](../../references/coordination.md)、[README](../../README.md)和[Dashboard 指南](../../references/dashboard.md)：同步新的文件位置与跨机器接手限制。

程序的业务源码、旧图谱和云端账号数据没有改。项目级的 `.ans/project.json` 仍作为一份已审核的执行配置，保留现有授权检查。旧任务历史没有被删除或转换。

## 怎样检查

- 工具完整回归：157 项通过，涵盖授权、版本、重复反馈、原子写、Git 合并、冲突拒绝、跨机器缺证据阻断、Windows 风格换行、标准输入同意凭据以及 Dashboard 新旧读取。
- 真实回放：用游戏引擎现有计时问题走“失败 → 改设计 → 暂停旧任务 → 重做 → 验收”，结果通过；产生 1 份任务 Markdown，记录 22 条事件。
- 单独复制 `dashboard/` 到临时目录后，服务模块仍能启动命令行；本地读取新任务则使用包含 `scripts/` 的完整技能安装。
- 这次未运行线上部署检查，也未把旧任务转成新格式。没有原令牌的新机器不能直接接手仍在运行的旧批次；要先核对并按授权重新安排。
