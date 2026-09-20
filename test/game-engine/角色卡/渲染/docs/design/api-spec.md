# 渲染模块 API 规范

## 类型定义 (`src/models/render.ts`)

### 基础类型

```
Vector2    { x: number, y: number }
Transform  { position: Vector2, rotation: number, scale: Vector2 }
Texture    { key: string, width: number, height: number, source: HTMLImageElement | HTMLCanvasElement }
Color      { r: number, g: number, b: number, a: number }
Rect       { x: number, y: number, width: number, height: number }
Camera     { position: Vector2, zoom: number, viewport: Rect }
```

### 渲染特定类型

```
SpriteData {
  textureKey: string
  sourceRect: Rect
  destRect: Rect
  transform: Transform
  color: Color
  layer: number
}

RenderCommand {
  type: RenderCommandType
  layer: number
  data: SpriteData | Rect | string
  color?: Color
}

RenderCommandType = Clear | Sprite | Rect | Text

RenderStats {
  drawCalls: number
  spriteCount: number
  textureCount: number
  frameTime: number
  culledCount: number
}
```

---

## Renderer 接口 (`src/providers/abstract/renderer.ts`)

| 方法 | 参数 | 返回值 | 说明 |
|------|------|--------|------|
| `initialize` | `canvas: HTMLCanvasElement` | `void` | 使用指定 canvas 初始化渲染器 |
| `beginFrame` | `camera: Camera` | `void` | 开始新帧，设置相机变换 |
| `endFrame` | - | `void` | 结束当前帧，提交所有绘制 |
| `clear` | `color: Color` | `void` | 用纯色清空画布 |
| `drawSprite` | `sprite: SpriteData` | `void` | 绘制单个精灵 |
| `drawRect` | `rect: Rect, color: Color` | `void` | 绘制填充矩形 |
| `drawTexture` | `texture: Texture, dest: Rect, source?: Rect` | `void` | 绘制纹理到目标区域 |
| `getStats` | - | `RenderStats` | 获取当前帧渲染统计 |
| `destroy` | - | `void` | 销毁渲染器，释放资源 |

---

## CanvasRenderer (`src/providers/impl/render/canvas.renderer.ts`)

构造函数: `new CanvasRenderer(config?: CanvasRendererConfig)`

```
CanvasRendererConfig {
  clearColor: Color       // 默认清空颜色
  enableBatch: boolean    // 是否启用批处理，默认 true
}
```

额外属性:
- `textures: TextureManager` — 纹理管理器引用

---

## TextureManager (`src/providers/impl/render/texture.ts`)

| 方法 | 参数 | 返回值 | 说明 |
|------|------|--------|------|
| `load` | `key: string, source: string \| HTMLImageElement \| HTMLCanvasElement` | `Promise<Texture>` | 加载纹理（已缓存则直接返回） |
| `get` | `key: string` | `Texture \| undefined` | 获取已缓存的纹理 |
| `has` | `key: string` | `boolean` | 检查纹理是否已缓存 |
| `remove` | `key: string` | `void` | 移除指定纹理 |
| `clear` | - | `void` | 清空所有缓存 |
| `size` | (getter) | `number` | 当前缓存纹理数量 |

---

## SpriteBatcher (`src/providers/impl/render/sprite.batcher.ts`)

| 方法 | 参数 | 返回值 | 说明 |
|------|------|--------|------|
| `add` | `sprite: SpriteData` | `void` | 向队列添加精灵 |
| `addSimple` | `textureKey, destRect, layer?, color?` | `void` | 快速添加精灵（默认白色、不变换） |
| `flush` | - | `readonly SpriteBatch[]` | 排序并生成批次 |
| `clear` | - | `void` | 清空队列 |
| `queuedCount` | (getter) | `number` | 当前队列精灵数量 |

`SpriteBatch`:
```
SpriteBatch {
  textureKey: string
  sprites: readonly SpriteData[]
  layer: number
}
```

---

## RenderPipeline (`src/pipelines/render/render.pipeline.ts`)

构造函数: `new RenderPipeline(renderer: Renderer, config: RenderPipelineConfig)`

| 方法 | 参数 | 返回值 | 说明 |
|------|------|--------|------|
| `updateConfig` | `config: Partial<RenderPipelineConfig>` | `void` | 更新管线配置 |
| `beginFrame` | `camera?: Camera` | `void` | 开始新帧（清空队列，清空画布） |
| `submitCommand` | `command: RenderCommand` | `void` | 提交渲染命令 |
| `submitSprite` | `sprite: SpriteData` | `void` | 提交精灵绘制 |
| `submitRect` | `rect: Rect, color: Color, layer?: number` | `void` | 提交矩形绘制 |
| `endFrame` | - | `void` | 结束帧，按图层排序并执行命令 |
| `getStats` | - | `RenderStats` | 获取当前帧统计 |
| `destroy` | - | `void` | 销毁管线 |
| `totalFrames` | (getter) | `number` | 已渲染总帧数 |