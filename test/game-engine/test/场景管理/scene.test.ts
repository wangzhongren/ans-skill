// 场景实现单元测试
// 主拥有者: 场景管理

import { SceneImpl } from '../../src/services/impl/scene/scene';
import { SceneState } from '../../src/models/scene';
import { Entity } from '../../src/models/ecs';

/** SceneImpl 基本功能测试 */
function testSceneCreation(): void {
  const scene = new SceneImpl('menu');
  console.assert(scene.name === 'menu', '场景名称应为 menu');
  console.assert(scene.entities.length === 0, '新场景应无实体');
  console.assert(scene.state === SceneState.Inactive, '新场景状态应为 Inactive');
  console.assert(scene.isActive === false, '新场景不应活跃');
  console.log('PASS: testSceneCreation');
}

function testSceneWithEntities(): void {
  const entity: Entity = { id: 1, components: new Map() };
  const scene = new SceneImpl('game', [entity]);
  console.assert(scene.entities.length === 1, '场景应有 1 个实体');
  console.assert(scene.entities[0].id === 1, '实体 id 应匹配');
  console.log('PASS: testSceneWithEntities');
}

function testSceneLifecycle(): void {
  const scene = new SceneImpl('test');

  scene.onEnter();
  console.assert(scene.isActive === true, 'onEnter 后应活跃');
  console.assert(scene.state === SceneState.Active, 'onEnter 后状态应为 Active');

  scene.onExit();
  console.assert(scene.isActive === false, 'onExit 后不应活跃');
  console.assert(scene.state === SceneState.Inactive, 'onExit 后状态应为 Inactive');
  console.log('PASS: testSceneLifecycle');
}

function testSceneUpdate(): void {
  const scene = new SceneImpl('updating');
  scene.onEnter();

  // onUpdate 不应抛出异常
  try {
    scene.onUpdate(0.016);
    console.log('PASS: testSceneUpdate (no throw)');
  } catch (error) {
    console.error('FAIL: testSceneUpdate threw', error);
  }
}

// 运行测试
testSceneCreation();
testSceneWithEntities();
testSceneLifecycle();
testSceneUpdate();