# 渲染模块功能描述

## 概述

渲染模块负责 2D 图形渲染，提供 Canvas/WebGL 渲染器抽象、渲染管线、纹理管理和精灵绘制能力。采用分层架构：Model 定义类型 -> Provider 提供实现 -> Pipeline 编排流程。

## 模块组成

### 1. 渲染类型定义 (`src/models/render.ts`)

定义渲染系统核心类型：
- **Vector2 / Transform** — 2D 空间变换基础
- **Texture / Color / Rect** — 纹理、颜色、矩形区域
- **Camera** — 视口相机（位置、缩放、视口）
- **SpriteData** — 精灵实例数据（纹理引用、源/目标区域、变换、颜色、图层）
- **RenderCommand / RenderCommandType** — 渲染命令系统
- **RenderStats** — 渲染统计信息
- **RenderPipelineConfig** — 管线配置

### 2. 渲染提供者契约 (`src/providers/abstract/renderer.ts`)

定义 `Renderer` 抽象接口：
- `initialize()` — 初始化渲染器
- `beginFrame()` / `endFrame()` — 帧生命周期
- `clear()` — 清空画布
- `drawSprite()` — 绘制精灵
- `drawRect()` — 绘制矩形
- `drawTexture()` — 绘制纹理
- `getStats()` — 获取统计
- `destroy()` — 释放资源

### 3. Canvas 渲染器 (`src/providers/impl/render/canvas.renderer.ts`)

基于 Canvas 2D API 的渲染器实现：
- 支持批处理模式与非批处理模式
- 自动应用相机变换（平移、缩放）
- 维护渲染统计（draw call 数、精灵数、帧耗时）
- 内置颜色到 rgba 字符串转换

### 4. 纹理管理器 (`src/providers/impl/render/texture.ts`)

纹理生命周期管理：
- 异步加载（URL 或 HTML 元素）
- 缓存机制（同级加载去重）
- 查询、移除、清空操作

### 5. 精灵批处理器 (`src/providers/impl/render/sprite.batcher.ts`)

精灵 draw call 合并：
- 按纹理键和图层排序
- 相同纹理+图层的精灵合并为一批
- 提供 `addSimple()` 快速添加接口

### 6. 渲染管线 (`src/pipelines/render/render.pipeline.ts`)

渲染流程编排：
- 管理渲染命令队列
- 按图层排序执行
- 支持 `submitSprite()` / `submitRect()` / `submitCommand()`
- 可更新管线配置（清空颜色、相机等）
- 提供帧统计和总帧数查询