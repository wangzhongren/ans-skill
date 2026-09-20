# 功能描述: 实体管理

## 架构概览

```
┌──────────────────────────────────────────────────────────┐
│                     EntityService                        │  ← 公共接口
├──────────────────────────────────────────────────────────┤
│                   GameEntityService                      │  ← 实现
│  ┌───────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ 创建/销毁 │  │ 组件增删查   │  │ 事件系统         │  │
│  └─────┬─────┘  └──────┬───────┘  └────────┬─────────┘  │
│        └───────────────┼────────────────────┘            │
│                        ▼                                 │
│              ┌─────────────────┐                         │
│              │ ComponentContainer │                      │  ← 存储层
│              │ (Map<EntityId,   │                        │
│              │  Map<string,    │                        │
│              │  Component>>)   │                        │
│              └─────────────────┘                         │
└──────────────────────────────────────────────────────────┘
         │                    │
         ▼                    ▼
    ┌──────────┐     ┌──────────────┐
    │ 场景管理  │     │ 渲染 / 主循环 │
    └──────────┘     └──────────────┘
```

## 分层说明

### 模型层 (`src/models/ecs.ts`)

实体与组件的类型定义。作为实体管理角色的主拥有模型，其他角色以只读方式引用。

**关键类型：**
- `EntityId` — 实体唯一标识（number 类型）
- `Entity` — 实体对象，包含组件映射表、创建时间戳、存活状态
- `Component` — 组件接口，所有组件必须实现 `readonly type: string`
- `EntityEventType` / `EntityEvent` / `ComponentEvent` — 事件系统类型
- `ComponentQuery` — 组件查询条件，支持 allOf/anyOf/noneOf 组合查询

### 服务契约 (`src/services/abstract/entity.ts`)

`EntityService` 接口定义实体管理服务的公共契约，包含：
- 实体生命周期: `createEntity`, `destroyEntity`
- 实体查询: `getEntity`, `getEntities`, `getEntityIds`, `hasEntity`
- 组件管理: `addComponent`, `removeComponent`, `getComponent`, `hasComponent`, `getComponents`
- 组件查询: `queryEntities`（支持组合条件）
- 事件监听: `on`, `off`

### 组件容器 (`src/services/impl/entity/component.container.ts`)

底层存储实现。负责实体的注册与组件数据的存储管理。

- 使用 `Map<EntityId, Map<string, Component>>` 双层映射结构
- 提供自增 ID 生成器（`acquireId`）
- 所有数据操作都经过类型安全和错误检查

### 服务实现 (`src/services/impl/entity/entity.service.ts`)

`GameEntityService` 实现 `EntityService` 接口，整合组件容器与事件系统。

**工作流程：**

1. **创建实体**: 调用 `acquireId()` 获取新 ID → 构建 Entity 对象 → 注册到容器 → 派发 `Created` 事件
2. **销毁实体**: 检查实体存在 → 标记 `alive = false` → 从容器移除 → 派发 `Destroyed` 事件
3. **添加组件**: 委托容器添加 → 派发 `ComponentAdded` 事件
4. **移除组件**: 委托容器移除 → 派发 `ComponentRemoved` 事件

## 事件系统

采用发布-订阅模式，支持按事件类型注册监听器。

| 事件类型 | 触发时机 | 事件载荷 |
| --- | --- | --- |
| `entity:created` | 实体创建完成 | `EntityEvent` (entityId, timestamp) |
| `entity:destroyed` | 实体被销毁 | `EntityEvent` (entityId, timestamp) |
| `component:added` | 组件被添加 | `ComponentEvent` (entityId, componentType, timestamp) |
| `component:removed` | 组件被移除 | `ComponentEvent` (entityId, componentType, timestamp) |

监听器中的异常会被捕获并通过 `console.error` 输出，不会影响其他监听器的执行。

## 查询系统

`queryEntities` 支持组合查询条件：

- **allOf**: 实体必须包含所有指定类型的组件
- **anyOf**: 实体包含至少一个指定类型的组件
- **noneOf**: 实体不包含任何指定类型的组件

查询条件可以组合使用（条件间为 AND 关系）。

## 关键代码位置

| 文件 | 功能 |
| --- | --- |
| `src/models/ecs.ts` | 实体与组件类型定义 |
| `src/services/abstract/entity.ts` | 实体管理服务契约 |
| `src/services/impl/entity/entity.service.ts` | 实体管理服务实现 |
| `src/services/impl/entity/component.container.ts` | 组件容器实现 |

## 质量约束满足情况

- **相邻层合规**: Service 层只引用 Model 层类型，不跨越 Provider/Pipeline 层
- **代码质量**: 所有方法均有真实实现；变量名使用完整描述性命名；无三元运算符；每个 try/catch 都输出错误信息
- **安全**: 所有方法包含边界检查（实体不存在、组件不存在等）