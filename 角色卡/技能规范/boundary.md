# 技能规范边界

## Section 1: 可修改文件与目录

| 类型 | 可操作路径 | 用途 |
| --- | --- | --- |
| 单文件 | `SKILL.md` | 英文技能入口规范 |
| 单文件 | `SKILL.zh.md` | 中文技能入口规范 |
| 单文件 | `README.md` | 项目说明与导航 |
| 单文件 | `references/role-card.md` | 角色卡格式与使用规则 |
| 单文件 | `references/project-role.md` | 项目管理角色规则 |
| 单文件 | `references/bootstrap-workflow.md` | 初始化与角色建立流程 |
| 单文件 | `references/module-boundary.md` | 模块边界格式与授权规则 |
| 单文件 | `references/built-in-boundary.md` | 内置治理边界参考的双格式说明 |
| 单文件 | `references/built-in-boundary.yaml` | 内置治理边界参考的同步 YAML 副本 |
| 单文件 | `references/documentation.md` | 文档通用规则 |
| 单文件 | `references/proposal-review.md` | 提案评审流程 |
| 单文件 | `references/testing.md` | 测试通用规则 |
| 单文件 | `references/test-role.md` | 固定测试角色规则 |
| 单文件 | `references/scheduler.md` | 项目角色调度规则 |
| 单文件 | `references/group-leadership.md` | 旧组内协作指南链接；现行统筹与增员规则以更新后的治理/调度指南为准 |
| 单文件 | `references/meeting.md` | 项目协作与技术评审会议主持规则 |
| 单文件 | `references/task-operations.md` | 统筹逐角色授权与独立验收的任务工具说明 |
| 单文件 | `references/coordination.md` | 各角色直接向统筹反馈及原始证据记录规则 |
| 单文件 | `references/built-in-assembly.md` | 装配角色固定职责与统筹授权边界 |
| 单文件 | `references/governance-changelog.md` | 治理变更记录规则 |
| 单文件 | `references/team-formation.md` | 团队组建与治理职责规则 |
| 单文件 | `references/acceptance-role.md` | 独立验收角色规则 |
| 单文件 | `references/evidence.md` | 角色协作证据规则 |
| 单文件 | `references/workflow.md` | 角色协作工作流规则 |
| 单文件 | `references/shared-directories.md` | 共享目录与角色所有权规则 |
| 单文件 | `references/api-spec.md` | 角色工具接口规范 |
| 单文件 | `references/entrypoint.md` | 角色工具入口规范 |
| 单文件 | `references/feature-point.md` | 角色功能说明规范 |
| 单文件 | `references/planning-role.md` | 策划角色职责、交付文档与协作边界规则 |
| 待新增单文件 | `references/project-rules.md` | 项目工程法案指南，接入后方可创建 |
| 待新增单文件 | `references/role-memo.md` | 角色备忘录指南，接入后方可创建 |
| 单文件 | `角色卡/技能规范/memo.md` | 技能规范角色的工作备忘录 |
| 单文件 | `角色卡/技能规范/feature-map.md` | 本角色功能导航 |
| 单文件 | `角色卡/技能规范/docs/feature/project-rules-memo.md` | 法案与 memo 规范的当前功能说明 |
| 单文件 | `角色卡/技能规范/docs/change/2026-10-10_change_project-rules-memo.md` | 本次技能规范变更记录 |
| 单文件 | `角色卡/技能规范/docs/feature/role-groups.md` | 平级角色组别的当前功能说明 |
| 单文件 | `角色卡/技能规范/docs/change/2026-10-14_change_role-groups.md` | 本轮组别规则修改记录 |
| 单文件 | `角色卡/技能规范/docs/change/2026-10-14_change_group-leadership.md` | 组长与工作量评估机制修改记录 |
| 单文件 | `角色卡/技能规范/docs/feature/boundary-yaml.md` | 边界文档双格式的当前功能说明 |
| 单文件 | `角色卡/技能规范/docs/change/2026-10-16_change_boundary-yaml.md` | 本轮边界 YAML 支持修改记录 |
| 单文件 | `角色卡/技能规范/docs/feature/role-authority-split.md` | 角色权责拆分功能说明 |
| 单文件 | `角色卡/技能规范/docs/change/2026-10-19_change_role-authority-split.md` | 本轮角色权责拆分技能规范变更记录 |
| 条件目录 | `角色卡/技能规范/docs/meetings/` | 已获准的技能维护组会议纪要，不包含其他角色文档 |
| 单文件 | `角色卡/技能规范/docs/fix/2026-10-20_fix_workflow-gaps.md` | 工作流缺口的技能规范修复记录 |
| 单文件 | `site/index.html` | 中文宣传页正文、安装命令、搜索元数据与来源链接 |
| 单文件 | `site/en/index.html` | 已确认 OPT-EN 的完整英文宣传页 |
| 单文件 | `site/style.css` | 两语言页共用的响应式布局与可访问样式 |
| 单文件 | `site/main.js` | 两语言页共用的复制按钮渐进增强及成功/失败反馈 |
| 单文件 | `site/sitemap.xml` | 实际公开页面的站点地图 |
| 单文件 | `.github/workflows/pages.yml` | 仅将 site 静态文件发布到 GitHub Pages 的声明 |
| 单文件 | `角色卡/技能规范/docs/feature/public-landing-page.md` | 宣传页用途、页面与复制流程、发布办法及设计历史链接 |

白名单路径以仓库根目录为基准。本轮列出的新参考文件及功能/变更记录仅供技能规范角色按确认方案撰写。其他文件和目录默认只读；角色卡与边界由 ANS Governance 唯一维护。除上表明确列出的静态宣传页、复制增强脚本和 Pages 声明外，其他程序及程序测试路径不在本边界内。

此前 2026-10-20 工作流缺口修复阶段的治理授权仅增加本角色工作文档；本次宣传页的精确实现权限另依下文客户确认授予，不扩展其他角色的权限。

2026-10-20 用户确认 P1＋LP-D1 并选择 OPT-EN，授权上述静态页面及发布声明的实施。README 本次只增加线上核验后的站点链接；功能导航只接入本次功能说明。GitHub 账户设置、推送与部署由可信操作端按客户授权执行，本角色不因此取得账户管理、其他角色文件或任务状态权限。
