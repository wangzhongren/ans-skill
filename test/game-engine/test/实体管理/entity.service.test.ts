// 实体管理服务单元测试
// 主拥有者: 实体管理

import { GameEntityService } from '../../src/services/impl/entity/entity.service';
import { type Component, EntityEventType, type ComponentEvent, type EntityEvent } from '../../src/models/ecs';

/** 辅助：创建一个测试组件 */
function createTestComponent(type: string, data?: Record<string, unknown>): Component {
  return { type, ...data } as Component;
}

/** 测试创建实体 */
function testCreateEntity(): void {
  const service = new GameEntityService();
  const entity = service.createEntity();

  console.assert(entity.id > 0, '实体 ID 应大于 0');
  console.assert(entity.alive === true, '新实体应为活跃状态');
  console.assert(entity.createdAt > 0, '创建时间戳应有效');
  console.assert(entity.components.size === 0, '新实体应无组件');
  console.assert(service.hasEntity(entity.id) === true, '服务应确认实体存在');
  console.log('PASS: testCreateEntity');
}

/** 测试创建多个实体 ID 自增 */
function testIncrementalIds(): void {
  const service = new GameEntityService();
  const entity1 = service.createEntity();
  const entity2 = service.createEntity();
  const entity3 = service.createEntity();

  console.assert(entity2.id > entity1.id, '第二个实体 ID 应大于第一个');
  console.assert(entity3.id > entity2.id, '第三个实体 ID 应大于第二个');
  console.log('PASS: testIncrementalIds');
}

/** 测试销毁实体 */
function testDestroyEntity(): void {
  const service = new GameEntityService();
  const entity = service.createEntity();
  const entityId = entity.id;

  console.assert(service.hasEntity(entityId) === true, '销毁前实体应存在');
  service.destroyEntity(entityId);
  console.assert(service.hasEntity(entityId) === false, '销毁后实体应不存在');
  console.assert(service.getEntity(entityId) === undefined, '销毁后 getEntity 应返回 undefined');
  console.log('PASS: testDestroyEntity');
}

/** 测试销毁不存在的实体抛异常 */
function testDestroyNonexistentEntityThrows(): void {
  const service = new GameEntityService();

  let threw = false;
  try {
    service.destroyEntity(9999);
  } catch (error) {
    threw = true;
  }
  console.assert(threw, '销毁不存在的实体应抛出异常');
  console.log('PASS: testDestroyNonexistentEntityThrows');
}

/** 测试 getEntity 返回正确实体 */
function testGetEntity(): void {
  const service = new GameEntityService();
  const entity = service.createEntity();

  const retrieved = service.getEntity(entity.id);
  console.assert(retrieved !== undefined, '应能获取创建的实体');
  console.assert(retrieved!.id === entity.id, 'ID 应匹配');
  console.log('PASS: testGetEntity');
}

/** 测试 getEntityIds 和 getEntities */
function testListEntities(): void {
  const service = new GameEntityService();
  console.assert(service.getEntityIds().length === 0, '初始应无实体');

  service.createEntity();
  service.createEntity();
  service.createEntity();

  console.assert(service.getEntityIds().length === 3, 'getEntityIds 应返回 3 个 ID');
  console.assert(service.getEntities().length === 3, 'getEntities 应返回 3 个实体');
  console.log('PASS: testListEntities');
}

/** 测试添加组件 */
function testAddComponent(): void {
  const service = new GameEntityService();
  const entity = service.createEntity();
  const component = createTestComponent('Transform', { x: 100, y: 200 });

  service.addComponent(entity.id, component);
  console.assert(service.hasComponent(entity.id, 'Transform') === true, '添加后应拥有组件');
  console.assert(service.getComponent(entity.id, 'Transform') === component, '获取的组件应与添加的相同');
  console.log('PASS: testAddComponent');
}

/** 测试替换组件 */
function testReplaceComponent(): void {
  const service = new GameEntityService();
  const entity = service.createEntity();

  const oldComponent = createTestComponent('TestComponent', { value: 1 });
  service.addComponent(entity.id, oldComponent);

  const newComponent = createTestComponent('TestComponent', { value: 2 });
  service.addComponent(entity.id, newComponent);

  const retrieved = service.getComponent(entity.id, 'TestComponent');
  console.assert(retrieved === newComponent, '替换后应返回新组件');
  console.assert((retrieved as Record<string, unknown>).value === 2, '新组件数据应更新');
  console.log('PASS: testReplaceComponent');
}

/** 测试移除组件 */
function testRemoveComponent(): void {
  const service = new GameEntityService();
  const entity = service.createEntity();
  service.addComponent(entity.id, createTestComponent('Removable', {}));

  console.assert(service.hasComponent(entity.id, 'Removable') === true, '移除前应拥有组件');
  service.removeComponent(entity.id, 'Removable');
  console.assert(service.hasComponent(entity.id, 'Removable') === false, '移除后不应拥有组件');
  console.assert(service.getComponent(entity.id, 'Removable') === undefined, '移除后 getComponent 应返回 undefined');
  console.log('PASS: testRemoveComponent');
}

/** 测试移除不存在的组件抛异常 */
function testRemoveNonexistentComponentThrows(): void {
  const service = new GameEntityService();
  const entity = service.createEntity();

  let threw = false;
  try {
    service.removeComponent(entity.id, 'Nonexistent');
  } catch (error) {
    threw = true;
  }
  console.assert(threw, '移除不存在的组件应抛出异常');
  console.log('PASS: testRemoveNonexistentComponentThrows');
}

/** 测试在不存在实体上添加组件抛异常 */
function testAddComponentToNonexistentEntityThrows(): void {
  const service = new GameEntityService();

  let threw = false;
  try {
    service.addComponent(9999, createTestComponent('SomeComponent', {}));
  } catch (error) {
    threw = true;
  }
  console.assert(threw, '在不存在实体上添加组件应抛出异常');
  console.log('PASS: testAddComponentToNonexistentEntityThrows');
}

/** 测试获取不存在的实体组件返回 undefined */
function testGetComponentFromNonexistentEntity(): void {
  const service = new GameEntityService();
  const component = service.getComponent(9999, 'Anything');
  console.assert(component === undefined, '不存在的实体应返回 undefined');
  console.log('PASS: testGetComponentFromNonexistentEntity');
}

/** 测试 getComponents 获取所有组件 */
function testGetComponents(): void {
  const service = new GameEntityService();
  const entity = service.createEntity();

  service.addComponent(entity.id, createTestComponent('A', {}));
  service.addComponent(entity.id, createTestComponent('B', {}));
  service.addComponent(entity.id, createTestComponent('C', {}));

  const allComponents = service.getComponents(entity.id);
  console.assert(allComponents.length === 3, '应有 3 个组件');
  console.assert(allComponents.some((c) => c.type === 'A'), '应包含组件 A');
  console.assert(allComponents.some((c) => c.type === 'B'), '应包含组件 B');
  console.assert(allComponents.some((c) => c.type === 'C'), '应包含组件 C');
  console.log('PASS: testGetComponents');
}

/** 测试 queryEntities allOf */
function testQueryEntitiesAllOf(): void {
  const service = new GameEntityService();

  const entity1 = service.createEntity();
  service.addComponent(entity1.id, createTestComponent('Transform', {}));
  service.addComponent(entity1.id, createTestComponent('Renderable', {}));

  const entity2 = service.createEntity();
  service.addComponent(entity2.id, createTestComponent('Transform', {}));

  const entity3 = service.createEntity();
  service.addComponent(entity3.id, createTestComponent('Audio', {}));

  const results = service.queryEntities({ allOf: ['Transform', 'Renderable'] });
  console.assert(results.length === 1, 'allOf 查询应返回 1 个实体');
  console.assert(results[0].id === entity1.id, '结果应为 entity1');
  console.log('PASS: testQueryEntitiesAllOf');
}

/** 测试 queryEntities anyOf */
function testQueryEntitiesAnyOf(): void {
  const service = new GameEntityService();

  const entity1 = service.createEntity();
  service.addComponent(entity1.id, createTestComponent('Transform', {}));

  const entity2 = service.createEntity();
  service.addComponent(entity2.id, createTestComponent('Audio', {}));

  const entity3 = service.createEntity();
  service.addComponent(entity3.id, createTestComponent('Collider', {}));

  const results = service.queryEntities({ anyOf: ['Transform', 'Audio'] });
  console.assert(results.length === 2, 'anyOf 查询应返回 2 个实体');
  const ids = results.map((e) => e.id);
  console.assert(ids.includes(entity1.id), '应包含 entity1');
  console.assert(ids.includes(entity2.id), '应包含 entity2');
  console.assert(!ids.includes(entity3.id), '不应包含 entity3');
  console.log('PASS: testQueryEntitiesAnyOf');
}

/** 测试 queryEntities noneOf */
function testQueryEntitiesNoneOf(): void {
  const service = new GameEntityService();

  const entity1 = service.createEntity();
  service.addComponent(entity1.id, createTestComponent('Transform', {}));

  const entity2 = service.createEntity();
  service.addComponent(entity2.id, createTestComponent('Transform', {}));
  service.addComponent(entity2.id, createTestComponent('Audio', {}));

  const results = service.queryEntities({ noneOf: ['Audio'] });
  console.assert(results.length === 1, 'noneOf 查询应返回 1 个实体');
  console.assert(results[0].id === entity1.id, '结果应为 entity1');
  console.log('PASS: testQueryEntitiesNoneOf');
}

/** 测试 queryEntities 组合条件 */
function testQueryEntitiesCombined(): void {
  const service = new GameEntityService();

  const entity1 = service.createEntity();
  service.addComponent(entity1.id, createTestComponent('Transform', {}));
  service.addComponent(entity1.id, createTestComponent('Renderable', {}));

  const entity2 = service.createEntity();
  service.addComponent(entity2.id, createTestComponent('Transform', {}));
  service.addComponent(entity2.id, createTestComponent('Renderable', {}));
  service.addComponent(entity2.id, createTestComponent('Audio', {}));

  const entity3 = service.createEntity();
  service.addComponent(entity3.id, createTestComponent('Transform', {}));

  const results = service.queryEntities({
    allOf: ['Transform', 'Renderable'],
    noneOf: ['Audio'],
  });
  console.assert(results.length === 1, '组合条件查询应返回 1 个实体');
  console.assert(results[0].id === entity1.id, '结果应为 entity1');
  console.log('PASS: testQueryEntitiesCombined');
}

/** 测试事件系统 - Created 事件 */
function testCreatedEvent(): void {
  const service = new GameEntityService();
  let capturedEvent: EntityEvent | null = null;

  service.on(EntityEventType.Created, (event) => {
    capturedEvent = event;
  });

  const entity = service.createEntity();

  console.assert(capturedEvent !== null, '创建实体时应触发 Created 事件');
  console.assert(capturedEvent!.entityId === entity.id, '事件中包含正确的实体 ID');
  console.assert(capturedEvent!.type === EntityEventType.Created, '事件类型应为 Created');
  console.log('PASS: testCreatedEvent');
}

/** 测试事件系统 - Destroyed 事件 */
function testDestroyedEvent(): void {
  const service = new GameEntityService();
  let capturedEvent: EntityEvent | null = null;

  service.on(EntityEventType.Destroyed, (event) => {
    capturedEvent = event;
  });

  const entity = service.createEntity();
  service.destroyEntity(entity.id);

  console.assert(capturedEvent !== null, '销毁实体时应触发 Destroyed 事件');
  console.assert(capturedEvent!.entityId === entity.id, '事件中包含正确的实体 ID');
  console.assert(capturedEvent!.type === EntityEventType.Destroyed, '事件类型应为 Destroyed');
  console.log('PASS: testDestroyedEvent');
}

/** 测试事件系统 - ComponentAdded 事件 */
function testComponentAddedEvent(): void {
  const service = new GameEntityService();
  let capturedEvent: ComponentEvent | null = null;

  service.on(EntityEventType.ComponentAdded, (event) => {
    capturedEvent = event as ComponentEvent;
  });

  const entity = service.createEntity();
  service.addComponent(entity.id, createTestComponent('Health', { value: 100 }));

  console.assert(capturedEvent !== null, '添加组件时应触发 ComponentAdded 事件');
  console.assert(capturedEvent!.componentType === 'Health', '事件中包含组件类型');
  console.assert(capturedEvent!.entityId === entity.id, '事件中包含正确的实体 ID');
  console.log('PASS: testComponentAddedEvent');
}

/** 测试事件系统 - ComponentRemoved 事件 */
function testComponentRemovedEvent(): void {
  const service = new GameEntityService();
  let capturedEvent: ComponentEvent | null = null;

  service.on(EntityEventType.ComponentRemoved, (event) => {
    capturedEvent = event as ComponentEvent;
  });

  const entity = service.createEntity();
  service.addComponent(entity.id, createTestComponent('Removable', {}));
  service.removeComponent(entity.id, 'Removable');

  console.assert(capturedEvent !== null, '移除组件时应触发 ComponentRemoved 事件');
  console.assert(capturedEvent!.componentType === 'Removable', '事件中包含组件类型');
  console.assert(capturedEvent!.entityId === entity.id, '事件中包含正确的实体 ID');
  console.log('PASS: testComponentRemovedEvent');
}

/** 测试事件系统 - off 取消监听 */
function testOffEvent(): void {
  const service = new GameEntityService();
  let callCount = 0;

  const handler = () => {
    callCount++;
  };

  service.on(EntityEventType.Created, handler);
  service.createEntity();
  console.assert(callCount === 1, '第一次创建实体应触发 1 次');

  service.off(EntityEventType.Created, handler);
  service.createEntity();
  console.assert(callCount === 1, '取消监听后创建实体不应触发');
  console.log('PASS: testOffEvent');
}

/** 测试事件处理器的错误不会影响其他监听器 */
function testEventHandlerErrorIsolation(): void {
  const service = new GameEntityService();
  let normalHandlerCalled = false;

  service.on(EntityEventType.Created, () => {
    throw new Error('Handler error');
  });

  service.on(EntityEventType.Created, () => {
    normalHandlerCalled = true;
  });

  try {
    service.createEntity();
  } catch (error) {
    console.error('testEventHandlerErrorIsolation should not throw:', error);
  }

  console.assert(normalHandlerCalled === true, '出错的监听器不应影响其他监听器');
  console.log('PASS: testEventHandlerErrorIsolation');
}

/** 测试 hasEntity */
function testHasEntity(): void {
  const service = new GameEntityService();
  const entity = service.createEntity();

  console.assert(service.hasEntity(entity.id) === true, '存在的实体返回 true');
  console.assert(service.hasEntity(9999) === false, '不存在的实体返回 false');
  console.log('PASS: testHasEntity');
}

/** 测试 hasComponent 边界情况 */
function testHasComponentEdgeCases(): void {
  const service = new GameEntityService();
  const entity = service.createEntity();

  console.assert(service.hasComponent(entity.id, 'AnyComponent') === false, '无组件时返回 false');
  console.assert(service.hasComponent(9999, 'AnyComponent') === false, '实体不存在时返回 false');
  console.log('PASS: testHasComponentEdgeCases');
}

/** 测试 getComponents 在实体不存在时返回空数组 */
function testGetComponentsForNonexistentEntity(): void {
  const service = new GameEntityService();
  const components = service.getComponents(9999);
  console.assert(Array.isArray(components), '应返回数组');
  console.assert(components.length === 0, '应返回空数组');
  console.log('PASS: testGetComponentsForNonexistentEntity');
}

// 运行测试
testCreateEntity();
testIncrementalIds();
testDestroyEntity();
testDestroyNonexistentEntityThrows();
testGetEntity();
testListEntities();
testAddComponent();
testReplaceComponent();
testRemoveComponent();
testRemoveNonexistentComponentThrows();
testAddComponentToNonexistentEntityThrows();
testGetComponentFromNonexistentEntity();
testGetComponents();
testQueryEntitiesAllOf();
testQueryEntitiesAnyOf();
testQueryEntitiesNoneOf();
testQueryEntitiesCombined();
testCreatedEvent();
testDestroyedEvent();
testComponentAddedEvent();
testComponentRemovedEvent();
testOffEvent();
testEventHandlerErrorIsolation();
testHasEntity();
testHasComponentEdgeCases();
testGetComponentsForNonexistentEntity();