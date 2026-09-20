---
id: resolve-role-governance-conflicts
type: change
title: 统一角色治理、装配、并行及语言约定
created: "2026-09-20"
updated: "2026-09-20"
timezone: Asia/Shanghai
status: verified
related: []
events:
  - date: "2026-09-20"
    kind: created
    summary: 根据角色治理审查解决规则冲突，保留用户工作区修改
  - date: "2026-09-20"
    kind: implemented
    summary: 统一治理权限、分层装配、依赖调度和语言原生测试规则
  - date: "2026-09-20"
    kind: verified
    summary: 格式、文件链接、章节锚点、嵌套代码围栏和差异空白检查通过
---

# 角色治理冲突修正

1. **基线与范围**：以用户当前工作区为基线，保留已有未提交修改及游戏示例产物。本次修改治理 Markdown；不修改游戏代码、脚手架脚本、扫描器、查询器或业务图谱。沿用仓库已有 `doc/change/` 存放本记录，不迁移历史文档。
2. **治理权限**：bootstrap 只规划目录、共享契约和唯一归属，不创建 Model 源码。获批后的激活角色才可创建应用文件或执行适用脚手架。是否新项目由实际源码和构建信息判断，不能仅看 `src/` 是否存在。应用源码精确到文件，支持性目录可用条件范围。
3. **装配与调度**：装配角色管理明确归属的入口、配置和分层装配文件。main 仅调用 Interface；各文件仍遵守相邻层调用，读 API 不等于可导入任意层。构建与测试配置允许提前准备，避免“先测试、最后才建测试环境”的死锁。角色仅在契约确定、写入不重叠、依赖就绪时并行；工具不可用时可顺序切换。最终集成等待实际依赖验证，而非全部无关角色完成。
4. **格式与配套规则**：语言优先级统一为用户要求、仓库约定、工具链惯例，系统区域仅兜底自然语言。移除 main.ts、GameLoop、test.ts 的强制要求。测试归属按角色，覆盖仍按层验证；Go 等需就近存放的测试遵循发现规则。公共入口路径以声明为准，可位于 public 内或根门面；其他内部文件仍不可直接导入。

## 关联规则

- [英文主文件](../../SKILL.md) / [中文主文件](../../SKILL.zh.md)
- [Bootstrap 与依赖调度](../../references/bootstrap-workflow.md)
- [装配角色](../../references/built-in-assembly.md) / [API 规范](../../references/api-spec.md)
- [角色卡](../../references/role-card.md) / [边界文档](../../references/module-boundary.md)
- [测试](../../references/testing.md) / [入口](../../references/entrypoint.md)
- [共享架构](../../references/architecture.md) / [图谱路径配置](../../references/code-atlas.md)

同步修正了角色模板自身修改权限的歧义：修改边界先切换治理角色并按授权验收，能力角色仅维护白名单内的实现报告。小修复仍需加载角色与边界。边界职责描述位于 functional-description.md；内置治理文档保留明确例外。图谱工具默认路径保持兼容，采用项目根 docs 时显式配置 --out 和 --atlas。

## 验证与实际限制

- skill-creator 的 quick_validate.py 返回 `Skill is valid!`。
- 检查主文件与全部参考文档的真实 Markdown 链接、章节锚点、嵌套代码围栏：无缺失。
- `git diff --check` 通过；相对于修改前用户工作区检查，17 份治理规则文件发生本次修正。
- 场景审查：根目录 Python 项目走存量映射；治理角色不写共享源码；共享模型变更由唯一属主先完成；装配先准备测试配置后按分层文件集成；无并行工具可顺序执行；Go 测试不被强制改成 TypeScript。
- 未修改可执行工具，未重复运行其单元测试。上述检查只验证文本一致性，不声称已完成跨角色真实项目行为评估。
- 未提交、推送或覆盖本地已安装版，避免将用户现有未提交工作混入发布；本次结果留在仓库工作区供审查。
