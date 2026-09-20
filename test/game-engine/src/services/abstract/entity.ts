// 实体管理服务契约
// 定义实体管理服务的公共接口
// 实现: src/services/impl/entity/entity.service.ts

import {
  type Component,
  type ComponentEvent,
  type ComponentQuery,
  type Entity,
  type EntityEvent,
  type EntityEventType,
  type EntityEventHandler,
  type EntityId,
} from '../../models/ecs';

/**
 * 实体管理服务契约
 *
 * 负责游戏实体的创建、销毁、组件增删查，以及实体生命周期。
 * 所有实体管理操作都通过此接口进行。
 */
export interface EntityService {
  /**
   * 创建一个新实体，分配唯一 ID
   * @returns 新创建的实体
   */
  createEntity(): Entity;

  /**
   * 销毁指定实体
   * 从注册表中移除实体并触发销毁事件
   * @param entityId 要销毁的实体 ID
   * @throws 如果实体不存在则抛出错误
   */
  destroyEntity(entityId: EntityId): void;

  /**
   * 根据 ID 获取实体
   * @param entityId 实体 ID
   * @returns 实体对象，如果不存在则返回 undefined
   */
  getEntity(entityId: EntityId): Entity | undefined;

  /**
   * 获取所有活跃实体的 ID 列表
   * @returns 实体 ID 数组
   */
  getEntityIds(): EntityId[];

  /**
   * 获取所有活跃实体的列表
   * @returns 实体数组
   */
  getEntities(): Entity[];

  /**
   * 检查指定实体是否存在
   * @param entityId 实体 ID
   */
  hasEntity(entityId: EntityId): boolean;

  /**
   * 为指定实体添加组件
   * 如果实体已存在同类型组件，则替换之
   * @param entityId 实体 ID
   * @param component 要添加的组件
   * @throws 如果实体不存在则抛出错误
   */
  addComponent(entityId: EntityId, component: Component): void;

  /**
   * 从指定实体移除指定类型的组件
   * @param entityId 实体 ID
   * @param componentType 组件类型
   * @throws 如果实体或组件不存在则抛出错误
   */
  removeComponent(entityId: EntityId, componentType: string): void;

  /**
   * 获取指定实体上的指定类型组件
   * @param entityId 实体 ID
   * @param componentType 组件类型
   * @returns 组件对象，如果不存在则返回 undefined
   */
  getComponent<T extends Component>(entityId: EntityId, componentType: string): T | undefined;

  /**
   * 检查指定实体是否拥有指定类型的组件
   * @param entityId 实体 ID
   * @param componentType 组件类型
   * @returns 如果实体拥有该类型组件则返回 true
   */
  hasComponent(entityId: EntityId, componentType: string): boolean;

  /**
   * 获取指定实体的所有组件
   * @param entityId 实体 ID
   * @returns 组件数组，如果实体不存在则返回空数组
   */
  getComponents(entityId: EntityId): Component[];

  /**
   * 根据组件查询条件查找匹配的实体
   * allOf: 必须包含所有指定类型组件
   * anyOf: 包含任意一个指定类型组件
   * noneOf: 不包含任何指定类型组件
   * @param query 查询条件
   * @returns 匹配的实体数组
   */
  queryEntities(query: ComponentQuery): Entity[];

  /**
   * 注册事件监听器
   * @param eventType 事件类型
   * @param handler 事件处理函数
   */
  on(eventType: EntityEventType, handler: EntityEventHandler): void;

  /**
   * 移除事件监听器
   * @param eventType 事件类型
   * @param handler 事件处理函数
   */
  off(eventType: EntityEventType, handler: EntityEventHandler): void;
}