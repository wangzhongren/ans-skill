// 场景管理器实现
// 主拥有者: 场景管理

import { Scene, SceneState, SceneLifecycle, SceneTransition } from '../../../models/scene';
import { Entity } from '../../../models/ecs';
import { SceneManager } from '../../abstract/scene';
import { SceneImpl } from './scene';

/** 场景管理器实现 —— 管理场景注册、切换、生命周期和帧更新 */
export class SceneManagerImpl implements SceneManager {
  private scenes: Map<string, SceneImpl> = new Map();
  private lifecycles: Map<string, SceneLifecycle> = new Map();
  private activeScene: SceneImpl | null = null;

  createScene(name: string, entities?: Entity[]): Scene {
    if (this.scenes.has(name)) {
      throw new Error(`Scene "${name}" already exists`);
    }
    const scene = new SceneImpl(name, entities);
    this.scenes.set(name, scene);
    return scene;
  }

  registerLifecycle(name: string, lifecycle: SceneLifecycle): void {
    if (!this.scenes.has(name)) {
      throw new Error(`Cannot register lifecycle for unknown scene "${name}"`);
    }
    this.lifecycles.set(name, lifecycle);
  }

  switchScene(name: string, transition?: SceneTransition): void {
    const nextScene = this.scenes.get(name);
    if (!nextScene) {
      throw new Error(`Scene "${name}" not found`);
    }

    // 通知当前场景退出
    if (this.activeScene) {
      const currentLifecycle = this.lifecycles.get(this.activeScene.name);
      if (currentLifecycle) {
        currentLifecycle.onExit();
      }
      this.activeScene.onExit();
    }

    // 进入新场景
    nextScene.onEnter();
    const nextLifecycle = this.lifecycles.get(name);
    if (nextLifecycle) {
      nextLifecycle.onEnter();
    }

    this.activeScene = nextScene;
  }

  getActiveScene(): Scene | null {
    return this.activeScene;
  }

  getScene(name: string): Scene | undefined {
    return this.scenes.get(name);
  }

  destroyScene(name: string): void {
    const scene = this.scenes.get(name);
    if (!scene) {
      return;
    }

    // 如果销毁的是当前活跃场景，清除活跃引用
    if (this.activeScene === scene) {
      this.activeScene = null;
    }

    scene.state = SceneState.Destroyed;
    scene.isActive = false;
    this.scenes.delete(name);
    this.lifecycles.delete(name);
  }

  update(dt: number): void {
    if (!this.activeScene) {
      return;
    }

    // 先驱动注册的生命周期钩子，再驱动场景自身的更新
    const lifecycle = this.lifecycles.get(this.activeScene.name);
    if (lifecycle) {
      lifecycle.onUpdate(dt);
    }
    this.activeScene.onUpdate(dt);
  }
}