/**
 * 输入提供者契约
 * 主拥有者: 输入
 * 定义键盘、鼠标、游戏手柄等输入设备的轮询和事件处理接口
 */

import type {
  GamepadState,
  InputEvent,
  InputState,
  Key,
  MouseButton,
} from '../../models/input';

/** 输入事件处理回调类型 */
export type InputEventHandler = (event: InputEvent) => void;

/** 输入提供者接口 */
export interface InputProvider {
  /**
   * 初始化输入系统，绑定 DOM 事件监听
   * 在游戏启动时调用一次
   */
  initialize(): void;

  /**
   * 销毁输入系统，移除所有事件监听并清理资源
   * 在游戏销毁时调用一次
   */
  destroy(): void;

  /**
   * 轮询所有输入设备，更新内部状态
   * 重置帧增量数据并刷新游戏手柄状态
   * 应在每帧开始时调用一次
   */
  poll(): void;

  // --- 键盘 ---

  /** 判断指定按键是否处于按下状态 */
  isKeyDown(key: Key): boolean;

  /** 获取当前所有处于按下状态的按键集合 */
  getPressedKeys(): Set<Key>;

  // --- 鼠标 ---

  /** 获取当前鼠标在视口中的位置 */
  getMousePosition(): { readonly x: number; readonly y: number };

  /** 判断指定鼠标按钮是否处于按下状态 */
  isMouseButtonDown(button: MouseButton): boolean;

  /** 获取鼠标在上一帧的移动增量（像素） */
  getMouseDelta(): { readonly x: number; readonly y: number };

  /** 获取鼠标滚轮在上一帧的滚动增量 */
  getScrollDelta(): number;

  // --- 游戏手柄 ---

  /** 获取指定索引的游戏手柄详细状态，未连接时返回 null */
  getGamepadState(index: number): GamepadState | null;

  /** 是否有至少一个游戏手柄已连接 */
  isGamepadConnected(): boolean;

  // --- 事件 ---

  /** 注册输入事件监听器，接收所有类型的输入事件 */
  addEventListener(handler: InputEventHandler): void;

  /** 移除已注册的输入事件监听器 */
  removeEventListener(handler: InputEventHandler): void;

  // --- 状态快照 ---

  /** 获取当前完整输入状态快照 */
  getState(): InputState;
}