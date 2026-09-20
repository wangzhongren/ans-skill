// 场景实现
// 主拥有者: 场景管理

import { Scene as SceneModel, SceneState, SceneLifecycle } from '../../../models/scene';
import { Entity } from '../../../models/ecs';

/** 场景实现类 —— 同时实现 Scene 数据模型和 SceneLifecycle 钩子 */
export class SceneImpl implements SceneModel, SceneLifecycle {
  readonly name: string;
  readonly entities: Entity[];
  state: SceneState;
  isActive: boolean;

  constructor(name: string, entities: Entity[] = []) {
    this.name = name;
    this.entities = entities;
    this.state = SceneState.Inactive;
    this.isActive = false;
  }

  onEnter(): void {
    this.state = SceneState.Active;
    this.isActive = true;
  }

  onExit(): void {
    this.state = SceneState.Inactive;
    this.isActive = false;
  }

  onUpdate(dt: number): void {
    // 场景帧更新：由场景管理器在帧循环中驱动
    // 子类可覆写此方法添加自定义逻辑
  }
}