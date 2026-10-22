# ANS 项目工程法案

版本：4。更新日期：2026-10-22。维护者：项目管理。

这份法案整理 ANS 已确认的工程选择，供所有本项目角色共同读取。通用角色权限仍以各自 boundary.md 为准；角色职责定义以 ANS 人事（ANS People Operations，原团队组建/招募）维护的角色定义参考为准（[策划](../../../references/planning-role.md)、[项目管理](../../../references/project-role.md)、[统筹调度](../../../references/scheduler.md)）。当前职责分工见[架构说明](architecture.md)和[角色分权方案](design/2026-10-19_design_role-authority-split.md)，早期法案整理见[评审记录](design/2026-10-10_design_project-rules-memo-review.md)。新增要求先走现有方案评审和客户确认流程。

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

## ROLE-01：职责分开，统筹直接逐角色安排

适用：本项目角色定义、任务交接与成果判断。

已确认要求：技能采用五个内置管理角色——沟通、策划、ANS 人事、统筹调度和独立验收；它们任何项目一开始即可使用，不需要项目角色卡，纯角色职责以 ANS 人事维护的角色定义为准（[沟通](../../../references/communication-role.md)、[策划](../../../references/planning-role.md)、[ANS 人事](../../../references/team-formation.md)、[统筹调度](../../../references/scheduler.md)、[独立验收](../../../references/acceptance-role.md)）。沟通是客户唯一接口并管理端到端工作流；策划负责产品方案、架构设计、共有业务契约和可验收完成标准；统筹判断团队并直接逐角色授权、预约、派发并收取反馈，需要新招或拆分时把团队计划和角色调整方案写入 `docs/scheduling/` 交 ANS 人事，ANS 人事只按计划写/改角色卡、边界与同步 YAML。项目管理不是默认角色：仅当统筹判断实现确实需要技术架构工作角色并按团队计划建立时，才承接策划已确认的产品方案、架构设计与共有业务契约，负责实现设计、技术评审、技术契约、工程法案及获准的共享代码与对应测试，不拥有或改写整体架构（[项目管理](../../../references/project-role.md)）。按已有规则取得客户实施授权后由统筹安排实施，不重复索取有效的同版同范围授权。开发角色负责自身实现和单元测试，固定测试负责实际跨角色流程与回归，独立验收负责前期完成标准及最终成果判断。各角色平级，group 只分类，取消 groupDuty 和组长／组员层级。上下文保持固定身份，所有写入仍受各自边界限制。

已确认工具要求：调度不能用自己的凭证完成验收；只有独立验收依据客户确认目标、实际产物及原测试证据作出的有效通过结果，才能作为依赖放行和完成依据。返工、证据不足、执行者完成反馈或停止确认都不能被当成验收通过。工具继续单写同一任务 Markdown，云端不增加角色 Key。

状态与检查：职责调整已获客户明确授权；开发方已报告真实 CLI 分权实现及自身验证，固定测试已提交[正式原报告](../../测试/docs/change/2026-10-19_change_role-authority-split-validation.md)，独立验收已按标准 v2 判定 [C1–C8 全部通过](../../验收/docs/acceptance/2026-10-19_role-authority-split-result.md)；本法案不把进度汇报当作最终通过。2026-10-22 五内置管理角色模型只调整角色职责表述与后续需求路由（架构设计归策划，项目管理按统筹团队计划按需建立），不改 Section 1 路径、本轮已完成方案归属或 CLI 验收契约。按实际角色卡／边界及最终执行证据核对，不新增本文之外的审批门槛。依据：[客户决定及本轮方案](design/2026-10-19_design_role-authority-split.md)、[独立验收标准](../../验收/docs/acceptance/2026-10-19_role-authority-split-criteria.md)、[五内置管理角色候选返工计划](../../../docs/scheduling/2026-10-22_five-role-rework.md)。

## 历史

| 日期 | 变化 | 依据 |
| --- | --- | --- |
| 2026-10-10 | 把已有已确认约束整理到单一入口，未新增业务行为 | [本轮方案](../../../doc/design/2026-10-10_design_project-plan-role-memo.md)、[评审](design/2026-10-10_design_project-rules-memo-review.md) |
| 2026-10-19 | 按客户已确认决定记录独立团队组建（现人事）、扁平角色和调度／架构／测试／验收分工；CLI 实现与验证状态明确为待完成 | [本轮方案](design/2026-10-19_design_role-authority-split.md)、[当前架构](architecture.md) |
| 2026-10-19 | 记录用户新增独立策划与后续产品方案→技术设计／评审→客户授权→统筹实施路由，原 CLI 契约不变 | [本轮方案补充](design/2026-10-19_design_role-authority-split.md#11-用户新增决定后续需求先由独立策划形成产品方案)、[策划角色](../../策划/role-card.md) |
| 2026-10-22 | 按五内置管理角色模型更新 ROLE-01：架构设计归策划，项目管理改为按统筹团队计划按需建立的技术架构工作角色，仅在已确认架构下负责实现设计、技术评审与技术契约；Section 1 路径与已完成验收的 CLI 契约不变 | [架构说明](architecture.md)、[五内置管理角色候选返工计划](../../../docs/scheduling/2026-10-22_five-role-rework.md) |
