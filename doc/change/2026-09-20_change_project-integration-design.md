---
id: project-integration-design-change
type: change
title: 项目默认角色统一设计角色对接文档
created: "2026-09-20"
updated: "2026-09-20"
timezone: Asia/Shanghai
status: verified
related:
  - project-scheduler-role-change
events:
  - date: "2026-09-20"
    kind: created
    summary: 项目角色负责架构、抽象和角色对接设计，执行角色负责实现
  - date: "2026-09-20"
    kind: implemented
    summary: 明确设计文档归属、实现报告及切换授权规则
  - date: "2026-09-20"
    kind: verified
    summary: Skill 格式、引用、章节锚点和差异空白检查通过
---

# 项目角色与角色对接设计

1. **默认职责**：治理角色创建并验收项目默认角色。主聊天框保持该角色，可全局只读调查、写获批架构/抽象/对接设计和调度记录，但不写业务源码、抽象接口源码、测试或授权配置。
2. **对接文档**：项目角色维护唯一的共享设计，包含参与角色、层级调用路径、契约版本、输入输出、错误语义、生命周期、交付依赖和验证要求。执行角色按设计实现，`api-spec.md` 记录实际导出、设计版本、差异及测试证据。
3. **变更与授权**：契约不可实现时由执行角色反馈，项目角色修订设计并协调受影响任务；修改权限仍由客户授权及治理流程处理。角色启用、切换和子代理派发统一检查客户同意或客户认可项目配置中的适用预授权，文件归属本身不等于自动执行权限。
4. **执行隔离**：工作代理在本次执行实例内锁定角色，不自行改身份或派生代理。无子代理工具的顺序切换也不豁免授权；主聊天框默认调查角色不会因读取其他角色卡而获取写权限。

新增 [project-role.md](../../references/project-role.md)，同步 [调度协议](../../references/scheduler.md)、[API 实现报告](../../references/api-spec.md)、[角色模板](../../references/role-card.md)、[bootstrap](../../references/bootstrap-workflow.md)、[装配规则](../../references/built-in-assembly.md)及中英文主文件。

验证：格式检查返回 Skill is valid；真实 Markdown 文件链接、章节锚点、嵌套围栏和 git diff --check 通过。检查设计文档修订、接口源码实现、配置缺失、预授权范围匹配和无工具顺序执行等场景的规则一致性。未修改或运行业务代码；规范不等于已实现运行时权限拦截。本次保留已有工作区修改，未提交、推送或更新已安装版本。
