// 资源类型定义
// 主拥有者: 资源加载
// 其他角色以只读方式引用

/** 资源类型枚举 */
export enum ResourceType {
  Image = 'image',
  Audio = 'audio',
  Data = 'data',
  Font = 'font',
}

/** 资源描述符 */
export interface ResourceDescriptor {
  readonly key: string;
  readonly type: ResourceType;
  readonly src: string;
}

/** 已加载的资源 */
export interface Resource<T = unknown> {
  readonly descriptor: ResourceDescriptor;
  readonly data: T;
  readonly loadedAt: number;
}

/** 资源清单 */
export interface ResourceManifest {
  readonly resources: ResourceDescriptor[];
}

/** 加载进度 */
export interface LoadProgress {
  readonly total: number;
  readonly loaded: number;
  readonly failed: number;
  readonly percent: number;
}

/** 资源事件 */
export interface ResourceEvent {
  readonly key: string;
  readonly type: ResourceType;
  readonly success: boolean;
  readonly error?: Error;
}