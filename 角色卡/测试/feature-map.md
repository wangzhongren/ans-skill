# 测试角色功能导航

本角色没有直接负责的业务功能。测试设计、场景推演和测试报告属于角色职责，不是产品功能；受测流程应回到功能所有者的当前功能文档。

## 本轮受测对象

- [角色分权当前说明](../技能规范/docs/feature/role-authority-split.md)、[任务工具导航](../任务工具/feature-map.md)与[分权方案](../项目管理/docs/design/2026-10-19_design_role-authority-split.md)：统筹、架构、开发、固定测试及独立验收的实际交接。
- [独立 CLI 流程测试](../../scripts/tests/test_role_authority_flow.py)及[本轮原始验证报告](docs/change/2026-10-19_change_role-authority-split-validation.md)：真实临时项目、旧基线、完整回归、timer 和 Dashboard 的已运行结果及限制，供验收独立判断。

- [项目工程法案指南](../../references/project-rules.md)：所有角色共用的工程约束如何建立、适用和检查。
- [角色备忘录指南](../../references/role-memo.md)：角色如何保存事实与续接线索。
- [ANS 项目当前工程法案](../项目管理/docs/project-rules.md)：本项目已确认约束的实际实例。
- [验证设计](docs/design/2026-10-10_design_project-rules-memo-validation.md)：测试情境、文档核对点和结果口径。
- [技能规范角色的当前功能说明](../技能规范/docs/feature/project-rules-memo.md)及[本轮变更记录](../技能规范/docs/change/2026-10-10_change_project-rules-memo.md)：当前实际功能流程和交付历史由该角色维护；测试导航不复制其流程。
