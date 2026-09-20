// Service 层统一入口
// 装配角色维护，其他角色通过此入口引用 Service 实现

// Entity Service
export { type EntityService } from '../abstract/entity';
export { GameEntityService } from '../impl/entity/entity.service';

// Scene Manager
export { type SceneManager } from '../abstract/scene';
export { SceneManagerImpl } from '../impl/scene/scene.manager';

// Timer
export { type Timer } from '../abstract/timer';
export { PerformanceTimer } from '../impl/timer/timer';