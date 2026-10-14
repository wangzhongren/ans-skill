---
id: role-groups-validation
type: change
title: 独立验证平级角色组别文档
created: "2026-10-14"
updated: "2026-10-14"
timezone: Asia/Shanghai
status: verified
related: [role-groups-feature, role-groups-change, role-groups-design]
events:
  - date: "2026-10-14"
    kind: verified
    summary: 独立检查角色组别文档并验证现有逐角色范围校验行为
---

# 独立验证平级角色组别文档

这轮修改把角色组别定义为协作标签，同时保留每个角色自己的文件边界。独立检查确认最终技能文档与已确认方案一致；现有任务范围校验仍按具体角色处理写入范围。

## 候选与依据

- 技能文档候选：按下列固定顺序，对每个 UTF-8 相对路径、NUL 字节、文件原始字节、NUL 字节连续计算 SHA-256，结果为 `33655e2c5832b8a1b9d58fb0665d8bd613b4cb521ad0c1a76a464a93e1b56960`：`SKILL.md`、`SKILL.zh.md`、`README.md`、`references/role-card.md`、`references/project-role.md`、`references/bootstrap-workflow.md`、`references/module-boundary.md`、`references/test-role.md`、`references/scheduler.md`、`角色卡/技能规范/feature-map.md`、`角色卡/技能规范/docs/feature/role-groups.md`、`角色卡/技能规范/docs/change/2026-10-14_change_role-groups.md`。初检后原文档 owner 只更新功能导航和 feature/change 的状态、验证事件及报告链接；项目管理只更新方案验证状态、真实结果和报告链接。我短复核了这些收尾，未发现规则或范围变化，并重算上述最终哈希。
- 代码检查输入：基线 Git `54ff93307ee2ee8bdac52d13789d0c4e6cce1675`；`scripts/task_ops.py` SHA-256 `90c8644f202913144a5f83e01b7276f14f67240f55519b5c6435775cd21f1017`。临时验证直接调用现有 `roles_valid`；该函数使用 `claim_scope` 按 `role_id` 拒绝跨角色重叠，并要求每个写入文件出现在该角色 boundary Section 1。没有修改该脚本。
- 方案依据：[客户确认的项目管理方案](../../../项目管理/docs/design/2026-10-14_design_role-groups.md)及其“本轮分工与验证”要求；同时按项目工程法案 DOC-01 核对新功能、历史文档和双向链接沿用现有 `docs/` 结构。TASK-01 的执行工具与正式任务记录规则没有因本次文档改动而改变。

## 检查结果

| 输入与步骤 | 预期 | 实际结果 |
| --- | --- | --- |
| 同一组的两个临时角色卡分别声明不同写入文件；调用 `roles_valid` | 两个范围仍分别归各自 `role_id`，组别不合并权限 | 通过；返回所有权分别为 `r1` 与 `r2` |
| 同组两个临时角色在 Section 1 声明同一路径；调用 `roles_valid` | 按现有重叠所有权规则拒绝 | 通过；拒绝信息为 `Duplicate or overlapping file owner: src/a.py` |
| 不同组的临时角色各自声明不同且独立授权的文件；调用 `roles_valid` | 不因组别不同而阻止其独立范围 | 通过；两个路径分别保留给各自 `role_id` |
| 同组临时角色把另一角色的文件加入自己的 `writeFiles`，但自身 Section 1 未列出；调用 `roles_valid` | 组名不能替代自身边界授权 | 通过；拒绝信息为 `Configured write file is absent from boundary Section 1: src/b.py` |
| 临时旧角色卡没有组别字段，但配置和边界仍有效；调用 `roles_valid` | 旧卡不改变原有逐角色范围校验 | 通过；原角色范围仍有效 |
| 对最终技能文档、当前功能、变更记录与项目管理方案只读比对 | 既有角色调组时只维护原卡、不复制角色或边界；确需新增角色才建平级卡和独立边界；固定角色上下文、项目管理派发、独立测试及未获准请求保持待办等规则一致 | 通过；方案 Mermaid 和功能 Mermaid 均包含调组/新增角色以及未获准待办分支 |
| 只读核对入口与参考：英文/中文入口、README、模板、项目管理/测试建卡指南、bootstrap、module-boundary、scheduler | 表述一致；调度使用具体 `roleId`，组别不是工具授权字段 | 通过；各入口链接到集中规则，scheduler 指明具体 `roleId` 和原有逐角色边界 |
| 核对文档身份、变更路径和内容 | 角色平级、无目录迁移或组权限文件；开发角色不自改卡；旧卡在 Governance 下次维护补字段 | 通过；文档把组别写作协作元数据，并说明既有角色仅更新原卡 |
| 检查受测文档与相关治理文件的相对链接/锚点、元数据、Mermaid 结构及历史导航 | 新增文档链接有效；front matter 与日期一致；当前功能和历史双向关联；流程图节点/分支结构完整 | 通过；报告创建后复查链接，相关路径与锚点均存在；设计、功能、变更及本报告相互链接 |
| `git diff --check` 与变更路径审阅 | 无空白错误，变更限于已授权的 12 个技能文件、治理已获准路径及 PM 方案 | 通过；没有发现测试源码、业务代码或旧 `test/game-engine` 文件改动 |

以上临时角色卡和 boundary 只写在系统临时目录，用于直接调用现有校验函数；没有加入仓库、没有激活为正式角色，也没有把结果表述成真实代理或文件系统权限执行测试。`roles_valid` 验证的是本地任务配置的逐角色写入范围规则。

## 限制与交接

本轮是技能文档审阅和现有配置校验逻辑的定向调用，不是完整应用、桌面界面或跨角色真实执行测试。组别不是工具授权字段，因此没有程序级组别执行行为可测。文字规则中的固定上下文、由 Governance 维护角色卡、项目管理按角色派发和独立测试职责只做文档一致性检查。

尝试运行官方 `skill-creator/scripts/quick_validate.py` 检查器，但当前 Python 3.14.7 环境缺少 PyYAML，检查器在导入 `yaml` 时退出；没有安装依赖。使用系统 Ruby YAML 库检查两个技能入口的 front matter 为含非空 `name`、`description` 的映射，并解析三份 design/feature/change 文档及本报告的 YAML 元数据，检查通过。尚未对 Mermaid 使用专用解析器；检查限于图块与结构的文档审阅。

发现后续文案或链接问题时，由项目管理交给原文档 owner 处理；测试角色不修改受测规范、角色卡或边界。本轮验证不代表技能已发布或安装。

## 相关记录

- 当前规则：[平级角色组别功能说明](../../../技能规范/docs/feature/role-groups.md)
- 文档改动：[技能规范变更记录](../../../技能规范/docs/change/2026-10-14_change_role-groups.md)
- 方案与评审：[项目管理方案](../../../项目管理/docs/design/2026-10-14_design_role-groups.md)
