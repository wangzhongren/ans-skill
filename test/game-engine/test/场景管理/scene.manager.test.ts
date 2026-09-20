// 场景管理器单元测试
// 主拥有者: 场景管理

import { SceneManagerImpl } from '../../src/services/impl/scene/scene.manager';
import { SceneLifecycle } from '../../src/models/scene';
import { Entity } from '../../src/models/ecs';

/** 测试场景创建与获取 */
function testCreateAndGetScene(): void {
  const manager = new SceneManagerImpl();
  const scene = manager.createScene('menu');

  console.assert(scene.name === 'menu', '场景名称应为 menu');
  console.assert(scene.entities.length === 0, '新场景应无实体');

  const retrieved = manager.getScene('menu');
  console.assert(retrieved !== undefined, '应能通过 getScene 获取');
  console.assert(retrieved === scene, '返回的应是同一个场景引用');
  console.log('PASS: testCreateAndGetScene');
}

/** 测试重复创建场景会抛异常 */
function testDuplicateSceneThrows(): void {
  const manager = new SceneManagerImpl();
  manager.createScene('menu');

  let threw = false;
  try {
    manager.createScene('menu');
  } catch (error) {
    threw = true;
  }
  console.assert(threw, '重复创建应抛出异常');
  console.log('PASS: testDuplicateSceneThrows');
}

/** 测试场景切换 */
function testSwitchScene(): void {
  const manager = new SceneManagerImpl();
  manager.createScene('menu');
  manager.createScene('game');

  console.assert(manager.getActiveScene() === null, '初始无活跃场景');

  manager.switchScene('menu');
  console.assert(manager.getActiveScene() !== null, '切换后应有活跃场景');
  console.assert(manager.getActiveScene()!.name === 'menu', '活跃场景应为 menu');

  manager.switchScene('game');
  console.assert(manager.getActiveScene()!.name === 'game', '切换到 game 后活跃场景应为 game');
  console.log('PASS: testSwitchScene');
}

/** 测试切换到不存在的场景抛异常 */
function testSwitchToUnknownSceneThrows(): void {
  const manager = new SceneManagerImpl();
  manager.createScene('menu');

  let threw = false;
  try {
    manager.switchScene('nonexistent');
  } catch (error) {
    threw = true;
  }
  console.assert(threw, '切换到不存在的场景应抛出异常');
  console.log('PASS: testSwitchToUnknownSceneThrows');
}

/** 测试注册生命周期钩子 */
function testRegisterLifecycle(): void {
  const manager = new SceneManagerImpl();
  manager.createScene('menu');

  let enteredCount = 0;
  let exitedCount = 0;
  let updated = false;

  const lifecycle: SceneLifecycle = {
    onEnter(): void {
      enteredCount++;
    },
    onExit(): void {
      exitedCount++;
    },
    onUpdate(dt: number): void {
      updated = true;
    },
  };

  manager.registerLifecycle('menu', lifecycle);

  manager.switchScene('menu');
  console.assert(enteredCount === 1, '进入场景应触发 onEnter');

  manager.switchScene('menu'); // 再次切换到同一个场景会触发 onExit + onEnter
  console.assert(exitedCount === 1, '离开场景应触发 onExit');
  console.assert(enteredCount === 2, '再次进入应再次触发 onEnter');

  manager.update(0.016);
  console.assert(updated === true, 'update 应触发生命周期 onUpdate');
  console.log('PASS: testRegisterLifecycle');
}

/** 测试注册未知场景的生命周期抛异常 */
function testRegisterLifecycleUnknownSceneThrows(): void {
  const manager = new SceneManagerImpl();
  const lifecycle: SceneLifecycle = {
    onEnter(): void {},
    onExit(): void {},
    onUpdate(dt: number): void {},
  };

  let threw = false;
  try {
    manager.registerLifecycle('unknown', lifecycle);
  } catch (error) {
    threw = true;
  }
  console.assert(threw, '注册未知场景的生命周期应抛出异常');
  console.log('PASS: testRegisterLifecycleUnknownSceneThrows');
}

/** 测试场景销毁 */
function testDestroyScene(): void {
  const manager = new SceneManagerImpl();
  manager.createScene('temp');
  console.assert(manager.getScene('temp') !== undefined, '销毁前应存在');

  manager.destroyScene('temp');
  console.assert(manager.getScene('temp') === undefined, '销毁后应不存在');
  console.log('PASS: testDestroyScene');
}

/** 测试销毁活跃场景时清除活跃引用 */
function testDestroyActiveScene(): void {
  const manager = new SceneManagerImpl();
  manager.createScene('active');
  manager.switchScene('active');
  console.assert(manager.getActiveScene() !== null, '切换后应有活跃场景');

  manager.destroyScene('active');
  console.assert(manager.getActiveScene() === null, '销毁活跃场景后活跃引用应清空');
  console.log('PASS: testDestroyActiveScene');
}

/** 测试 update 在没有活跃场景时静默跳过 */
function testUpdateWithoutActiveScene(): void {
  const manager = new SceneManagerImpl();
  manager.createScene('idle');

  // 没有活跃场景时 update 不应抛异常
  try {
    manager.update(0.016);
    console.log('PASS: testUpdateWithoutActiveScene (no throw)');
  } catch (error) {
    console.error('FAIL: testUpdateWithoutActiveScene threw', error);
  }
}

/** 测试场景 update 驱动 */
function testSceneUpdateDriven(): void {
  const manager = new SceneManagerImpl();
  manager.createScene('updating');

  let sceneUpdated = false;
  const lifecycle: SceneLifecycle = {
    onEnter(): void {},
    onExit(): void {},
    onUpdate(dt: number): void {
      sceneUpdated = true;
    },
  };

  manager.registerLifecycle('updating', lifecycle);
  manager.switchScene('updating');
  manager.update(0.016);

  console.assert(sceneUpdated === true, 'update 应驱动场景更新');
  console.log('PASS: testSceneUpdateDriven');
}

// 运行测试
testCreateAndGetScene();
testDuplicateSceneThrows();
testSwitchScene();
testSwitchToUnknownSceneThrows();
testRegisterLifecycle();
testRegisterLifecycleUnknownSceneThrows();
testDestroyScene();
testDestroyActiveScene();
testUpdateWithoutActiveScene();
testSceneUpdateDriven();