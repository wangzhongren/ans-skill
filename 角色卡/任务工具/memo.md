# 任务工具工作线索

固定角色 task-tools；唯一写范围见 boundary.md Section 1。项目规则统一读取项目管理 docs/project-rules.md。本角色负责 CLI、存储、test_task_ops 开发单测和隔离 timer 回放；test_role_authority_flow 归固定测试独占。

当前实现 state schema2，配置/计划 schema1。调度、验收、assignment三个摘要字段各自独立；不保留旧coordinatorTokenHash/tokenHash别名，status递归去除认证字段。accept-plan和verify仅独立验收，完成由全节点当前有效pass派生。readSet必须列检查脚本、fixture及相关输入；环境只核对声明/相关变量和实际程序路径/摘要，无法发现隐藏依赖。

旧Markdown按原v1渲染校验读取；旧JSON只读加载plan/state，不声称复核旧events。recover是v2调度认证后的只读检查，不修复凭证。没有迁移、重置、TTL、组模型或新服务。

开发单测、timer原日志与候选定位见docs/change/2026-10-19_change_task-authority.md；正式QA与验收由各固定上下文提供，现已通过：[QA原报告](../测试/docs/change/2026-10-19_change_role-authority-split-validation.md)为201项/53.608秒/exit 0/无跳过，真实CLI25项；[独立验收结果](../验收/docs/acceptance/2026-10-19_role-authority-split-result.md)为标准v2 C1–C8 pass。本角色只引用独立来源。隔离fixture秘密不能作为本仓库真实任务凭证，不建立虚构生产任务。
