/**
 * 计时器实现（基于 performance.now）
 * 主拥有者: 主循环
 */

import { Timer } from '../../abstract/timer';

/** 使用 performance.now 的高精度计时器 */
export class PerformanceTimer implements Timer {
  private startTimeInMs: number = 0;
  private lastTickTimeInMs: number = 0;
  private pauseOffsetInMs: number = 0;
  private pauseStartTimeInMs: number = 0;
  private running: boolean = false;
  private deltaTimeInSeconds: number = 0;
  private elapsedTimeInSeconds: number = 0;
  private frameCount: number = 0;

  /** 获取当前时间戳（毫秒） */
  private getNow(): number {
    return performance.now();
  }

  start(): void {
    if (this.running) {
      return;
    }
    const now: number = this.getNow();
    this.startTimeInMs = now;
    this.lastTickTimeInMs = now;
    this.pauseOffsetInMs = 0;
    this.pauseStartTimeInMs = 0;
    this.deltaTimeInSeconds = 0;
    this.elapsedTimeInSeconds = 0;
    this.frameCount = 0;
    this.running = true;
  }

  stop(): void {
    if (!this.running) {
      return;
    }
    this.running = false;
    if (this.pauseStartTimeInMs > 0) {
      this.pauseOffsetInMs += this.getNow() - this.pauseStartTimeInMs;
      this.pauseStartTimeInMs = 0;
    }
  }

  reset(): void {
    this.startTimeInMs = 0;
    this.lastTickTimeInMs = 0;
    this.pauseOffsetInMs = 0;
    this.pauseStartTimeInMs = 0;
    this.deltaTimeInSeconds = 0;
    this.elapsedTimeInSeconds = 0;
    this.frameCount = 0;
    this.running = false;
  }

  tick(): number {
    if (!this.running) {
      return 0;
    }

    const now: number = this.getNow();
    if (this.lastTickTimeInMs === 0) {
      this.lastTickTimeInMs = now;
      return 0;
    }

    const rawDelta: number = now - this.lastTickTimeInMs;
    this.lastTickTimeInMs = now;

    // 限制最大 deltaTime 为 1 秒，防止长时间暂停后出现时间爆炸
    const clampedDelta: number = Math.min(rawDelta, 1000);
    this.deltaTimeInSeconds = clampedDelta / 1000;
    this.elapsedTimeInSeconds = (now - this.startTimeInMs - this.pauseOffsetInMs) / 1000;
    this.frameCount += 1;

    return this.deltaTimeInSeconds;
  }

  getDeltaTime(): number {
    return this.deltaTimeInSeconds;
  }

  getElapsedTime(): number {
    if (!this.running) {
      return this.elapsedTimeInSeconds;
    }
    const now: number = this.getNow();
    return (now - this.startTimeInMs - this.pauseOffsetInMs) / 1000;
  }

  getFrameCount(): number {
    return this.frameCount;
  }

  isRunning(): boolean {
    return this.running;
  }
}