# 任务工具角色边界

## Section 1: 可修改文件与目录

| 类型 | 可操作路径 | 用途 |
| --- | --- | --- |
| 单文件 | `scripts/task_ops.py` | 任务操作 CLI、认证和状态门禁 |
| 单文件 | `scripts/coordination_store.py` | 任务记录原子读写、渲染与事件校验 |
| 单文件 | `scripts/tests/test_task_ops.py` | 任务操作 CLI 的开发单元测试 |
| 单文件 | `scripts/validate_task_flow.py` | 实际任务 CLI 的隔离流程回放 |
| 单文件 | `角色卡/任务工具/feature-map.md` | 本角色功能导航 |
| 单文件 | `角色卡/任务工具/memo.md` | 本角色私有工作备忘录 |
| 单文件 | `角色卡/任务工具/docs/feature/task-authority.md` | 任务工具当前行为与状态流程说明 |
| 单文件 | `角色卡/任务工具/docs/change/2026-10-19_change_task-authority.md` | 本轮任务工具职责与实现变更记录 |

未列路径默认只读。本边界不授权其他测试文件、技能规范、调度记录、验收文档、Dashboard 或业务模块。`scripts/tests/test_role_authority_flow.py` 归固定测试角色独占；工具的单元测试不构成独立测试或最终验收。
