---
id: project-scheduler-role-change
type: change
title: 将调度定义为项目角色
created: "2026-09-20"
updated: "2026-09-20"
timezone: Asia/Shanghai
status: verified
related:
  - resolve-role-governance-conflicts
events:
  - date: "2026-09-20"
    kind: created
    summary: 在治理与能力实现之间增加独立的项目调度职责
  - date: "2026-09-20"
    kind: implemented
    summary: 保持 Governance 为唯一内置角色，由其创建项目调度角色
  - date: "2026-09-20"
    kind: verified
    summary: 中英文规则一致性、格式、文档链接及章节锚点检查通过
---

# 项目调度角色

1. **职责**：Governance 是唯一内置角色，定义能力、装配和项目调度角色的权限；项目调度角色按获批定义派发执行代理。读取角色卡用于路由不等于激活其修改权限。
2. **产物**：新增 [scheduler.md](../../references/scheduler.md) 模板。实际项目创建自己的 role-card.md、boundary.md 与伴随说明，配置执行记录路径、并发工具和限制。模板本身不授予权限。
3. **执行**：节点是角色＋阶段＋可验证产物；代码引用图仅提供依赖线索。明确契约就绪、实现就绪与验证通过的放行条件，检查写入冲突与工具容量。能力代理不派生代理；无子代理工具时可顺序切换。单角色独立任务无需强制创建调度记录。
4. **验收**：调度核对实际差异和证据，失败只阻塞相关后续；共享契约变化使相关证据失效。装配验证最终组合状态，单个代理完成不等于系统通过。共享图谱输出分配唯一写入阶段，避免并行覆盖。

## 涉及规则

同步更新 [英文主文件](../../SKILL.md)、[中文主文件](../../SKILL.zh.md)、[bootstrap](../../references/bootstrap-workflow.md)、[角色模板](../../references/role-card.md)、[边界格式](../../references/module-boundary.md)、[治理边界](../../references/built-in-boundary.md)与[装配规则](../../references/built-in-assembly.md)。临时的内置调度角色草案已替换，没有增加第二个内置角色。

## 验证和限制

Skill 格式、真实文件链接、章节锚点、嵌套代码围栏和 `git diff --check` 均通过。检查了单角色直接执行、多角色就绪队列、缺少并行工具、写入冲突、失败阻塞、证据失效及断点恢复的规则衔接。

本次只更新技能规范和角色模板，没有创建业务项目的调度角色、启动执行代理或实现通用调度引擎；未执行运行时调度测试。保留已有工作区修改，未提交、推送或覆盖本地安装版本。
