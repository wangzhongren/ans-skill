# 主循环 — 变更日志

## [0.1.0] - 2026-09-18

### 新增

- **计时器服务接口** (`src/services/abstract/timer.ts`)
  - 定义 `Timer` 接口，包含 start、stop、reset、tick、getDeltaTime、getElapsedTime、getFrameCount、isRunning 方法

- **计时器服务实现** (`src/services/impl/timer/timer.ts`)
  - `PerformanceTimer` 类，基于 `performance.now()` 实现高精度帧时序追踪
  - 支持暂停/恢复时的累计偏移补偿
  - deltaTime 上限限制（1秒），防止长时间暂停后时间爆炸

- **固定时间步长更新** (`src/pipelines/gameloop/fixed.timestep.ts`)
  - `FixedTimestep` 类，实现累加器模式的固定时间步长更新
  - 返回固定更新步数和渲染插值因子
  - 最大帧时间限制防止螺旋死锁
  - 参数校验确保 fixedDeltaTime > 0、maxFrameTime > 0

- **游戏主循环** (`src/pipelines/gameloop/game.loop.ts`)
  - `GameLoop` 接口和 `DefaultGameLoop` 实现
  - 基于 `requestAnimationFrame` 驱动帧循环
  - 状态管理：运行 / 暂停 / 停止
  - FPS 统计（每秒更新一次）
  - 协调固定时间步长更新和渲染回调
  - 异常保护：每帧的 try/catch 捕获并输出错误