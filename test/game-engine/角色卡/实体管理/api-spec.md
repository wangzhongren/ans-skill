# API 规范: 实体管理

## 导出

### 模型 (`src/models/ecs.ts`)

| 导出 | 类型 | 说明 |
| --- | --- | --- |
| `EntityId` | `type` | 实体唯一标识（number） |
| `Component` | `interface` | 组件接口，包含 `readonly type: string` |
| `Entity` | `interface` | 实体，包含 `id`, `components`, `createdAt`, `alive` |
| `EntityEventType` | `enum` | 实体生命周期事件类型枚举 |
| `EntityEvent` | `interface` | 实体事件基础接口 |
| `ComponentEvent` | `interface` | 组件变更事件（继承 EntityEvent） |
| `EntityEventHandler` | `type` | 实体事件处理器函数签名 |
| `ComponentQuery` | `interface` | 组件查询条件（allOf/anyOf/noneOf） |

### 服务契约 (`src/services/abstract/entity.ts`)

| 导出 | 类型 | 说明 |
| --- | --- | --- |
| `EntityService` | `interface` | 实体管理服务公共接口 |

### 服务实现 (`src/services/impl/entity/entity.service.ts`)

| 导出 | 类型 | 说明 |
| --- | --- | --- |
| `GameEntityService` | `class` | 实体管理服务实现 |

### 组件容器 (`src/services/impl/entity/component.container.ts`)

| 导出 | 类型 | 说明 |
| --- | --- | --- |
| `ComponentContainer` | `class` | 组件存储容器实现（内部使用，不建议对外导出） |

## 依赖

| 依赖模块 | 引用方式 | 说明 |
| --- | --- | --- |
| `src/models/ecs.ts` | 直接 import | 实体与组件类型定义 |
| 无其他内部依赖 | — | 实体管理不依赖其他角色模块 |

## 装配说明

```typescript
import { GameEntityService } from './services/impl/entity/entity.service';
import { type EntityService } from './services/abstract/entity';

// 创建实体管理服务实例
const entityService: EntityService = new GameEntityService();

// 创建实体
const player = entityService.createEntity();

// 添加组件
entityService.addComponent(player.id, { type: 'Transform', position: { x: 0, y: 0 } });

// 查询实体
const movingEntities = entityService.queryEntities({
  allOf: ['Transform', 'Velocity'],
});

// 监听事件
import { EntityEventType } from './models/ecs';
entityService.on(EntityEventType.Created, (event) => {
  console.log(`Entity ${event.entityId} created`);
});
```

## 其他角色集成要点

- **场景管理**: 通过 `EntityService` 接口操作实体。Scene 中的 `entities: Entity[]` 由场景管理自行管理引用，实体管理服务负责实体的创建和销毁。
- **渲染**: 通过 `queryEntities` 按组件类型查询需要渲染的实体（如包含 `Transform` 和 `Sprite` 组件的实体）。
- **主循环**: 通过事件监听 (`EntityEventType`) 感知实体生命周期变化。