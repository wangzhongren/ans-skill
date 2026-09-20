# 场景管理设计

## 概述

场景管理负责游戏场景的创建、切换、生命周期管理以及场景图组织。它是游戏引擎的核心模块之一，与主循环、实体管理、渲染等其他角色并行协作。

## 设计决策

### 1. Scene 与 SceneLifecycle 分离

将场景数据（Scene）与生命周期行为（SceneLifecycle）分离为两个接口，允许灵活组合。`SceneImpl` 同时实现了两者作为默认实现，外部也可提供自定义生命周期钩子。

### 2. SceneState 枚举

引入 `SceneState` 枚举（Loading, Active, Inactive, Destroyed），使场景状态转换显式化，便于调试和状态机集成。

### 3. 注册表架构

SceneManager 维护 `Map<string, SceneImpl>` 和 `Map<string, SceneLifecycle>` 两个注册表，分别管理场景实例和生命周期钩子，保持关注点分离。

### 4. 场景切换顺序

场景切换时严格按照 当前场景 onExit -> 新场景 onEnter 的顺序执行，确保资源释放和初始化的正确顺序。

## 文件清单

| 文件 | 说明 |
| --- | --- |
| `src/models/scene.ts` | 场景类型定义（Model，主拥有者：场景管理） |
| `src/services/abstract/scene.ts` | 场景管理服务契约（Abstract） |
| `src/services/impl/scene/scene.ts` | Scene 实现类（Impl） |
| `src/services/impl/scene/scene.manager.ts` | SceneManager 实现（Impl） |
| `test/场景管理/scene.test.ts` | SceneImpl 单元测试 |
| `test/场景管理/scene.manager.test.ts` | SceneManagerImpl 单元测试 |

## 与其它角色的交互

| 角色 | 关系 |
| --- | --- |
| 主循环 | 每帧调用 `SceneManager.update(dt)` |
| 实体管理 | Scene 持有 Entity[] 引用 |
| 装配 | 负责实例化 SceneManagerImpl 并注入到引擎中 |
| 渲染 | 渲染活跃场景中的实体（通过 SceneManager.getActiveScene） |