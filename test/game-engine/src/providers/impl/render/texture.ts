// 纹理管理实现
// 职责: 加载、缓存和释放纹理资源

import { Texture } from '../../../models/render';

/** 纹理加载选项 */
export interface TextureLoadOptions {
  readonly key: string;
  readonly source: string | HTMLImageElement | HTMLCanvasElement;
}

/** 纹理管理器 — 管理纹理生命周期与缓存 */
export class TextureManager {
  private readonly cache: Map<string, Texture> = new Map();
  private readonly pendingLoads: Map<string, Promise<Texture>> = new Map();

  /** 当前缓存的纹理数量 */
  get size(): number {
    return this.cache.size;
  }

  /** 加载纹理，若已缓存则直接返回 */
  async load(key: string, source: string | HTMLImageElement | HTMLCanvasElement): Promise<Texture> {
    const cached = this.cache.get(key);
    if (cached !== undefined) {
      return cached;
    }

    const pending = this.pendingLoads.get(key);
    if (pending !== undefined) {
      return pending;
    }

    const loadPromise = this.loadTextureInternal(key, source);
    this.pendingLoads.set(key, loadPromise);

    try {
      const texture = await loadPromise;
      this.cache.set(key, texture);
      return texture;
    } finally {
      this.pendingLoads.delete(key);
    }
  }

  /** 同步获取已缓存的纹理 */
  get(key: string): Texture | undefined {
    return this.cache.get(key);
  }

  /** 检查纹理是否已缓存 */
  has(key: string): boolean {
    return this.cache.has(key);
  }

  /** 移除指定纹理 */
  remove(key: string): void {
    this.cache.delete(key);
  }

  /** 清空所有缓存纹理 */
  clear(): void {
    this.cache.clear();
  }

  /** 内部加载纹理 */
  private loadTextureInternal(
    key: string,
    source: string | HTMLImageElement | HTMLCanvasElement,
  ): Promise<Texture> {
    if (typeof source === 'string') {
      return this.loadFromUrl(key, source);
    }
    return Promise.resolve(this.createTextureFromElement(key, source));
  }

  /** 从 URL 加载图像 */
  private loadFromUrl(key: string, url: string): Promise<Texture> {
    return new Promise<Texture>((resolve, reject) => {
      const image = new Image();
      image.onload = () => {
        resolve({
          key,
          width: image.naturalWidth,
          height: image.naturalHeight,
          source: image,
        });
      };
      image.onerror = () => {
        reject(new Error(`Failed to load texture from URL: ${url}`));
      };
      image.src = url;
    });
  }

  /** 从 HTML 元素创建纹理 */
  private createTextureFromElement(
    key: string,
    element: HTMLImageElement | HTMLCanvasElement,
  ): Texture {
    const width = 'naturalWidth' in element ? element.naturalWidth : element.width;
    const height = 'naturalHeight' in element ? element.naturalHeight : element.height;
    return {
      key,
      width,
      height,
      source: element,
    };
  }
}