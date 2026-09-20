/**
 * 键盘输入处理
 * 主拥有者: 输入
 * 监听 DOM 键盘事件，维护按键状态，支持轮询查询
 */

import {
  InputEventType,
  Key,
  type InputEvent,
  type KeyboardEventData,
} from '../../../models/input';

/** 键盘事件回调类型 */
export type KeyboardEventHandler = (event: InputEvent) => void;

/**
 * 键盘输入处理器
 *
 * 绑定 window 的 keydown / keyup 事件，维护当前按下的按键集合。
 * 通过 mapKeyCode 将 DOM KeyboardEvent.code 映射到内部 Key 枚举，
 * 未识别的按键码会被安全忽略。
 *
 * 实现原则：事件驱动更新状态，Polling 层直接读取状态集合，
 * 无需在每帧进行额外计算。
 */
export class KeyboardHandler {
  private pressedKeys: Set<Key> = new Set();
  private eventHandler: KeyboardEventHandler | null = null;

  private onKeyDownBound: ((event: KeyboardEvent) => void) | null = null;
  private onKeyUpBound: ((event: KeyboardEvent) => void) | null = null;

  /**
   * 注册外部事件回调
   * 由 InputProvider 在 initialize 时注入
   */
  setEventHandler(handler: KeyboardEventHandler): void {
    this.eventHandler = handler;
  }

  /**
   * 将 DOM KeyboardEvent.code 字符串映射到 Key 枚举值
   * code 值（如 'ArrowUp', 'KeyA', 'Digit1'）与 Key 枚举值完全匹配，
   * 不在枚举范围内的 code 返回 null 并被安全忽略
   */
  private mapKeyCode(code: string): Key | null {
    const keyValues: string[] = Object.values(Key);
    if (keyValues.includes(code)) {
      return code as Key;
    }
    return null;
  }

  /** 初始化，绑定键盘事件监听 */
  initialize(): void {
    this.onKeyDownBound = (event: KeyboardEvent): void => {
      const key: Key | null = this.mapKeyCode(event.code);
      if (key === null) {
        return;
      }

      this.pressedKeys.add(key);

      if (this.eventHandler !== null) {
        const eventData: KeyboardEventData = {
          type: InputEventType.KeyDown,
          key,
          altKey: event.altKey,
          ctrlKey: event.ctrlKey,
          shiftKey: event.shiftKey,
          timestamp: performance.now(),
        };
        this.eventHandler(eventData);
      }
    };

    this.onKeyUpBound = (event: KeyboardEvent): void => {
      const key: Key | null = this.mapKeyCode(event.code);
      if (key === null) {
        return;
      }

      this.pressedKeys.delete(key);

      if (this.eventHandler !== null) {
        const eventData: KeyboardEventData = {
          type: InputEventType.KeyUp,
          key,
          altKey: event.altKey,
          ctrlKey: event.ctrlKey,
          shiftKey: event.shiftKey,
          timestamp: performance.now(),
        };
        this.eventHandler(eventData);
      }
    };

    window.addEventListener('keydown', this.onKeyDownBound);
    window.addEventListener('keyup', this.onKeyUpBound);
  }

  /** 销毁，移除所有事件监听并清理状态 */
  destroy(): void {
    if (this.onKeyDownBound !== null) {
      window.removeEventListener('keydown', this.onKeyDownBound);
      this.onKeyDownBound = null;
    }
    if (this.onKeyUpBound !== null) {
      window.removeEventListener('keyup', this.onKeyUpBound);
      this.onKeyUpBound = null;
    }
    this.pressedKeys.clear();
    this.eventHandler = null;
  }

  /** 判断指定按键是否处于按下状态 */
  isKeyDown(key: Key): boolean {
    return this.pressedKeys.has(key);
  }

  /** 获取当前所有按下按键的副本 */
  getPressedKeys(): Set<Key> {
    return new Set(this.pressedKeys);
  }
}