# 技能规范角色变更记录

- 2026-10-19：按用户取消组长层级、改由统筹直接协调的决定，更新 boundary 中四条仍描述现行双级调度/组长职责的产品指南用途；只改 `references/meeting.md`、`task-operations.md`、`coordination.md`、`built-in-assembly.md` 的用途说明，文件所有权与权限不变。Doc: [boundary.md](boundary.md)、[boundary.yaml](boundary.yaml)。

- 2026-10-19：依据用户新增策划角色的请求，增加 `references/planning-role.md` 的精确写入路径；该指南由技能规范角色维护，用于说明用户目标与产品流程方案的策划职责及与技术架构、调度、执行、测试和验收的分工。现有角色权责拆分功能/变更文档可承载相应记录，无新增宽泛目录权限。Doc: [boundary.md](boundary.md)、[boundary.yaml](boundary.yaml)。

- 2026-10-19：按用户后续决定，移除技能规范卡片的组长/组员身份与默认组内调度；`group` 仅作分类，规范角色仍只维护产品规则。角色模板和旧组内协作指南的产品更新由技能规范角色维护。Doc: [role-card.md](role-card.md)、[boundary.md](boundary.md)、[boundary.yaml](boundary.yaml)。

- 2026-10-19：依据用户确认的角色职责拆分和已确认方案，明确本角色只维护用户可读规则、模板和产品流程；团队建卡归 ANS Governance（现人事），全局派发归统筹调度，CLI 开发、独立测试和最终验收分别归其所有者。本角色组长职责限于技能维护组。Doc: [role-card.md](role-card.md)、[角色职责拆分方案](../项目管理/docs/design/2026-10-19_design_role-authority-split.md)。

- 2026-10-19：依据用户确认拆分团队组建（现人事）、统筹调度与独立验收职责，并保留项目管理的架构/公共代码职责及测试、组长的既有业务职责；为后续技能规范工作增加八份参考文档及本轮功能/变更文档的精确白名单。仅做边界准备，未授权程序测试目录。Doc: [boundary.md](boundary.md)、[boundary.yaml](boundary.yaml)。

- 2026-10-16：按用户要求补充同名 boundary.yaml，角色卡引用双格式；增加本轮双格式指南、参考副本与功能/修改文档的具体范围。YAML 不增加任何写入权限。Doc: [boundary.md](boundary.md)、[boundary.yaml](boundary.yaml)。

- 2026-10-14：按客户确认的组长方案，单角色技能维护组由本角色兼任组长；增加组长指南、相邻会议/调度说明、本轮修改记录及本组获准会议纪要的明确范围。业务权限仍限自身边界。Doc: [role-card.md](role-card.md)、[boundary.md](boundary.md)。

- 2026-10-14：按客户确认的扁平角色分组方案，角色卡增加“组别：技能维护组”，添加组别功能及修改记录的单文件白名单。组别不授予权限；本轮技能规则维护仍限现有产品白名单。Doc: [role-card.md](role-card.md)、[boundary.md](boundary.md)。

- 2026-10-10：移除角色卡导航中的本轮交付进度，保留稳定的功能导航与当前说明链接。Doc: [role-card.md](role-card.md)。
- 2026-10-10：本角色卡已接入[项目法案指南](../../references/project-rules.md)、[角色 memo 指南](../../references/role-memo.md)、共同的[项目工程法案](../项目管理/docs/project-rules.md)、本角色 memo 和[本地治理覆盖](../governance-boundary.md)；链接现有功能导航及功能说明。授权仍限本轮，不构成永久自动派发。Doc: [role-card.md](role-card.md)。
- 2026-10-10：将“项目法案与角色备忘录支持”记录为本角色负责的 ANS 技能产品功能；该记录作成时功能说明待建，后续已建立，见[当前功能说明](docs/feature/project-rules-memo.md)。Doc: [role-card.md](role-card.md)。

- 2026-10-10：创建本角色卡、边界与变更记录；授权依据为用户明确委派实施已确认方案并限定本轮角色范围。该授权不是永久自动派发授权。记录依据：[role-card.md](role-card.md) 与 [边界](boundary.md)。

## 2026-10-20 — 工作流缺口文档授权

依据用户 2026-10-20 授权，仅为本角色增加以下定点工作文档写入路径：`角色卡/技能规范/docs/fix/2026-10-20_fix_workflow-gaps.md`。其他角色路径及未列程序路径仍按原边界管理；本次不修改角色身份或组别。

## 2026-10-20：中英文静态宣传页

用户确认 P1＋LP-D1，包含 OPT-EN，并授权实现、测试、双仓库相关变更及 GitHub Pages 发布。复用技能规范角色，增加6个精确页面/发布文件和1份功能说明；同步角色职责、边界 Markdown 与 YAML。已有 README/功能导航路径仅用于本次站点入口和导航。本次不授予后台、CLI、独立测试、任务状态或 GitHub 账户管理权限，不更新本地技能安装。

## 2026-10-22：五内置管理角色模型的边界扩展

用户确认采用五个内置管理角色（沟通、策划、招募（现人事）、调度、验收）后，技能规范角色需要维护新增的沟通规则与行动/客户沟通规则。为 `references/communication-role.md`（沟通内置管理角色的规则与默认写权）和 `references/action-policy.md`（行动选择与客户沟通规则）各增加精确的单文件写入路径，并同步 Markdown 与 YAML 副本。本次只做治理边界授权，不修改技能正文、不创建其他角色，也不扩展其他角色或程序路径的权限。Doc: [boundary.md](boundary.md)、[boundary.yaml](boundary.yaml)。

## 2026-10-22：角色定义类参考移交团队组建（现人事）

用户纠正治理原则：**角色不能写自己的角色定义**。角色卡、边界以及定义角色职责和权限的规则参考都是治理资料，只能由 ANS 团队组建（招募，现人事）维护；技能规范也不得代改。据此将下列角色定义类参考从本角色边界移出，交由团队组建（现人事）唯一维护：`references/communication-role.md`、`references/planning-role.md`、`references/team-formation.md`、`references/scheduler.md`、`references/acceptance-role.md`、`references/project-role.md`、`references/test-role.md`、`references/built-in-assembly.md`、`references/built-in-boundary.md`、`references/built-in-boundary.yaml`、`references/governance-changelog.md`。本角色只保留共享入口、格式、流程和宣传页文档（包括 `references/action-policy.md`），不再维护任何角色职责、权限或边界定义；角色卡同步删除“维护治理参考”的旧表述。上一条 2026-10-22 授权中的 `references/communication-role.md` 由本次调整取代，`references/action-policy.md` 继续由本角色维护。Doc: [boundary.md](boundary.md)、[boundary.yaml](boundary.yaml)、[role-card.md](role-card.md)。

## 2026-10-22：共享架构参考归属技能规范

用户确认 `references/architecture.md` 是共享五层架构与模块组织参考，不是角色定义。将该文件精确加入本角色 Section 1 与同名 YAML 副本；本次只调整边界归属，不修改正文，正文中旧的架构归属表述留待后续技能规范任务处理。Doc: [boundary.md](boundary.md)、[boundary.yaml](boundary.yaml)。

## 2026-10-22：五内置管理角色返工的治理记录更正与边界补充

依据 2026-10-22 返工计划 `docs/scheduling/2026-10-22_five-role-rework.md` 的 B4、R1、R2，由 ANS 团队组建（招募，现人事）更正本角色治理记录并补充精确路径：

- **B4 更正**：`references/architecture.md` 的正文已在同一候选的后续轮次实际修改，不再保留“只调整边界归属、不修改正文”的记录。实际差异为：`common/shared/` 归属改为按统筹团队计划建立的项目管理（技术架构）角色；产品方案与架构设计归策划并写入 `docs/planning/`；只有该角色建立后才由其维护实现层 `docs/architecture.md` 与技术契约；跨角色共享复用在该角色未建立时由统筹判断团队计划。逐行依据见 `git diff HEAD -- references/architecture.md`。
- **B4 路径**：增加 `角色卡/技能规范/docs/change/2026-10-22_change_five-role-model.md` 精确单文件路径，由技能规范记录本候选内其所属共享文档的实际正文修改与依据。
- **R1 归属**：增加 `references/project-context.md`、`references/role-architecture-viewer.md`、`references/dashboard.md` 三个共享旧工具说明的精确单文件路径。三者按 legacy 处理，仅客户明确要求时使用；正文由技能规范更新为默认阅读路径以策划方案为准。
- **R2 更正**：`references/project-rules.md`、`references/role-memo.md` 已实际存在，删除“待新增单文件/接入后方可创建”的过期标记，改为一般单文件并写清用途。此前创建授权依据未能从现有记录核实，本次只确认现状与归属，不补造历史授权。

Doc: [boundary.md](boundary.md)、[boundary.yaml](boundary.yaml)。

## 2026-10-22 — 运行架构与上下文隔离

客户窗口只加载沟通角色；本工作角色由统筹调度启动独立上下文，只接收自己的角色、边界、授权、任务输入和交付要求，不在同一上下文切换为其他角色；不直接接受沟通派活、授权或启动。角色卡执行原则同步本条；不改变角色身份、边界或程序权限。Doc: [role-card.md](role-card.md)。
