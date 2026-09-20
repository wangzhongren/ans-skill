// 数据资源加载器
// 负责加载数据类型的资源，支持 JSON 和文本格式

import {
  type ResourceDescriptor,
  ResourceType,
} from '../../../models/resource';
import { type ResourceDataLoader } from './resource.loader';

/** 数据文件格式 */
enum DataFormat {
  Json = 'json',
  Text = 'text',
  Unknown = 'unknown',
}

/**
 * 数据资源加载器
 *
 * 使用 Fetch API 加载 JSON 和文本数据资源。根据文件扩展名自动
 * 推断数据格式，也支持通过资源键名的前缀约定指定格式。
 */
export class DataLoader implements ResourceDataLoader {
  readonly type: ResourceType = ResourceType.Data;

  /**
   * 加载数据资源
   * @param descriptor 资源描述符
   * @returns 解析后的数据（JSON 对象或文本字符串）
   */
  async load(descriptor: ResourceDescriptor): Promise<unknown> {
    try {
      const response = await fetch(descriptor.src);

      if (!response.ok) {
        throw new Error(
          `HTTP ${response.status}: ${response.statusText}`
        );
      }

      const format = this.detectFormat(descriptor.src);

      if (format === DataFormat.Json) {
        return await response.json();
      }

      return await response.text();
    } catch (error) {
      throw new Error(
        `Failed to load data resource "${descriptor.key}" from "${descriptor.src}": ${error instanceof Error ? error.message : 'Unknown error'}`
      );
    }
  }

  /**
   * 释放数据资源
   * @param _data 数据（无需特定释放操作）
   */
  release(_data: unknown): void {
    // 数据资源（JSON/文本）不需要特定的释放操作，
    // 垃圾回收器会自动回收内存
  }

  /**
   * 根据文件路径推断数据格式
   */
  private detectFormat(src: string): DataFormat {
    const lower = src.toLowerCase();

    if (lower.endsWith('.json')) {
      return DataFormat.Json;
    }

    if (
      lower.endsWith('.txt') ||
      lower.endsWith('.csv') ||
      lower.endsWith('.xml') ||
      lower.endsWith('.yaml') ||
      lower.endsWith('.yml')
    ) {
      return DataFormat.Text;
    }

    return DataFormat.Unknown;
  }
}