# 功能描述: 场景管理

## 架构图

```
┌──────────────────────────────────────────────────────────┐
│                    场景管理 (Scene Management)              │
│                                                          │
│  ┌─────────────────┐    ┌──────────────────────────────┐ │
│  │  SceneManager    │    │  SceneLifecycle (钩子)        │ │
│  │  (abstract/      │───▶│  onEnter / onExit / onUpdate │ │
│  │   scene.ts)      │    └──────────────────────────────┘ │
│  └────────┬─────────┘                                     │
│           │ implements                                    │
│  ┌────────▼──────────┐                                    │
│  │ SceneManagerImpl   │    ┌──────────────────────────┐   │
│  │ (impl/scene/       │───▶│ SceneImpl                 │   │
│  │  scene.manager.ts) │    │ (impl/scene/scene.ts)     │   │
│  │                    │    │ · name / entities / state │   │
│  │ · scenes: Map      │    │ · onEnter / onExit       │   │
│  │ · lifecycles: Map   │    └──────────────────────────┘   │
│  │ · activeScene       │                                    │
│  └────────────────────┘                                    │
│                                                          │
│  ┌──────────────────────────────────────────────────┐    │
│  │ Model (src/models/scene.ts)                      │    │
│  │ · Scene (name, entities, state, isActive)        │    │
│  │ · SceneLifecycle (onEnter, onExit, onUpdate)     │    │
│  │ · SceneTransition (from, to, duration)           │    │
│  │ · SceneState (Loading, Active, Inactive, Destroyed)│   │
│  └──────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────┘
```

## 关键代码位置

| 文件 | 角色 |
| --- | --- |
| `src/models/scene.ts` | 场景类型定义（Model）—— 场景管理的拥有者 |
| `src/services/abstract/scene.ts` | 场景管理器接口（Abstract 层） |
| `src/services/impl/scene/scene.ts` | Scene 实现类，实现 Scene + SceneLifecycle |
| `src/services/impl/scene/scene.manager.ts` | SceneManager 实现，管理注册/切换/生命周期 |
| `test/场景管理/scene.test.ts` | SceneImpl 单元测试 |
| `test/场景管理/scene.manager.test.ts` | SceneManagerImpl 单元测试 |

## 详解

### 场景类型定义 (Model)

`Scene` 接口定义了场景的核心属性：名称、实体列表、生命周期状态、活跃标志。`SceneState` 枚举跟踪场景从创建到销毁的完整生命周期。`SceneLifecycle` 接口定义了场景进入、退出、更新的钩子方法。`SceneTransition` 定义场景切换的元数据。

### 场景管理服务 (Abstract)

`SceneManager` 接口定义了场景管理的核心契约：
- `createScene`：创建新场景并注册到管理器
- `registerLifecycle`：为场景绑定生命周期钩子
- `switchScene`：执行场景切换，触发生命周期回调
- `getActiveScene` / `getScene`：场景查询
- `destroyScene`：销毁场景并清理资源
- `update`：在帧循环中驱动当前场景更新

### 场景管理器实现 (Impl)

`SceneManagerImpl` 维护场景注册表（Map）和生命周期钩子注册表。场景切换时，先调用当前场景的 onExit，再调用新场景的 onEnter，确保生命周期顺序正确。`update` 方法在帧循环中被调用，驱动当前活跃场景的 onUpdate。

### 场景实现 (Impl)

`SceneImpl` 同时实现了 Scene 数据模型和 SceneLifecycle 钩子，提供默认的状态转换逻辑。