// 资源加载提供者契约
// 职责: 定义资源加载器抽象接口，供所有资源加载实现遵循

import {
  type ResourceDescriptor,
  type Resource,
  type ResourceManifest,
  type LoadProgress,
} from '../../models/resource';

/** 资源缓存统计信息 */
export interface ResourceCacheStats {
  readonly totalCached: number;
  readonly totalLoaded: number;
  readonly totalFailed: number;
  readonly totalRequested: number;
}

/** 资源加载提供者抽象接口 */
export interface ResourceProvider {
  /**
   * 加载单个资源
   * @param descriptor 资源描述符
   * @returns 加载完成的资源
   */
  load(descriptor: ResourceDescriptor): Promise<Resource>;

  /**
   * 批量加载资源，支持进度回调
   * @param manifest 资源清单
   * @param onProgress 可选进度回调，每个资源加载完成后触发
   * @returns 所有加载完成的资源数组
   */
  loadMany(
    manifest: ResourceManifest,
    onProgress?: (progress: LoadProgress) => void
  ): Promise<Resource[]>;

  /**
   * 从缓存中获取已加载的资源
   * @param key 资源键名
   * @returns 资源对象，如果未加载则返回 undefined
   */
  get(key: string): Resource | undefined;

  /**
   * 检查资源是否已加载并存在于缓存中
   * @param key 资源键名
   */
  has(key: string): boolean;

  /**
   * 释放指定资源的缓存
   * @param key 资源键名
   */
  release(key: string): void;

  /**
   * 释放所有已加载资源的缓存
   */
  releaseAll(): void;

  /**
   * 获取当前加载进度
   * @returns 加载进度对象
   */
  getProgress(): LoadProgress;

  /**
   * 注册加载进度回调
   * @param callback 进度回调函数
   */
  onProgress(callback: (progress: LoadProgress) => void): void;

  /**
   * 移除加载进度回调
   * @param callback 要移除的进度回调函数
   */
  offProgress(callback: (progress: LoadProgress) => void): void;

  /**
   * 获取资源缓存统计信息
   * @returns 缓存统计对象
   */
  getStats(): ResourceCacheStats;

  /**
   * 获取已加载的资源总数
   * @returns 成功加载的资源数量
   */
  getLoadedCount(): number;

  /**
   * 获取已请求的资源总数
   * @returns 请求加载的资源总数量
   */
  getTotalCount(): number;
}