# Section 1: 可修改的文件

| 类型 | 路径 | 功能 |
| --- | --- | --- |
| 单文件 | `src/providers/abstract/renderer.ts` | 渲染提供者契约 |
| 单文件 | `src/providers/impl/render/canvas.renderer.ts` | Canvas 渲染器实现 |
| 单文件 | `src/providers/impl/render/texture.ts` | 纹理管理实现 |
| 单文件 | `src/providers/impl/render/sprite.batcher.ts` | 精灵批处理实现 |
| 单文件 | `src/pipelines/render/render.pipeline.ts` | 渲染管线 |
| 单文件 | `src/models/render.ts` | 渲染类型定义（主拥有者） |
| 条件文件 | `角色卡/渲染/docs/` | 任务相关文档 |