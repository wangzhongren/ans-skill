// 实体与组件类型定义
// 主拥有者: 实体管理
// 其他角色以只读方式引用

/** 实体唯一标识 */
export type EntityId = number;

/** 组件接口 */
export interface Component {
  readonly type: string;
}

/** 实体 */
export interface Entity {
  readonly id: EntityId;
  readonly components: Map<string, Component>;
  readonly createdAt: number;
  alive: boolean;
}

/** 实体生命周期事件类型 */
export enum EntityEventType {
  Created = 'entity:created',
  Destroyed = 'entity:destroyed',
  ComponentAdded = 'component:added',
  ComponentRemoved = 'component:removed',
}

/** 实体事件基础接口 */
export interface EntityEvent {
  readonly type: EntityEventType;
  readonly entityId: EntityId;
  readonly timestamp: number;
}

/** 组件变更事件 */
export interface ComponentEvent extends EntityEvent {
  readonly componentType: string;
}

/** 实体事件处理器 */
export type EntityEventHandler = (event: EntityEvent | ComponentEvent) => void;

/** 组件查询条件 */
export interface ComponentQuery {
  readonly allOf?: readonly string[];
  readonly anyOf?: readonly string[];
  readonly noneOf?: readonly string[];
}