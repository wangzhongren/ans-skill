/**
 * 输入提供者实现
 * 主拥有者: 输入
 * 组合键盘、鼠标、游戏手柄处理器，对外暴露统一的 InputProvider 接口
 */

import type { InputProvider, InputEventHandler } from '../../abstract/input';
import { KeyboardHandler } from './keyboard';
import { MouseHandler } from './mouse';
import { GamepadHandler } from './gamepad';
import type {
  GamepadState,
  InputEvent,
  InputState,
  Key,
  MouseButton,
} from '../../../models/input';

/**
 * 浏览器环境输入提供者
 *
 * 组合 KeyboardHandler、MouseHandler、GamepadHandler 三个子系统，
 * 统一管理初始化、销毁、轮询生命周期。
 * 将三个子系统的原生事件通过统一回调分发给所有注册的 InputEventHandler。
 *
 * 用法:
 *   const provider = new BrowserInputProvider();
 *   provider.initialize();
 *   // 每帧:
 *   provider.poll();
 *   const state = provider.getState();
 *   // 游戏结束:
 *   provider.destroy();
 */
export class BrowserInputProvider implements InputProvider {
  private keyboardHandler: KeyboardHandler;
  private mouseHandler: MouseHandler;
  private gamepadHandler: GamepadHandler;
  private eventHandlers: Set<InputEventHandler> = new Set();
  private initialized: boolean = false;

  constructor() {
    this.keyboardHandler = new KeyboardHandler();
    this.mouseHandler = new MouseHandler();
    this.gamepadHandler = new GamepadHandler();
  }

  /**
   * 统一的内部事件分发函数
   * 将来自三个子系统的原生输入事件分发给所有注册的外部监听器
   */
  private dispatchEvent(event: InputEvent): void {
    for (const handler of this.eventHandlers) {
      try {
        handler(event);
      } catch (error) {
        console.error('Input event handler error:', error);
      }
    }
  }

  /** 初始化输入系统，绑定所有输入设备事件监听 */
  initialize(): void {
    if (this.initialized) {
      return;
    }

    const dispatchBound: (event: InputEvent) => void = this.dispatchEvent.bind(this);

    this.keyboardHandler.setEventHandler(dispatchBound);
    this.mouseHandler.setEventHandler(dispatchBound);
    this.gamepadHandler.setEventHandler(dispatchBound);

    this.keyboardHandler.initialize();
    this.mouseHandler.initialize();
    this.gamepadHandler.initialize();

    this.initialized = true;
  }

  /** 销毁输入系统，移除所有事件监听并清理资源 */
  destroy(): void {
    if (!this.initialized) {
      return;
    }

    this.keyboardHandler.destroy();
    this.mouseHandler.destroy();
    this.gamepadHandler.destroy();
    this.eventHandlers.clear();
    this.initialized = false;
  }

  /**
   * 轮询所有输入设备，更新内部状态
   * 重置鼠标帧增量并刷新游戏手柄状态
   * 应在每帧开始时调用一次
   */
  poll(): void {
    if (!this.initialized) {
      return;
    }

    this.mouseHandler.resetFrameDelta();
    this.gamepadHandler.poll();
  }

  // --- 键盘 ---

  isKeyDown(key: Key): boolean {
    return this.keyboardHandler.isKeyDown(key);
  }

  getPressedKeys(): Set<Key> {
    return this.keyboardHandler.getPressedKeys();
  }

  // --- 鼠标 ---

  getMousePosition(): { readonly x: number; readonly y: number } {
    return this.mouseHandler.getPosition();
  }

  isMouseButtonDown(button: MouseButton): boolean {
    return this.mouseHandler.isButtonDown(button);
  }

  getMouseDelta(): { readonly x: number; readonly y: number } {
    return this.mouseHandler.getDelta();
  }

  getScrollDelta(): number {
    return this.mouseHandler.getScrollDelta();
  }

  // --- 游戏手柄 ---

  getGamepadState(index: number): GamepadState | null {
    return this.gamepadHandler.getState(index);
  }

  isGamepadConnected(): boolean {
    return this.gamepadHandler.isConnected();
  }

  // --- 事件 ---

  addEventListener(handler: InputEventHandler): void {
    this.eventHandlers.add(handler);
  }

  removeEventListener(handler: InputEventHandler): void {
    this.eventHandlers.delete(handler);
  }

  // --- 状态快照 ---

  getState(): InputState {
    return {
      keys: this.keyboardHandler.getPressedKeys(),
      mouseButtons: this.mouseHandler.getPressedButtons(),
      mousePosition: this.mouseHandler.getPosition(),
      gamepadConnected: this.gamepadHandler.isConnected(),
      gamepads: this.getConnectedGamepadStates(),
    };
  }

  /**
   * 获取所有已连接游戏手柄的状态数组
   * 用于填充 InputState.gamepads 字段
   */
  private getConnectedGamepadStates(): GamepadState[] {
    const states: GamepadState[] = [];
    for (let index: number = 0; index <= 3; index += 1) {
      const state: GamepadState | null = this.gamepadHandler.getState(index);
      if (state !== null) {
        states.push(state);
      }
    }
    return states;
  }
}