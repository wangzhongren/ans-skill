// 资源加载器实现
// 实现 src/providers/abstract/resource.ts 中定义的 ResourceProvider 接口

import {
  type ResourceDescriptor,
  type Resource,
  type ResourceManifest,
  type LoadProgress,
  ResourceType,
} from '../../../models/resource';
import {
  type ResourceProvider,
  type ResourceCacheStats,
} from '../../abstract/resource';

/** 资源加载器的内部接口，每种资源类型实现各自的加载逻辑 */
export interface ResourceDataLoader {
  readonly type: ResourceType;
  load(descriptor: ResourceDescriptor): Promise<unknown>;
  release(data: unknown): void;
}

/**
 * 游戏资源加载器
 *
 * 协调多种资源加载器（图片、音频、数据），统一管理资源缓存、
 * 加载进度通知和资源释放。外部通过 ResourceProvider 接口使用。
 */
export class GameResourceLoader implements ResourceProvider {
  /** 已加载资源的缓存: key -> Resource */
  private readonly cache: Map<string, Resource>;

  /** 类型到加载器的映射 */
  private readonly loaders: Map<ResourceType, ResourceDataLoader>;

  /** 进度回调集合 */
  private readonly progressCallbacks: Set<(progress: LoadProgress) => void>;

  /** 统计信息 */
  private totalRequested: number;
  private totalLoaded: number;
  private totalFailed: number;

  constructor(loaders: ResourceDataLoader[]) {
    this.cache = new Map<string, Resource>();
    this.loaders = new Map<ResourceType, ResourceDataLoader>();
    this.progressCallbacks = new Set<(progress: LoadProgress) => void>();
    this.totalRequested = 0;
    this.totalLoaded = 0;
    this.totalFailed = 0;

    for (const loader of loaders) {
      this.loaders.set(loader.type, loader);
    }
  }

  /**
   * 加载单个资源
   */
  async load(descriptor: ResourceDescriptor): Promise<Resource> {
    // 检查缓存，避免重复加载
    const cached = this.cache.get(descriptor.key);
    if (cached !== undefined) {
      return cached;
    }

    const loader = this.loaders.get(descriptor.type);
    if (loader === undefined) {
      this.totalRequested++;
      this.totalFailed++;
      this.notifyProgress();
      throw new Error(
        `No resource loader registered for type: ${descriptor.type}`
      );
    }

    this.totalRequested++;

    try {
      const data = await loader.load(descriptor);

      const resource: Resource = {
        descriptor,
        data,
        loadedAt: Date.now(),
      };

      this.cache.set(descriptor.key, resource);
      this.totalLoaded++;
      this.notifyProgress();

      return resource;
    } catch (error) {
      this.totalFailed++;
      this.notifyProgress();
      throw error;
    }
  }

  /**
   * 批量加载资源，支持进度回调
   */
  async loadMany(
    manifest: ResourceManifest,
    onProgress?: (progress: LoadProgress) => void
  ): Promise<Resource[]> {
    if (onProgress !== undefined) {
      this.onProgress(onProgress);
    }

    const results: Resource[] = [];
    const errors: Error[] = [];

    for (const descriptor of manifest.resources) {
      try {
        const resource = await this.load(descriptor);
        results.push(resource);
      } catch (error) {
        errors.push(error as Error);
      }
    }

    if (onProgress !== undefined) {
      this.offProgress(onProgress);
    }

    if (errors.length > 0) {
      const messages = errors
        .map((error) => error.message)
        .join('; ');
      throw new Error(
        `Failed to load ${errors.length} resource(s): ${messages}`
      );
    }

    return results;
  }

  /**
   * 从缓存中获取已加载的资源
   */
  get(key: string): Resource | undefined {
    return this.cache.get(key);
  }

  /**
   * 检查资源是否已加载并存在于缓存中
   */
  has(key: string): boolean {
    return this.cache.has(key);
  }

  /**
   * 释放指定资源的缓存
   */
  release(key: string): void {
    const resource = this.cache.get(key);
    if (resource === undefined) {
      return;
    }

    const loader = this.loaders.get(resource.descriptor.type);
    if (loader !== undefined) {
      try {
        loader.release(resource.data);
      } catch (error) {
        console.error(
          `Failed to release resource data for key "${key}": ${error}`
        );
      }
    }

    this.cache.delete(key);
    this.totalLoaded--;
    this.notifyProgress();
  }

  /**
   * 释放所有已加载资源的缓存
   */
  releaseAll(): void {
    const keys = Array.from(this.cache.keys());
    for (const key of keys) {
      this.release(key);
    }
  }

  /**
   * 获取当前加载进度
   */
  getProgress(): LoadProgress {
    return {
      total: this.totalRequested,
      loaded: this.totalLoaded,
      failed: this.totalFailed,
      percent:
        this.totalRequested > 0
          ? Math.round(
              ((this.totalLoaded + this.totalFailed) / this.totalRequested) *
                100
            )
          : 0,
    };
  }

  /**
   * 注册加载进度回调
   */
  onProgress(callback: (progress: LoadProgress) => void): void {
    this.progressCallbacks.add(callback);
  }

  /**
   * 移除加载进度回调
   */
  offProgress(callback: (progress: LoadProgress) => void): void {
    this.progressCallbacks.delete(callback);
  }

  /**
   * 获取资源缓存统计信息
   */
  getStats(): ResourceCacheStats {
    return {
      totalCached: this.cache.size,
      totalLoaded: this.totalLoaded,
      totalFailed: this.totalFailed,
      totalRequested: this.totalRequested,
    };
  }

  /**
   * 获取已加载的资源总数
   */
  getLoadedCount(): number {
    return this.totalLoaded;
  }

  /**
   * 获取已请求的资源总数
   */
  getTotalCount(): number {
    return this.totalRequested;
  }

  /**
   * 通知所有已注册的进度回调
   */
  private notifyProgress(): void {
    const progress = this.getProgress();
    for (const callback of this.progressCallbacks) {
      try {
        callback(progress);
      } catch (error) {
        console.error(
          `Error in resource progress callback: ${error}`
        );
      }
    }
  }
}