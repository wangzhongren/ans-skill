// 场景类型定义
// 主拥有者: 场景管理
// 其他角色以只读方式引用

import { Entity } from './ecs';

/** 场景生命周期状态 */
export enum SceneState {
  Loading = 'loading',
  Active = 'active',
  Inactive = 'inactive',
  Destroyed = 'destroyed',
}

/** 场景 */
export interface Scene {
  readonly name: string;
  readonly entities: Entity[];
  state: SceneState;
  isActive: boolean;
}

/** 场景生命周期钩子 */
export interface SceneLifecycle {
  onEnter(): void;
  onExit(): void;
  onUpdate(dt: number): void;
}

/** 场景切换参数 */
export interface SceneTransition {
  readonly from: string;
  readonly to: string;
  readonly duration?: number;
}