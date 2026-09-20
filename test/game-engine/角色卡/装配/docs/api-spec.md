# API 规范: 装配

## 导出

### 引擎外观 (`src/interface/engine.ts`)

| 导出 | 类型 | 说明 |
| --- | --- | --- |
| `Engine` | `interface` | 引擎公共接口，定义生命周期和子系统访问 |
| `GameEngine` | `class` | 引擎默认实现，组合所有子系统 |

#### Engine 接口方法

| 方法 | 签名 | 说明 |
| --- | --- | --- |
| `initialize` | `(): Promise<void>` | 初始化所有子系统 |
| `start` | `(): void` | 启动游戏主循环 |
| `stop` | `(): void` | 停止游戏主循环 |
| `pause` | `(): void` | 暂停游戏循环 |
| `resume` | `(): void` | 恢复游戏循环 |
| `destroy` | `(): Promise<void>` | 销毁引擎，释放所有资源 |
| `getState` | `(): EngineState` | 获取引擎运行状态 |
| `getFps` | `(): number` | 获取当前帧率 |
| `getEntityService` | `(): EntityService` | 获取实体管理服务 |
| `getSceneManager` | `(): SceneManager` | 获取场景管理器 |
| `getInputProvider` | `(): InputProvider` | 获取输入提供者 |
| `getAudioProvider` | `(): AudioProvider` | 获取音频提供者 |
| `getResourceProvider` | `(): ResourceProvider` | 获取资源加载提供者 |
| `getRenderPipeline` | `(): RenderPipeline` | 获取渲染管线 |

### 引擎入口点 (`main.ts`)

| 导出 | 类型 | 说明 |
| --- | --- | --- |
| (模块自执行) | — | 监听 `DOMContentLoaded`，读取 `#game-root` 配置，启动引擎 |

### 服务层统一入口 (`src/services/public/index.ts`)

| 导出 | 类型 | 说明 |
| --- | --- | --- |
| `EntityService` | `interface` | 实体管理服务契约 |
| `GameEntityService` | `class` | 实体管理服务实现 |
| `SceneManager` | `interface` | 场景管理器契约 |
| `SceneManagerImpl` | `class` | 场景管理器实现 |
| `Timer` | `interface` | 计时器服务契约 |
| `PerformanceTimer` | `class` | 计时器实现 |

### 提供者层统一入口 (`src/providers/public/index.ts`)

| 导出 | 类型 | 说明 |
| --- | --- | --- |
| `Renderer` | `interface` | 渲染器契约 |
| `CanvasRenderer` | `class` | Canvas 渲染器实现 |
| `CanvasRendererConfig` | `interface` | Canvas 渲染器配置 |
| `TextureManager` | `class` | 纹理管理器 |
| `TextureLoadOptions` | `interface` | 纹理加载选项 |
| `SpriteBatcher` | `class` | 精灵批处理器 |
| `SpriteBatch` | `interface` | 批处理批次 |
| `InputProvider` | `interface` | 输入提供者契约 |
| `InputEventHandler` | `type` | 输入事件处理器签名 |
| `BrowserInputProvider` | `class` | 浏览器输入提供者 |
| `AudioProvider` | `interface` | 音频提供者契约 |
| `GameAudioProvider` | `class` | 音频提供者实现 |
| `ResourceProvider` | `interface` | 资源加载提供者契约 |
| `ResourceCacheStats` | `interface` | 资源缓存统计 |
| `GameResourceLoader` | `class` | 资源加载器 |
| `ImageLoader` | `class` | 图片加载器 |
| `AudioLoader` | `class` | 音频加载器 |
| `DataLoader` | `class` | 数据加载器 |

### 引擎模型 (`src/models/engine.ts`)

| 导出 | 类型 | 说明 |
| --- | --- | --- |
| `EngineConfig` | `interface` | 引擎配置 |
| `EngineState` | `enum` | 引擎运行状态枚举 |
| `FrameTiming` | `interface` | 帧时序信息 |

## 依赖关系

```
main.ts
  └─ src/interface/engine.ts
       ├─ src/models/engine.ts          (引擎配置类型)
       ├─ src/models/render.ts          (渲染配置类型)
       ├─ src/pipelines/render/render.pipeline.ts  (渲染管线)
       ├─ src/pipelines/gameloop/game.loop.ts      (游戏主循环)
       ├─ src/pipelines/gameloop/fixed.timestep.ts (固定时间步长)
       ├─ src/services/public/index.ts  (服务层)
       └─ src/providers/public/index.ts (提供者层)
```

## 装配说明

### 基本用法

```typescript
import { GameEngine } from './src/interface/engine';
import { EngineConfig } from './src/models/engine';

const config: EngineConfig = {
  canvasId: 'game-canvas',
  width: 800,
  height: 600,
  backgroundColor: { r: 0, g: 0, b: 0, a: 255 },
  fixedTimestep: 1 / 60,
};

const engine = new GameEngine(config);

async function main(): Promise<void> {
  await engine.initialize();
  engine.start();

  // 游戏中暂停
  // engine.pause();

  // 恢复
  // engine.resume();

  // 停止
  // engine.stop();

  // 销毁
  // await engine.destroy();
}

main().catch(console.error);
```

### HTML 模板

```html
<div id="game-root"
     data-canvas-id="game-canvas"
     data-width="800"
     data-height="600"
     data-debug="true">
  <canvas id="game-canvas"></canvas>
</div>
<script src="main.ts" type="module"></script>
```

### 子系统访问

```typescript
const engine = new GameEngine(config);
await engine.initialize();
engine.start();

// 访问子系统
const entities = engine.getEntityService();
const scenes = engine.getSceneManager();
const input = engine.getInputProvider();
const audio = engine.getAudioProvider();
const resources = engine.getResourceProvider();
const renderer = engine.getRenderPipeline();
```