# 功能描述: 输入

## 架构概览

```
┌────────────────────────────────────────────────────────────────────┐
│                      BrowserInputProvider                          │
│  (src/providers/impl/input/input.provider.ts)                      │
│                                                                     │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────┐ │
│  │  KeyboardHandler │  │   MouseHandler   │  │   GamepadHandler    │ │
│  │  keyboard.ts     │  │  mouse.ts        │  │  gamepad.ts         │ │
│  │                  │  │                  │  │                     │ │
│  │  keydown/keyup   │  │  mousedown/up    │  │  gamepadconnected   │ │
│  │  → Set<Key>      │  │  mousemove/wheel │  │  Navigator.getGP()  │ │
│  │                  │  │  → position      │  │  → button/axis poll │ │
│  │                  │  │  → delta, scroll │  │                     │ │
│  └────────┬─────────┘  └────────┬─────────┘  └──────────┬──────────┘ │
│           │                     │                       │            │
│           └─────────┬───────────┴───────────┬───────────┘            │
│                     │                       │                        │
│              ┌──────▼──────┐         ┌──────▼──────┐                 │
│              │ dispatchEvent()        │ poll()      │                 │
│              │ → 外部监听器          │ → 帧增量重置  │                 │
│              └─────────────┘         │ → 手柄刷新   │                 │
│                                      └─────────────┘                 │
└────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │  InputProvider    │
                    │  契约 (abstract)  │
                    │  input.ts         │
                    └──────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │  src/models/     │
                    │  input.ts        │
                    │  (类型定义)       │
                    └──────────────────┘
```

## 核心组件

### 1. 类型模型 (`src/models/input.ts`)

**主拥有者：输入**（其他角色只读引用）

定义完整的输入数据模型：
- `InputEventType` — 所有输入事件类型的枚举（关键帧、鼠标、手柄）
- `Key` — 键盘按键枚举（方向键 + 字母 + 数字 + 功能键共 40+ 个）
- `MouseButton` — 鼠标按钮枚举（左/中/右/后退/前进）
- `InputEvent` + 子接口 — 结构化事件数据（KeyboardEventData、MouseEventData、GamepadButtonEvent、GamepadAxisEvent）
- `InputState` — 帧级状态快照（按键、鼠标位置、按钮、手柄状态）
- `GamepadButtonState` / `GamepadState` — 游戏手柄精细状态（模拟值 + 轴数组）

### 2. 提供者契约 (`src/providers/abstract/input.ts`)

`InputProvider` 接口定义了统一输入抽象：
- **生命周期**: `initialize()` / `destroy()` / `poll()`
- **键盘**: `isKeyDown()` / `getPressedKeys()`
- **鼠标**: `getMousePosition()` / `isMouseButtonDown()` / `getMouseDelta()` / `getScrollDelta()`
- **游戏手柄**: `getGamepadState()` / `isGamepadConnected()`
- **事件**: `addEventListener()` / `removeEventListener()`
- **状态**: `getState()`

### 3. 键盘处理器 (`src/providers/impl/input/keyboard.ts`)

- 绑定 `window.keydown` / `window.keyup`
- 通过 `mapKeyCode()` 将 DOM `KeyboardEvent.code` 映射到 `Key` 枚举
- 维护 `pressedKeys: Set<Key>` 作为当前帧状态
- 触发 `InputEventType.KeyDown` / `KeyUp` 事件

### 4. 鼠标处理器 (`src/providers/impl/input/mouse.ts`)

- 绑定 `mousedown` / `mouseup` / `mousemove` / `wheel`
- 维护 `position`、`delta`（帧间增量）、`scrollDelta`、`pressedButtons`
- `resetFrameDelta()` 在每帧 poll 时清零增量数据
- `mapButton()` 将 `MouseEvent.button` 数值映射到 `MouseButton` 枚举

### 5. 游戏手柄处理器 (`src/providers/impl/input/gamepad.ts`)

- 监听 `gamepadconnected` / `gamepaddisconnected`
- 每帧 `poll()` 通过 `Navigator.getGamepads()` 轮询最新状态
- `detectButtonTransitions()` — 检测按钮按下/释放过渡并触发事件
- `detectAxisChanges()` — 检测轴值变化（阈值 0.01）并触发事件
- 维护 `gamepadStates: Map<number, GamepadState>` 最多追踪 4 个手柄

### 6. 组合提供者 (`src/providers/impl/input/input.provider.ts`)

`BrowserInputProvider` 实现了 `InputProvider` 接口：
- 组合三个子系统，注入统一 `dispatchEvent()` 回调
- `initialize()` 初始化全部三个子系统
- `poll()` 重置鼠标增量 + 轮询手柄状态
- `getState()` 聚合键盘/鼠标/手柄状态为单一 `InputState`
- 事件分发使用 `try/catch` 保护，单个监听器异常不会影响其他监听器

## 设计决策

| 决策 | 选择 | 理由 |
| --- | --- | --- |
| 轮询 vs 事件驱动 | 混合 | 键盘/鼠标用事件更新状态（自动），手柄用轮询（Gamepad API 不支持事件） |
| 手柄状态更新时机 | 每帧 poll() | Gamepad API 只在用户交互时更新状态，需显式轮询 |
| 手柄轴变化阈值 | 0.01 | 防止微小噪声导致事件风暴 |
| DOM 事件绑定目标 | window | 确保全窗口范围内捕获输入，不影响游戏内焦点管理 |
| wheel 事件 passive | true | 不阻止默认滚动，提升滚轮响应性能 |
| 帧增量清零时机 | poll() 开始 | 确保每帧的 delta 数据仅反映该帧内的输入变化 |