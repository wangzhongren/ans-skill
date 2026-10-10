# ANS 项目工程法案

版本：1。整理日期：2026-10-10。维护者：项目管理。

这份法案整理 ANS 已确认的工程选择，供所有本项目角色共同读取。通用角色权限仍以各自 boundary.md 为准；本轮任务分工见[评审记录](design/2026-10-10_design_project-rules-memo-review.md)。新增要求先走现有方案评审和客户确认流程。

## DOC-01：角色功能和历史采用当前 Markdown 结构

适用：技能提供的文档约定与本项目新角色资料。

要求：沿用角色的 docs/。每个功能一份稳定的 docs/feature 文件，feature-map 导航；设计、修改、修复记录解释历史并双向链接。默认不恢复角色架构 JSON 或重复项目理解库。

实现：共同规则写在 references，实际角色只维护自己的当前文档。旧根目录 doc/ 历史保留并引用，不在一次新功能里批量改名迁移。

检查：检查实际文档入口、相对链接和是否出现两份当前功能说明。依据：[已确认文档结构改动](../../../doc/change/2026-09-30_change_role-feature-docs.md)、[当前功能指南](../../../references/feature-point.md)。

## TASK-01：任务记录必须保持可核对并可随 Git 保存

适用：scripts/task_ops.py、scripts/coordination_store.py 及其读取方。

要求：新任务保留一份 scheduling Markdown 记录；现有授权、版本、事件顺序、原子写入及检查证据验证继续有效。不能为减少文件而放松验证，也不能把无法核对的旧结果当作当前通过。

实现：通过 task_ops 更新任务文档。项目执行策略保留一份已审核配置；锁及完整检查输出留在本地运行目录。换机器先核对执行者和证据，同一任务 Git 冲突不能直接覆盖。

检查：实际任务和 Git 合并/冲突用例；旧任务只读展示及下游证据检查。依据：[任务改造记录](../../../doc/change/2026-09-30_change_git-task-records.md)、[任务操作指南](../../../references/task-operations.md)。

## DEPLOY-01：云端 Dashboard 的独立发布目录能够启动

适用：dashboard/ 的服务、导入关系和部署说明。

要求：仅复制 dashboard/ 的云端部署仍可启动，不让云端服务模块在启动时强制依赖未打包的 scripts/。本地新任务 Markdown 阅读可以要求完整技能目录，应在使用说明中写清。

实现：局部读取能力在实际使用时加载，云端部署入口遵守 dashboard/Dockerfile 的已有打包范围。

检查：隔离复制 dashboard/ 后的模块启动检查；本地新任务与旧记录的读取测试。依据：[部署约定及检查记录](../../../doc/change/2026-09-30_change_git-task-records.md)、[Dashboard 部署指南](../../../dashboard/README.md)。

## 历史

| 日期 | 变化 | 依据 |
| --- | --- | --- |
| 2026-10-10 | 把已有已确认约束整理到单一入口，未新增业务行为 | [本轮方案](../../../doc/design/2026-10-10_design_project-plan-role-memo.md)、[评审](design/2026-10-10_design_project-rules-memo-review.md) |
