# 输入模块设计

## 职责

输入模块为游戏引擎提供统一的键盘、鼠标、游戏手柄输入抽象，支持：
- 每帧轮询当前输入状态（状态查询模式）
- 注册输入事件监听器（事件驱动模式）
- 多输入设备共存，统一管理生命周期

## 分层架构

```
┌─────────────────────────────────────┐
│          InputProvider 契约          │  ← 抽象层 (abstract/)
│     接口定义，不含任何实现           │
├─────────────────────────────────────┤
│  ┌────────┐ ┌────────┐ ┌─────────┐  │  ← 实现层 (impl/input/)
│  │Keyboard│ │  Mouse  │ │ Gamepad │  │     各自独立初始化+销毁
│  └────────┘ └────────┘ └─────────┘  │
│  ┌───────────────────────────────┐  │
│  │   BrowserInputProvider        │  │  ← 组合实现，协调三者
│  └───────────────────────────────┘  │
├─────────────────────────────────────┤
│       src/models/input.ts           │  ← 类型模型层
│    枚举、接口、状态快照类型          │
└─────────────────────────────────────┘
```

## 核心流程

### 初始化
```
BrowserInputProvider.initialize()
  ├─ KeyboardHandler.initialize()      → window.addEventListener('keydown', ...)
  ├─ KeyboardHandler.setEventHandler() → 注入统一分发回调
  ├─ MouseHandler.initialize()         → window.addEventListener('mousedown', ...)
  ├─ MouseHandler.setEventHandler()    → 注入统一分发回调
  ├─ GamepadHandler.initialize()       → window.addEventListener('gamepadconnected', ...)
  └─ GamepadHandler.setEventHandler()  → 注入统一分发回调
```

### 每帧轮询
```
gameLoop()
  ├─ inputProvider.poll()
  │   ├─ MouseHandler.resetFrameDelta()    → delta = {0,0}, scrollDelta = 0
  │   └─ GamepadHandler.poll()             → navigator.getGamepads() 刷新状态
  ├─ inputProvider.isKeyDown(Key.Space)     → 读取键盘状态
  ├─ inputProvider.getMousePosition()       → 读取鼠标位置
  ├─ inputProvider.getGamepadState(0)       → 读取手柄状态
  └─ inputProvider.getState()               → 聚合快照
```

### 事件分发
```
KeyboardEvent 'keydown'
  → KeyboardHandler.onKeyDownBound()
    → pressedKeys.add(key)
    → dispatchEvent({ type: KeyDown, key, ... })
      → forEach(handler) handler(event)

MouseEvent 'mousemove'
  → MouseHandler.onMouseMoveBound()
    → position += delta
    → dispatchEvent({ type: MouseMove, x, y, ... })
```

## 文件清单

| 文件 | 类型 | 说明 |
| --- | --- | --- |
| `src/models/input.ts` | 类型定义 | 主拥有者，所有 input 相关类型 |
| `src/providers/abstract/input.ts` | 抽象契约 | InputProvider 接口 |
| `src/providers/impl/input/input.provider.ts` | 组合实现 | BrowserInputProvider |
| `src/providers/impl/input/keyboard.ts` | 键盘实现 | KeyboardHandler |
| `src/providers/impl/input/mouse.ts` | 鼠标实现 | MouseHandler |
| `src/providers/impl/input/gamepad.ts` | 手柄实现 | GamepadHandler |