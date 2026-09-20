# API 规范: 输入

## 导出

| 符号 | 类型 | 源文件 | 说明 |
| --- | --- | --- | --- |
| `InputProvider` | Interface | `src/providers/abstract/input.ts` | 输入提供者契约接口 |
| `InputEventHandler` | Type | `src/providers/abstract/input.ts` | 输入事件回调类型：`(event: InputEvent) => void` |
| `BrowserInputProvider` | Class | `src/providers/impl/input/input.provider.ts` | 浏览器环境输入提供者实现 |
| `KeyboardHandler` | Class | `src/providers/impl/input/keyboard.ts` | 键盘输入处理（内部使用） |
| `MouseHandler` | Class | `src/providers/impl/input/mouse.ts` | 鼠标输入处理（内部使用） |
| `GamepadHandler` | Class | `src/providers/impl/input/gamepad.ts` | 游戏手柄输入处理（内部使用） |

### 模型导出（src/models/input.ts，主拥有者：输入）

| 符号 | 类型 | 说明 |
| --- | --- | --- |
| `InputEventType` | Enum | 所有输入事件类型（keydown/keyup/mousedown/...） |
| `Key` | Enum | 键盘按键码（方向键/字母/数字/功能键等） |
| `MouseButton` | Enum | 鼠标按钮（左/中/右/后退/前进） |
| `InputEvent` | Interface | 输入事件基接口 |
| `KeyboardEventData` | Interface | 键盘事件数据 |
| `MouseEventData` | Interface | 鼠标事件数据 |
| `GamepadButtonEvent` | Interface | 游戏手柄按钮事件 |
| `GamepadAxisEvent` | Interface | 游戏手柄轴事件 |
| `InputState` | Interface | 输入状态快照 |
| `GamepadButtonState` | Interface | 游戏手柄按钮状态 |
| `GamepadState` | Interface | 游戏手柄完整状态 |

## 依赖

- 无外部 npm 依赖，仅使用标准 DOM API（window.addEventListener、Navigator.getGamepads、performance.now）

## 装配说明（供装配角色使用）

### 初始化顺序

```typescript
import { BrowserInputProvider } from './src/providers/impl/input/input.provider';
import type { InputProvider } from './src/providers/abstract/input';

// 1. 创建实例
const inputProvider: InputProvider = new BrowserInputProvider();

// 2. 初始化（绑定 DOM 事件）
inputProvider.initialize();

// 3. 每帧开始时 poll
function gameLoop(): void {
  inputProvider.poll();

  // 读取输入状态
  if (inputProvider.isKeyDown(Key.Space)) {
    // 玩家跳跃
  }

  const state: InputState = inputProvider.getState();
  // 使用 state...

  requestAnimationFrame(gameLoop);
}

// 4. 游戏结束时销毁
inputProvider.destroy();
```

### 事件监听示例

```typescript
const handler: InputEventHandler = (event: InputEvent) => {
  switch (event.type) {
    case InputEventType.KeyDown: {
      const keyEvent = event as KeyboardEventData;
      console.log('Key pressed:', keyEvent.key);
      break;
    }
    case InputEventType.MouseMove: {
      const mouseEvent = event as MouseEventData;
      console.log('Mouse at:', mouseEvent.x, mouseEvent.y);
      break;
    }
  }
};

inputProvider.addEventListener(handler);
// 不再需要时:
inputProvider.removeEventListener(handler);
```

### 注意事项

- `poll()` 必须在每帧开始时调用，且早于任何输入状态读取
- `BrowserInputProvider` 依赖浏览器 DOM API，不适用于 Node.js 环境
- `KeyboardHandler` 的 `mapKeyCode` 仅识别 `Key` 枚举中定义的按键码，其余按键被安全忽略
- 游戏手柄轮询最多追踪前 4 个已连接设备
- 鼠标帧增量（delta / scrollDelta）在每次 `poll()` 时重置为零
- 游戏手柄轴变化阈值 0.01，低于此值的微小波动被忽略以避免事件风暴