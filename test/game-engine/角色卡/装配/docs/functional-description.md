# 装配 — 功能描述

## 概述

装配角色负责将引擎的六个能力角色（实体管理、场景管理、主循环、渲染、输入、音频、资源加载）的产出组合为可运行的引擎系统。提供统一的入口点、公共 API 外观和服务/提供者层统一导出。

## 架构位置

```
main.ts  ← 引擎入口点
  └─ src/interface/engine.ts  ← 引擎公共 API 外观
       ├─ src/services/public/index.ts   ← 服务层统一入口
       └─ src/providers/public/index.ts  ← 提供者层统一入口
```

## 组件说明

### 1. `main.ts` — 引擎入口点

- 监听 `DOMContentLoaded` 事件，确保 DOM 就绪后启动
- 从 `#game-root` 元素的 `data-*` 属性读取配置
- 创建 `GameEngine` 实例并调用 `initialize()` → `start()`
- Debug 模式下将引擎实例暴露到 `window.__engine`

### 2. `src/interface/engine.ts` — 引擎公共 API 外观

**Engine 接口** 定义了引擎对外暴露的完整 API:

| 方法 | 说明 |
|------|------|
| `initialize()` | 初始化所有子系统，按确定顺序创建实例并建立依赖关系 |
| `start()` | 启动游戏主循环 |
| `stop()` | 停止游戏主循环 |
| `pause()` | 暂停游戏循环 |
| `resume()` | 恢复游戏循环 |
| `destroy()` | 销毁引擎，按逆序释放资源 |
| `getState()` | 获取引擎运行状态 |
| `getFps()` | 获取当前帧率 |
| `getEntityService()` | 获取实体管理服务 |
| `getSceneManager()` | 获取场景管理器 |
| `getInputProvider()` | 获取输入提供者 |
| `getAudioProvider()` | 获取音频提供者 |
| `getResourceProvider()` | 获取资源加载提供者 |
| `getRenderPipeline()` | 获取渲染管线 |

**初始化顺序**:

1. 获取 Canvas 元素并设尺寸
2. 创建 CanvasRenderer 并初始化
3. 创建 RenderPipeline（注入 Renderer）
4. 创建 GameEntityService
5. 创建 SceneManagerImpl
6. 创建 PerformanceTimer
7. 创建 FixedTimestep
8. 创建 BrowserInputProvider 并初始化
9. 创建 GameAudioProvider 并初始化
10. 创建 GameResourceLoader（注入 ImageLoader、AudioLoader、DataLoader）
11. 创建 DefaultGameLoop（注入 EngineConfig、Timer、FixedTimestep）
12. 加载初始资源清单（可选）

**游戏循环回调**:

- `onFixedUpdate`: 驱动场景管理器 `update(dt)` 更新
- `onRender`: 驱动渲染管线 `beginFrame()` → `endFrame()`

### 3. `src/services/public/index.ts` — 服务层统一入口

导出所有服务的抽象接口和实现:

| 导出 | 类型 | 来源 |
|------|------|------|
| `EntityService` | Interface | services/abstract/entity.ts |
| `GameEntityService` | Class | services/impl/entity/entity.service.ts |
| `SceneManager` | Interface | services/abstract/scene.ts |
| `SceneManagerImpl` | Class | services/impl/scene/scene.manager.ts |
| `Timer` | Interface | services/abstract/timer.ts |
| `PerformanceTimer` | Class | services/impl/timer/timer.ts |

### 4. `src/providers/public/index.ts` — 提供者层统一入口

导出所有提供者的抽象接口和实现:

| 导出 | 类型 | 来源 |
|------|------|------|
| `Renderer` | Interface | providers/abstract/renderer.ts |
| `CanvasRenderer` | Class | providers/impl/render/canvas.renderer.ts |
| `TextureManager` | Class | providers/impl/render/texture.ts |
| `SpriteBatcher` | Class | providers/impl/render/sprite.batcher.ts |
| `InputProvider` | Interface | providers/abstract/input.ts |
| `BrowserInputProvider` | Class | providers/impl/input/input.provider.ts |
| `AudioProvider` | Interface | providers/abstract/audio.ts |
| `GameAudioProvider` | Class | providers/impl/audio/audio.provider.ts |
| `ResourceProvider` | Interface | providers/abstract/resource.ts |
| `GameResourceLoader` | Class | providers/impl/resource/resource.loader.ts |

## 质量约束遵守

- **相邻层合规**: Interface 层通过 Pipeline 的公开导出文件引用 Pipeline 内容
- **无空桩/无 TODO**: 所有方法都有真实实现
- **变量名**: 描述性强，无单/双字母缩写（循环计数器除外）
- **禁止三元运算符**: 使用 `if/else` 替代
- **try/catch**: 每个捕获块都通过 `console.error` 输出错误信息