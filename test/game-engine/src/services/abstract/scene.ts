// 场景管理服务契约
// 主拥有者: 场景管理
// 其他角色以只读方式引用

import { Scene, SceneLifecycle, SceneTransition } from '../../models/scene';
import { Entity } from '../../models/ecs';

/** 场景管理器 —— 管理场景的创建、切换、生命周期和状态跟踪 */
export interface SceneManager {
  /** 创建一个新场景 */
  createScene(name: string, entities?: Entity[]): Scene;

  /** 为指定场景注册生命周期钩子 */
  registerLifecycle(name: string, lifecycle: SceneLifecycle): void;

  /** 切换到指定场景，支持可选的过渡参数 */
  switchScene(name: string, transition?: SceneTransition): void;

  /** 获取当前活跃场景，无活跃场景时返回 null */
  getActiveScene(): Scene | null;

  /** 按名称查找场景 */
  getScene(name: string): Scene | undefined;

  /** 销毁指定场景并清理资源 */
  destroyScene(name: string): void;

  /** 驱动当前活跃场景的帧更新 */
  update(dt: number): void;
}