# API 规范: 场景管理

## 导出

### Model (src/models/scene.ts)

| 导出名 | 类型 | 说明 |
| --- | --- | --- |
| `SceneState` | enum | 场景生命周期状态：Loading, Active, Inactive, Destroyed |
| `Scene` | interface | 场景数据模型：name, entities, state, isActive |
| `SceneLifecycle` | interface | 场景生命周期钩子：onEnter, onExit, onUpdate |
| `SceneTransition` | interface | 场景切换参数：from, to, duration |

### Abstract（服务契约）

| 导出名 | 类型 | 说明 |
| --- | --- | --- |
| `SceneManager` | interface | 场景管理器契约 |

### Impl（具体实现）

| 导出名 | 类型 | 说明 |
| --- | --- | --- |
| `SceneImpl` | class | 场景实现类（同时实现 Scene + SceneLifecycle） |
| `SceneManagerImpl` | class | 场景管理器实现（实现 SceneManager） |

## 依赖

| 依赖方向 | 源文件 | 目标 |
| --- | --- | --- |
| import | `src/services/abstract/scene.ts` | `../../models/scene`, `../../models/ecs` |
| import | `src/services/impl/scene/scene.ts` | `../../../models/scene`, `../../../models/ecs` |
| import | `src/services/impl/scene/scene.manager.ts` | `../../../models/scene`, `../../../models/ecs`, `../../abstract/scene`, `./scene` |

## 装配说明

### 接入流程

1. **创建 SceneManagerImpl 实例**：在引擎初始化阶段创建
2. **创建场景**：调用 `createScene(name, entities?)` 注册场景
3. **注册生命周期**：（可选）调用 `registerLifecycle(name, lifecycle)` 绑定钩子
4. **切换到初始场景**：调用 `switchScene(name, transition?)` 激活场景
5. **帧循环驱动**：每帧调用 `update(dt)` 驱动活跃场景更新
6. **销毁场景**：场景结束时调用 `destroyScene(name)` 清理

### 示例用法

```typescript
import { SceneManagerImpl } from './services/impl/scene/scene.manager';
import { SceneLifecycle } from './models/scene';

const manager = new SceneManagerImpl();
const menuScene = manager.createScene('menu');
const gameScene = manager.createScene('game');

const gameLifecycle: SceneLifecycle = {
  onEnter(): void { /* 初始化游戏逻辑 */ },
  onExit(): void { /* 清理游戏逻辑 */ },
  onUpdate(dt: number): void { /* 更新游戏逻辑 */ },
};
manager.registerLifecycle('game', gameLifecycle);

manager.switchScene('menu');
// ... user clicks start
manager.switchScene('game');

// 在游戏循环中每帧调用
function gameLoop(dt: number): void {
  manager.update(dt);
}

manager.destroyScene('menu');
```

### Provider 引用

场景管理的 Service 实现仅引用 Model 层（`models/scene`、`models/ecs`），不依赖任何 Provider。它通过 `SceneManager` 接口对外暴露能力，装配角色应将 `SceneManagerImpl` 实例化并注入到主循环或 Pipeline 中。