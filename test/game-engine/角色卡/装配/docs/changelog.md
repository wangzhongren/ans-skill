# 装配 — 变更日志

## [1.0.0] - 2026-09-18

### Added

#### 新增文件

- `main.ts` — 引擎入口点，负责 DOM 初始化和系统启动。
  监听 `DOMContentLoaded` 事件，从 `#game-root` 元素读取配置，创建并启动 `GameEngine` 实例。
  Debug 模式下将引擎实例暴露到 `window.__engine` 便于调试。

- `src/interface/engine.ts` — 引擎公共 API 外观。
  定义 `Engine` 接口和 `GameEngine` 实现类，组合所有子系统并协调其生命周期：
  - 初始化: 获取 Canvas、创建渲染器/渲染管线、实体服务、场景管理器、计时器、
    固定时间步长、输入提供者、音频提供者、资源加载器、游戏主循环。
  - 启动/停止/暂停/恢复: 委托给 `DefaultGameLoop`。
  - 销毁: 按序停止游戏循环、销毁音频/输入/渲染子系统、释放资源。
  - 子系统访问: 通过 getter 方法提供对各子系统的只读访问。

- `src/services/public/index.ts` — Service 层统一入口。
  聚合导出所有服务（EntityService、SceneManager、Timer）的抽象接口和实现类。

- `src/providers/public/index.ts` — Provider 层统一入口。
  重导出 `render.ts` 内容并聚合导出所有提供者
  （Input、Audio、Resource）的抽象接口和实现类。

- `test/装配/engine.test.ts` — 引擎外观单元测试。
  覆盖引擎配置创建、生命周期状态流转（初始 → 运行 → 暂停 → 恢复 → 停止 → 销毁）、
  子系统访问接口、状态守卫边界条件。

#### 已存在（本角色主拥有）

- `src/models/engine.ts` — 引擎配置类型（未修改）。
  包含 `EngineConfig`、`EngineState`、`FrameTiming` 类型定义。