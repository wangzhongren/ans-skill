# 主循环 — API 规范

## 1. Timer (计时器服务接口)

**路径**: `src/services/abstract/timer.ts`

### Export

```typescript
export interface Timer
```

### Methods

| 方法 | 签名 | 说明 |
|------|------|------|
| `start` | `(): void` | 启动计时器，记录起始时间。已运行时无效果 |
| `stop` | `(): void` | 停止计时器。未运行时无效果 |
| `reset` | `(): void` | 重置所有状态至初始值 |
| `tick` | `(): number` | 推进一帧，返回自上一帧以来的 deltaTime（秒），首帧返回 0 |
| `getDeltaTime` | `(): number` | 获取上一帧的 deltaTime（秒） |
| `getElapsedTime` | `(): number` | 获取自启动以来扣除暂停时间的运行时间（秒） |
| `getFrameCount` | `(): number` | 获取累计帧数 |
| `isRunning` | `(): boolean` | 计时器是否在运行 |

### 实现

**路径**: `src/services/impl/timer/timer.ts`

**类**: `PerformanceTimer implements Timer`

- 使用 `performance.now()` 作为时间源
- deltaTime 上限 1000ms，防止时间爆炸
- 暂停期间累积偏移量，恢复后自动补偿

---

## 2. FixedTimestep (固定时间步长)

**路径**: `src/pipelines/gameloop/fixed.timestep.ts`

### Exports

```typescript
export interface FixedTimestepResult
export class FixedTimestep
```

### FixedTimestepResult

| 字段 | 类型 | 说明 |
|------|------|------|
| `steps` | `number` | 本轮需执行的固定更新步数 |
| `interpolation` | `number` | 渲染插值因子 [0, 1) |

### Constructor

```typescript
constructor(fixedDeltaTime: number, maxFrameTime: number = 0.25)
```

- `fixedDeltaTime`: 每个固定更新的时间步长（秒），必须 > 0
- `maxFrameTime`: 单帧最大可消耗时间（秒），必须 ≥ fixedDeltaTime

### Methods

| 方法 | 签名 | 说明 |
|------|------|------|
| `update` | `(deltaTime: number): FixedTimestepResult` | 累加 deltaTime，返回更新步数和插值因子。负值返回 0 步 |
| `reset` | `(): void` | 重置累加器 |
| `getFixedDeltaTime` | `(): number` | 获取固定时间步长 |
| `getAccumulator` | `(): number` | 获取当前累加器值 |

---

## 3. GameLoop (游戏主循环)

**路径**: `src/pipelines/gameloop/game.loop.ts`

### Exports

```typescript
export interface GameLoopCallbacks
export interface GameLoop
export class DefaultGameLoop
```

### GameLoopCallbacks

| 字段 | 签名 | 说明 |
|------|------|------|
| `onFixedUpdate` | `(dt: number): void` | 固定时间步长更新回调 |
| `onRender` | `(interpolation: number, frameTiming: FrameTiming): void` | 渲染回调 |

### Constructor

```typescript
constructor(config: EngineConfig, timer: Timer, fixedTimestep: FixedTimestep)
```

### Methods

| 方法 | 签名 | 说明 |
|------|------|------|
| `start` | `(callbacks: GameLoopCallbacks): void` | 启动游戏循环。已运行时无效果 |
| `stop` | `(): void` | 停止游戏循环，释放回调引用 |
| `pause` | `(): void` | 暂停游戏循环，停止 requestAnimationFrame。仅 Running 态生效 |
| `resume` | `(): void` | 恢复运行，重新调度帧循环。仅 Paused 态生效 |
| `getState` | `(): EngineState` | 获取当前引擎状态 |
| `getFps` | `(): number` | 获取当前 FPS 估算值（每秒更新） |

### 状态流转

- `EngineState.Stopped` → `start()` → `EngineState.Running`
- `EngineState.Running` → `pause()` → `EngineState.Paused`
- `EngineState.Paused` → `resume()` → `EngineState.Running`
- `EngineState.Running` / `EngineState.Paused` → `stop()` → `EngineState.Stopped`

### 帧循环周期

1. `Timer.tick()` — 获取 deltaTime
2. `FixedTimestep.update(deltaTime)` — 计算固定更新步数
3. 循环调用 `callbacks.onFixedUpdate(fixedDt)` × steps
4. 调用 `callbacks.onRender(interpolation, frameTiming)` — 渲染帧
5. `requestAnimationFrame` 调度下一帧

异常保护：每帧由 try/catch 包裹，捕获的错误通过 `console.error` 输出。