# Section 1: 可修改的文件

| 类型 | 路径 | 功能 |
| --- | --- | --- |
| 单文件 | `main.ts` | 引擎入口点和系统启动 |
| 单文件 | `src/interface/engine.ts` | 引擎公共 API 外观 |
| 单文件 | `src/services/public/index.ts` | Service 层统一入口 |
| 单文件 | `src/providers/public/index.ts` | Provider 层统一入口 |
| 单文件 | `src/models/engine.ts` | 引擎配置类型（主拥有者） |
| 条件文件 | `角色卡/装配/docs/` | 任务相关文档 |