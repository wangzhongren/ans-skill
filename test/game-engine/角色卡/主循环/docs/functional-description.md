# 主循环 — 功能描述

## 概述

主循环模块是游戏引擎的核心驱动层，负责管理每一帧的时序、调度逻辑更新和渲染。它确保游戏以稳定的节奏运行，将帧率波动与物理/逻辑更新频率解耦。

## 架构位置

```
Pipeline 层（主循环）
 ├── FixedTimestep    ← 累加器模式固定步长
 └── GameLoop         ← 帧循环调度器
        │
Service 层（主循环）
 └── Timer            ← 帧时序测量
```

## 核心概念

### 1. 计时器 (Timer)
使用 `performance.now()` 提供高精度帧时序测量。支持启动、停止、重置，暂停期间的时间不计入运行时间，保证 `getElapsedTime()` 只反映实际运行时长。

### 2. 固定时间步长 (Fixed Timestep)
累加器模式将不稳定的帧 deltaTime 转换为稳定的固定步长更新。每帧计算：
- **steps**: 需要执行的更新次数
- **interpolation**: 渲染插值因子，用于在两次固定更新之间平滑渲染

最大帧时间限制（默认 250ms）防止螺旋死锁。

### 3. 游戏主循环 (Game Loop)
基于 `requestAnimationFrame` 驱动，每帧工作流程：
1. 调用 `Timer.tick()` 获取 deltaTime
2. 将 deltaTime 输入 `FixedTimestep` 计算更新步数
3. 循环调用 `onFixedUpdate(dt)` 执行所有固定更新
4. 调用 `onRender(interpolation, frameTiming)` 执行渲染
5. 调度下一帧

## 状态流转

```
Stopped → start() → Running → pause() → Paused
                        ↑                    ↓
                        └── resume() ←───────┘
Stopped ← stop() ← Running
Stopped ← stop() ← Paused
```

## 边界与依赖

| 方向 | 依赖 | 方式 |
|------|------|------|
| 引用 | `src/models/engine.ts` (EngineConfig, EngineState, FrameTiming) | 只读导入 |
| 管理 | 计时器服务 | 通过接口注入 |
| 管理 | 固定时间步长 | 通过类引用 |
| 回调 | 更新/渲染逻辑 | 外部注册回调 |