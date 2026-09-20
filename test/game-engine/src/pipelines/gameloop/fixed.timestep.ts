/**
 * 固定时间步长更新
 * 主拥有者: 主循环
 *
 * 使用累加器模式实现固定时间步长更新，
 * 确保物理/逻辑更新以稳定的频率执行，与渲染帧率解耦。
 */

/** 固定时间步长更新结果 */
export interface FixedTimestepResult {
  /** 本轮需要执行的固定更新步数 */
  readonly steps: number;
  /** 当前帧的插值因子 [0, 1)，用于渲染预测 */
  readonly interpolation: number;
}

/** 固定时间步长累加器 */
export class FixedTimestep {
  private fixedDeltaTime: number;
  private accumulator: number = 0;
  private maxFrameTime: number;

  /**
   * @param fixedDeltaTime 每个固定更新的时间步长（秒），例如 1/60
   * @param maxFrameTime   单帧最大可消耗时间（秒），防止螺旋死锁，默认 0.25
   */
  constructor(fixedDeltaTime: number, maxFrameTime: number = 0.25) {
    if (fixedDeltaTime <= 0) {
      throw new Error(`fixedDeltaTime must be positive, got ${fixedDeltaTime}`);
    }
    if (maxFrameTime <= 0) {
      throw new Error(`maxFrameTime must be positive, got ${maxFrameTime}`);
    }
    if (maxFrameTime < fixedDeltaTime) {
      throw new Error(
        `maxFrameTime (${maxFrameTime}) must not be less than fixedDeltaTime (${fixedDeltaTime})`
      );
    }
    this.fixedDeltaTime = fixedDeltaTime;
    this.maxFrameTime = maxFrameTime;
  }

  /**
   * 向累加器添加 deltaTime 并计算需要执行的固定更新步数
   * @param deltaTime 当前帧的增量时间（秒）
   * @returns 固定更新步数和插值因子
   */
  update(deltaTime: number): FixedTimestepResult {
    if (deltaTime < 0) {
      return { steps: 0, interpolation: 0 };
    }

    // 限制单帧最大时间，防止长时间暂停后一次性执行大量更新
    const clampedDelta: number = Math.min(deltaTime, this.maxFrameTime);
    this.accumulator += clampedDelta;

    const steps: number = Math.floor(this.accumulator / this.fixedDeltaTime);

    if (steps > 0) {
      this.accumulator -= steps * this.fixedDeltaTime;
    }

    const interpolation: number = this.accumulator / this.fixedDeltaTime;

    return { steps, interpolation };
  }

  /** 重置累加器 */
  reset(): void {
    this.accumulator = 0;
  }

  /** 获取固定时间步长 */
  getFixedDeltaTime(): number {
    return this.fixedDeltaTime;
  }

  /** 获取当前累加器值 */
  getAccumulator(): number {
    return this.accumulator;
  }
}