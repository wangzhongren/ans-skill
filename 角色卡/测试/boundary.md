# 测试角色边界

## Section 1: 可修改文件与目录

| 类型 | 可操作路径 | 用途 |
| --- | --- | --- |
| 单文件 | `角色卡/测试/memo.md` | 测试角色的工作备忘录 |
| 单文件 | `角色卡/测试/feature-map.md` | 本角色功能导航；说明无直接业务功能 |
| 单文件 | `角色卡/测试/docs/design/2026-10-10_design_project-rules-memo-validation.md` | 项目法案与 memo 方案的验证设计 |
| 单文件 | `角色卡/测试/docs/change/2026-10-10_change_project-rules-memo-validation.md` | 本次验证工作记录 |

未列路径默认只读。本边界不授予测试源码、业务代码、构建配置、其他角色文档或技能规范的写入权限；角色卡与边界由 ANS Governance 唯一维护。新增路径须先由 Governance 更新边界并取得所需确认。
