// 输入类型定义
// 主拥有者: 输入
// 其他角色以只读方式引用

/** 输入事件类型 */
export enum InputEventType {
  KeyDown = 'keydown',
  KeyUp = 'keyup',
  MouseDown = 'mousedown',
  MouseUp = 'mouseup',
  MouseMove = 'mousemove',
  MouseWheel = 'mousewheel',
  GamepadButtonDown = 'gamepadbuttondown',
  GamepadButtonUp = 'gamepadbuttonup',
  GamepadAxis = 'gamepadaxis',
}

/** 键盘按键 */
export enum Key {
  ArrowUp = 'ArrowUp',
  ArrowDown = 'ArrowDown',
  ArrowLeft = 'ArrowLeft',
  ArrowRight = 'ArrowRight',
  Space = ' ',
  Enter = 'Enter',
  Escape = 'Escape',
  ShiftLeft = 'ShiftLeft',
  ShiftRight = 'ShiftRight',
  ControlLeft = 'ControlLeft',
  ControlRight = 'ControlRight',
  AltLeft = 'AltLeft',
  AltRight = 'AltRight',
  KeyA = 'KeyA',
  KeyB = 'KeyB',
  KeyC = 'KeyC',
  KeyD = 'KeyD',
  KeyE = 'KeyE',
  KeyF = 'KeyF',
  KeyG = 'KeyG',
  KeyH = 'KeyH',
  KeyI = 'KeyI',
  KeyJ = 'KeyJ',
  KeyK = 'KeyK',
  KeyL = 'KeyL',
  KeyM = 'KeyM',
  KeyN = 'KeyN',
  KeyO = 'KeyO',
  KeyP = 'KeyP',
  KeyQ = 'KeyQ',
  KeyR = 'KeyR',
  KeyS = 'KeyS',
  KeyT = 'KeyT',
  KeyU = 'KeyU',
  KeyV = 'KeyV',
  KeyW = 'KeyW',
  KeyX = 'KeyX',
  KeyY = 'KeyY',
  KeyZ = 'KeyZ',
  Digit0 = 'Digit0',
  Digit1 = 'Digit1',
  Digit2 = 'Digit2',
  Digit3 = 'Digit3',
  Digit4 = 'Digit4',
  Digit5 = 'Digit5',
  Digit6 = 'Digit6',
  Digit7 = 'Digit7',
  Digit8 = 'Digit8',
  Digit9 = 'Digit9',
}

/** 鼠标按钮 */
export enum MouseButton {
  Left = 0,
  Middle = 1,
  Right = 2,
  Back = 3,
  Forward = 4,
}

/** 输入事件 */
export interface InputEvent {
  readonly type: InputEventType;
  readonly timestamp: number;
}

/** 键盘事件 */
export interface KeyboardEventData extends InputEvent {
  readonly type: InputEventType.KeyDown | InputEventType.KeyUp;
  readonly key: Key;
  readonly altKey: boolean;
  readonly ctrlKey: boolean;
  readonly shiftKey: boolean;
}

/** 鼠标事件 */
export interface MouseEventData extends InputEvent {
  readonly type: InputEventType.MouseDown | InputEventType.MouseUp | InputEventType.MouseMove | InputEventType.MouseWheel;
  readonly button: MouseButton;
  readonly x: number;
  readonly y: number;
}

/** 游戏手柄按钮事件 */
export interface GamepadButtonEvent extends InputEvent {
  readonly type: InputEventType.GamepadButtonDown | InputEventType.GamepadButtonUp;
  readonly index: number;
  readonly button: number;
}

/** 游戏手柄轴事件 */
export interface GamepadAxisEvent extends InputEvent {
  readonly type: InputEventType.GamepadAxis;
  readonly index: number;
  readonly axis: number;
  readonly value: number;
}

/** 游戏手柄按钮状态（按压和模拟值） */
export interface GamepadButtonState {
  readonly pressed: boolean;
  readonly value: number;
}

/** 游戏手柄完整状态 */
export interface GamepadState {
  readonly index: number;
  readonly connected: boolean;
  readonly id: string;
  readonly buttons: readonly GamepadButtonState[];
  readonly axes: readonly number[];
}

/** 输入状态快照 */
export interface InputState {
  readonly keys: Set<Key>;
  readonly mouseButtons: Set<MouseButton>;
  readonly mousePosition: { x: number; y: number };
  readonly gamepadConnected: boolean;
  readonly gamepads: readonly GamepadState[];
}