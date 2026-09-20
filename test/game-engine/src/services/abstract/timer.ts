/**
 * 计时器服务契约
 * 主拥有者: 主循环
 * 提供帧时序测量和时间追踪功能
 */

/** 计时器服务接口 */
export interface Timer {
  /** 启动计时器，记录起始时间 */
  start(): void;

  /** 停止计时器 */
  stop(): void;

  /** 重置计时器所有状态 */
  reset(): void;

  /**
   * 推进一帧，计算当前帧的 deltaTime（秒）
   * 应在每帧开始时调用一次
   * @returns 自上一帧以来的秒数
   */
  tick(): number;

  /** 获取上一帧的 deltaTime（秒） */
  getDeltaTime(): number;

  /** 获取自启动以来的总运行时间（秒），暂停期间不计入 */
  getElapsedTime(): number;

  /** 获取累计帧数 */
  getFrameCount(): number;

  /** 计时器是否正在运行 */
  isRunning(): boolean;
}