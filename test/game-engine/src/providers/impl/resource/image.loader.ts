// 图片资源加载器
// 负责加载图片类型的资源，返回 HTMLImageElement

import {
  type ResourceDescriptor,
  ResourceType,
} from '../../../models/resource';
import { type ResourceDataLoader } from './resource.loader';

/**
 * 图片资源加载器
 *
 * 使用 HTML Image 对象加载图片资源，加载完成后返回 HTMLImageElement。
 * 支持跨域图片加载，默认启用匿名跨域模式。
 */
export class ImageLoader implements ResourceDataLoader {
  readonly type: ResourceType = ResourceType.Image;

  /**
   * 加载图片资源
   * @param descriptor 资源描述符
   * @returns 加载完成的 HTMLImageElement
   */
  load(descriptor: ResourceDescriptor): Promise<unknown> {
    return new Promise<HTMLImageElement>((resolve, reject) => {
      const image = new Image();

      // 启用跨域支持
      image.crossOrigin = 'anonymous';

      image.onload = () => {
        resolve(image);
      };

      image.onerror = () => {
        reject(
          new Error(
            `Failed to load image resource "${descriptor.key}" from "${descriptor.src}"`
          )
        );
      };

      image.src = descriptor.src;
    });
  }

  /**
   * 释放图片资源
   * @param data 图片数据（HTMLImageElement）
   */
  release(data: unknown): void {
    // HTMLImageElement 没有特定的释放方法，
    // 将 src 置空以帮助垃圾回收
    const image = data as HTMLImageElement;
    image.src = '';
  }
}