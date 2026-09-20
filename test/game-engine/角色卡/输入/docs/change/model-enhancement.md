# 变更: InputState 模型增强

## 变更内容

在 `src/models/input.ts` 中新增了游戏手柄精细状态类型定义：

### 新增类型

- `GamepadButtonState` — 表示游戏手柄单个按钮的状态（`pressed: boolean`, `value: number`）
- `GamepadState` — 表示游戏手柄完整状态（`index`, `connected`, `id`, `buttons[]`, `axes[]`）

### 修改类型

- `InputState` — 新增 `gamepads: readonly GamepadState[]` 字段，返回所有已连接手柄的完整状态数组

## 理由

原有 `InputState` 仅通过 `gamepadConnected: boolean` 表示"是否有手柄连接"，无法获取具体手柄的按钮和轴状态供游戏逻辑使用。新增类型后：

1. 游戏逻辑可直接通过 `getState().gamepads[0].axes[0]` 读取左摇杆 X 轴
2. 装配角色可通过 `GamepadState.buttons` 遍历所有按钮状态
3. 与 `GamepadHandler` 的 `poll()` 机制配合，每帧自动刷新

## 兼容性

- 新增字段 `gamepads` 为 additive change，不影响已有只读引用
- 旧代码读取 `InputState` 时不使用 `gamepads` 不会出错