// 引擎配置类型
// 主拥有者: 装配
// 其他角色以只读方式引用

import { Color } from './render';
import { ResourceManifest } from './resource';

/** 引擎配置 */
export interface EngineConfig {
  readonly canvasId: string;
  readonly width: number;
  readonly height: number;
  readonly backgroundColor?: Color;
  readonly resourceManifest?: ResourceManifest;
  readonly maxFps?: number;
  readonly fixedTimestep?: number;
  readonly debug?: boolean;
}

/** 引擎状态 */
export enum EngineState {
  Stopped = 'stopped',
  Running = 'running',
  Paused = 'paused',
}

/** 帧时序信息 */
export interface FrameTiming {
  readonly deltaTime: number;
  readonly elapsedTime: number;
  readonly frameCount: number;
}