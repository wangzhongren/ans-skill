// 实体管理服务实现
// 实现 src/services/abstract/entity.ts 中定义的 EntityService 接口

import {
  type Component,
  type ComponentEvent,
  type ComponentQuery,
  type Entity,
  type EntityEvent,
  EntityEventType,
  type EntityEventHandler,
  type EntityId,
} from '../../../models/ecs';
import { type EntityService } from '../../abstract/entity';
import { ComponentContainer } from './component.container';

/**
 * 实体管理服务
 *
 * 提供实体的创建、销毁、组件管理以及实体查询功能。
 * 内部使用 ComponentContainer 管理存储，并通过事件系统通知生命周期变更。
 */
export class GameEntityService implements EntityService {
  private readonly container: ComponentContainer;

  /**
   * 事件监听器存储: EventType -> Set<Handler>
   */
  private readonly listeners: Map<EntityEventType, Set<EntityEventHandler>>;

  constructor() {
    this.container = new ComponentContainer();
    this.listeners = new Map<EntityEventType, Set<EntityEventHandler>>();

    // 初始化事件类型存储
    for (const eventType of Object.values(EntityEventType)) {
      this.listeners.set(eventType, new Set<EntityEventHandler>());
    }
  }

  /**
   * 创建一个新实体，分配唯一 ID
   */
  createEntity(): Entity {
    const entityId = this.container.acquireId();

    const entity: Entity = {
      id: entityId,
      components: new Map<string, Component>(),
      createdAt: Date.now(),
      alive: true,
    };

    try {
      this.container.addEntity(entity);

      const event: EntityEvent = {
        type: EntityEventType.Created,
        entityId: entity.id,
        timestamp: Date.now(),
      };
      this.dispatch(event);

      return entity;
    } catch (error) {
      console.error(`Failed to create entity: ${error}`);
      throw error;
    }
  }

  /**
   * 销毁指定实体
   */
  destroyEntity(entityId: EntityId): void {
    try {
      if (!this.container.hasEntity(entityId)) {
        throw new Error(`Entity with id ${entityId} does not exist`);
      }

      // 标记实体为死亡
      const entity = this.container.getEntity(entityId);
      if (entity) {
        entity.alive = false;
      }

      this.container.removeEntity(entityId);

      const event: EntityEvent = {
        type: EntityEventType.Destroyed,
        entityId,
        timestamp: Date.now(),
      };
      this.dispatch(event);
    } catch (error) {
      console.error(`Failed to destroy entity ${entityId}: ${error}`);
      throw error;
    }
  }

  /**
   * 根据 ID 获取实体
   */
  getEntity(entityId: EntityId): Entity | undefined {
    return this.container.getEntity(entityId);
  }

  /**
   * 获取所有活跃实体的 ID 列表
   */
  getEntityIds(): EntityId[] {
    return this.container.getAllEntityIds();
  }

  /**
   * 获取所有活跃实体的列表
   */
  getEntities(): Entity[] {
    return this.container.getAllEntities();
  }

  /**
   * 检查指定实体是否存在
   */
  hasEntity(entityId: EntityId): boolean {
    return this.container.hasEntity(entityId);
  }

  /**
   * 为指定实体添加组件
   */
  addComponent(entityId: EntityId, component: Component): void {
    try {
      this.container.addComponent(entityId, component);

      const event: ComponentEvent = {
        type: EntityEventType.ComponentAdded,
        entityId,
        componentType: component.type,
        timestamp: Date.now(),
      };
      this.dispatch(event);
    } catch (error) {
      console.error(
        `Failed to add component "${component.type}" to entity ${entityId}: ${error}`
      );
      throw error;
    }
  }

  /**
   * 从指定实体移除组件
   */
  removeComponent(entityId: EntityId, componentType: string): void {
    try {
      this.container.removeComponent(entityId, componentType);

      const event: ComponentEvent = {
        type: EntityEventType.ComponentRemoved,
        entityId,
        componentType,
        timestamp: Date.now(),
      };
      this.dispatch(event);
    } catch (error) {
      console.error(
        `Failed to remove component "${componentType}" from entity ${entityId}: ${error}`
      );
      throw error;
    }
  }

  /**
   * 获取指定实体上的指定类型组件
   */
  getComponent<T extends Component>(
    entityId: EntityId,
    componentType: string
  ): T | undefined {
    return this.container.getComponent<T>(entityId, componentType);
  }

  /**
   * 检查指定实体是否拥有指定类型的组件
   */
  hasComponent(entityId: EntityId, componentType: string): boolean {
    return this.container.hasComponent(entityId, componentType);
  }

  /**
   * 获取指定实体的所有组件
   */
  getComponents(entityId: EntityId): Component[] {
    return this.container.getComponents(entityId);
  }

  /**
   * 根据组件查询条件查找匹配的实体
   */
  queryEntities(query: ComponentQuery): Entity[] {
    const allEntities = this.container.getAllEntities();

    return allEntities.filter((entity) => {
      const entityTypes = Array.from(entity.components.keys());

      // allOf: 必须包含所有指定类型组件
      if (query.allOf && query.allOf.length > 0) {
        const hasAll = query.allOf.every((type) => entityTypes.includes(type));
        if (!hasAll) {
          return false;
        }
      }

      // anyOf: 包含任意一个指定类型组件
      if (query.anyOf && query.anyOf.length > 0) {
        const hasAny = query.anyOf.some((type) => entityTypes.includes(type));
        if (!hasAny) {
          return false;
        }
      }

      // noneOf: 不包含任何指定类型组件
      if (query.noneOf && query.noneOf.length > 0) {
        const hasNone = query.noneOf.every(
          (type) => !entityTypes.includes(type)
        );
        if (!hasNone) {
          return false;
        }
      }

      return true;
    });
  }

  /**
   * 注册事件监听器
   */
  on(eventType: EntityEventType, handler: EntityEventHandler): void {
    const handlers = this.listeners.get(eventType);
    if (handlers) {
      handlers.add(handler);
    } else {
      const newSet = new Set<EntityEventHandler>();
      newSet.add(handler);
      this.listeners.set(eventType, newSet);
    }
  }

  /**
   * 移除事件监听器
   */
  off(eventType: EntityEventType, handler: EntityEventHandler): void {
    const handlers = this.listeners.get(eventType);
    if (handlers) {
      handlers.delete(handler);
    }
  }

  /**
   * 分发事件到所有已注册的监听器
   */
  private dispatch(event: EntityEvent): void {
    const handlers = this.listeners.get(event.type as EntityEventType);
    if (!handlers) {
      return;
    }

    for (const handler of handlers) {
      try {
        handler(event);
      } catch (error) {
        console.error(
          `Error in event handler for ${event.type}: ${error}`
        );
      }
    }
  }
}