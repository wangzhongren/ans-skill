/**
 * 游戏主循环实现
 * 主拥有者: 主循环
 *
 * 驱动游戏帧循环，协调固定时间步长更新和渲染，
 * 管理引擎状态（运行/暂停/停止）和帧率控制。
 */

import { EngineConfig, EngineState, FrameTiming } from '../../models/engine';
import { Timer } from '../../services/abstract/timer';
import { FixedTimestep, FixedTimestepResult } from './fixed.timestep';

/** 游戏循环回调集合 */
export interface GameLoopCallbacks {
  /**
   * 固定时间步长更新回调
   * 在物理/逻辑更新频率下调用
   * @param deltaTime 固定时间步长（秒）
   */
  onFixedUpdate(deltaTime: number): void;

  /**
   * 渲染回调
   * 在每一帧调用
   * @param interpolation 渲染插值因子 [0, 1)
   * @param frameTiming   当前帧时序信息
   */
  onRender(interpolation: number, frameTiming: FrameTiming): void;
}

/** 游戏主循环接口 */
export interface GameLoop {
  /** 启动游戏循环 */
  start(callbacks: GameLoopCallbacks): void;

  /** 停止游戏循环 */
  stop(): void;

  /** 暂停游戏循环 */
  pause(): void;

  /** 恢复运行 */
  resume(): void;

  /** 获取当前引擎状态 */
  getState(): EngineState;

  /** 获取当前帧率估算 */
  getFps(): number;
}

/** 游戏主循环默认实现 */
export class DefaultGameLoop implements GameLoop {
  private config: EngineConfig;
  private timer: Timer;
  private fixedTimestep: FixedTimestep;
  private state: EngineState = EngineState.Stopped;
  private callbacks: GameLoopCallbacks | null = null;
  private animationFrameId: number | null = null;
  private fpsFrameCount: number = 0;
  private fpsAccumulator: number = 0;
  private currentFps: number = 0;

  constructor(config: EngineConfig, timer: Timer, fixedTimestep: FixedTimestep) {
    this.config = config;
    this.timer = timer;
    this.fixedTimestep = fixedTimestep;
  }

  start(callbacks: GameLoopCallbacks): void {
    if (this.state === EngineState.Running) {
      return;
    }

    this.callbacks = callbacks;
    this.state = EngineState.Running;
    this.fpsFrameCount = 0;
    this.fpsAccumulator = 0;
    this.currentFps = 0;

    this.timer.start();
    this.fixedTimestep.reset();
    this.scheduleFrame();
  }

  stop(): void {
    if (this.state === EngineState.Stopped) {
      return;
    }

    this.state = EngineState.Stopped;
    this.timer.stop();

    if (this.animationFrameId !== null) {
      cancelAnimationFrame(this.animationFrameId);
      this.animationFrameId = null;
    }

    this.callbacks = null;
    this.fpsFrameCount = 0;
    this.fpsAccumulator = 0;
    this.currentFps = 0;
  }

  pause(): void {
    if (this.state !== EngineState.Running) {
      return;
    }

    this.state = EngineState.Paused;
    this.timer.stop();

    if (this.animationFrameId !== null) {
      cancelAnimationFrame(this.animationFrameId);
      this.animationFrameId = null;
    }
  }

  resume(): void {
    if (this.state !== EngineState.Paused) {
      return;
    }

    this.state = EngineState.Running;
    this.timer.start();
    this.fixedTimestep.reset();
    this.scheduleFrame();
  }

  getState(): EngineState {
    return this.state;
  }

  getFps(): number {
    return this.currentFps;
  }

  private scheduleFrame(): void {
    if (this.state !== EngineState.Running) {
      return;
    }
    this.animationFrameId = requestAnimationFrame(() => {
      this.frameLoop();
    });
  }

  private frameLoop(): void {
    if (this.state !== EngineState.Running) {
      return;
    }

    try {
      const deltaTime: number = this.timer.tick();
      const elapsedTime: number = this.timer.getElapsedTime();
      const frameCount: number = this.timer.getFrameCount();

      if (deltaTime <= 0) {
        // 首帧或无效 deltaTime，直接调度下一帧
        this.scheduleFrame();
        return;
      }

      // FPS 统计：每秒更新一次
      this.fpsFrameCount += 1;
      this.fpsAccumulator += deltaTime;
      if (this.fpsAccumulator >= 1.0) {
        this.currentFps = Math.round(this.fpsFrameCount / this.fpsAccumulator);
        this.fpsFrameCount = 0;
        this.fpsAccumulator = 0;
      }

      // 固定时间步长更新
      const result: FixedTimestepResult = this.fixedTimestep.update(deltaTime);
      if (this.callbacks) {
        for (let stepIndex: number = 0; stepIndex < result.steps; stepIndex += 1) {
          this.callbacks.onFixedUpdate(this.fixedTimestep.getFixedDeltaTime());
        }

        // 渲染
        const frameTiming: FrameTiming = {
          deltaTime,
          elapsedTime,
          frameCount,
        };
        this.callbacks.onRender(result.interpolation, frameTiming);
      }
    } catch (error) {
      console.error('Game loop frame error:', error);
    }

    this.scheduleFrame();
  }
}