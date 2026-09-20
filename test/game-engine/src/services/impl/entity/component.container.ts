// 组件容器实现
// 管理实体的组件存储，提供组件的增删查操作
// 被 EntityService 使用，不对外暴露

import {
  type Component,
  type Entity,
  type EntityId,
} from '../../../models/ecs';

/**
 * 组件容器
 *
 * 管理实体及其组件的存储。
 * 内部使用 Map<EntityId, Entity> 存储结构。
 * 组件的增删直接操作 Entity 的 components Map。
 */
export class ComponentContainer {
  /**
   * 实体注册表: EntityId -> Entity
   */
  private readonly entities: Map<EntityId, Entity>;

  /**
   * 下一个实体 ID（自增，从 1 开始）
   */
  private nextId: EntityId;

  constructor() {
    this.entities = new Map<EntityId, Entity>();
    this.nextId = 1;
  }

  /**
   * 获取下一个可用的实体 ID 并自增
   */
  acquireId(): EntityId {
    const id = this.nextId;
    this.nextId += 1;
    return id;
  }

  /**
   * 注册一个新实体
   * @param entity 要注册的实体
   * @throws 如果实体 ID 已存在则抛出错误
   */
  addEntity(entity: Entity): void {
    if (this.entities.has(entity.id)) {
      throw new Error(`Entity with id ${entity.id} already exists`);
    }
    this.entities.set(entity.id, entity);
  }

  /**
   * 移除一个实体及其所有组件
   * @param entityId 要移除的实体 ID
   * @throws 如果实体不存在则抛出错误
   */
  removeEntity(entityId: EntityId): void {
    if (!this.entities.has(entityId)) {
      throw new Error(`Entity with id ${entityId} does not exist`);
    }
    this.entities.delete(entityId);
  }

  /**
   * 获取实体元数据
   * @param entityId 实体 ID
   * @returns 实体对象，如果不存在则返回 undefined
   */
  getEntity(entityId: EntityId): Entity | undefined {
    return this.entities.get(entityId);
  }

  /**
   * 检查实体是否存在
   * @param entityId 实体 ID
   */
  hasEntity(entityId: EntityId): boolean {
    return this.entities.has(entityId);
  }

  /**
   * 获取所有实体
   */
  getAllEntities(): Entity[] {
    return Array.from(this.entities.values());
  }

  /**
   * 获取所有实体 ID
   */
  getAllEntityIds(): EntityId[] {
    return Array.from(this.entities.keys());
  }

  /**
   * 添加组件到指定实体
   * 如果实体已存在同类型组件，则替换
   * @param entityId 实体 ID
   * @param component 要添加的组件
   * @throws 如果实体不存在则抛出错误
   */
  addComponent(entityId: EntityId, component: Component): void {
    const entity = this.entities.get(entityId);
    if (!entity) {
      throw new Error(`Entity with id ${entityId} does not exist`);
    }
    entity.components.set(component.type, component);
  }

  /**
   * 从指定实体移除组件
   * @param entityId 实体 ID
   * @param componentType 组件类型
   * @throws 如果实体或组件不存在则抛出错误
   */
  removeComponent(entityId: EntityId, componentType: string): void {
    const entity = this.entities.get(entityId);
    if (!entity) {
      throw new Error(`Entity with id ${entityId} does not exist`);
    }
    if (!entity.components.has(componentType)) {
      throw new Error(
        `Component of type "${componentType}" not found on entity ${entityId}`
      );
    }
    entity.components.delete(componentType);
  }

  /**
   * 获取指定实体上的组件
   * @param entityId 实体 ID
   * @param componentType 组件类型
   * @returns 组件对象，如果不存在则返回 undefined
   */
  getComponent<T extends Component>(
    entityId: EntityId,
    componentType: string
  ): T | undefined {
    const entity = this.entities.get(entityId);
    if (!entity) {
      return undefined;
    }
    return entity.components.get(componentType) as T | undefined;
  }

  /**
   * 检查实体是否拥有指定类型组件
   * @param entityId 实体 ID
   * @param componentType 组件类型
   */
  hasComponent(entityId: EntityId, componentType: string): boolean {
    const entity = this.entities.get(entityId);
    if (!entity) {
      return false;
    }
    return entity.components.has(componentType);
  }

  /**
   * 获取实体所有组件
   * @param entityId 实体 ID
   * @returns 组件数组
   */
  getComponents(entityId: EntityId): Component[] {
    const entity = this.entities.get(entityId);
    if (!entity) {
      return [];
    }
    return Array.from(entity.components.values());
  }
}