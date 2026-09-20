/**
 * 鼠标输入处理
 * 主拥有者: 输入
 * 监听 DOM 鼠标事件，维护鼠标位置、按钮状态、滚动增量，支持轮询查询
 */

import {
  InputEventType,
  MouseButton,
  type InputEvent,
  type MouseEventData,
} from '../../../models/input';

/** 鼠标事件回调类型 */
export type MouseEventHandler = (event: InputEvent) => void;

/**
 * 鼠标输入处理器
 *
 * 绑定 mousedown / mouseup / mousemove / wheel 事件，
 * 维护当前鼠标位置、按钮按压状态、帧间移动增量、滚动增量。
 * 帧增量（delta / scrollDelta）在每帧 poll() 调用时重置为零。
 */
export class MouseHandler {
  private position: { x: number; y: number } = { x: 0, y: 0 };
  private delta: { x: number; y: number } = { x: 0, y: 0 };
  private scrollDelta: number = 0;
  private pressedButtons: Set<MouseButton> = new Set();
  private eventHandler: MouseEventHandler | null = null;

  private onMouseDownBound: ((event: MouseEvent) => void) | null = null;
  private onMouseUpBound: ((event: MouseEvent) => void) | null = null;
  private onMouseMoveBound: ((event: MouseEvent) => void) | null = null;
  private onWheelBound: ((event: WheelEvent) => void) | null = null;

  /**
   * 将 MouseEvent.button 数值映射到 MouseButton 枚举
   * 标准鼠标: 0=左, 1=中, 2=右, 3=后退, 4=前进
   * 超出范围的安全映射为 Left
   */
  private static mapButton(button: number): MouseButton {
    switch (button) {
      case 0:
        return MouseButton.Left;
      case 1:
        return MouseButton.Middle;
      case 2:
        return MouseButton.Right;
      case 3:
        return MouseButton.Back;
      case 4:
        return MouseButton.Forward;
      default:
        return MouseButton.Left;
    }
  }

  /**
   * 注册外部事件回调
   * 由 InputProvider 在 initialize 时注入
   */
  setEventHandler(handler: MouseEventHandler): void {
    this.eventHandler = handler;
  }

  /** 初始化，绑定鼠标事件监听 */
  initialize(): void {
    this.onMouseDownBound = (event: MouseEvent): void => {
      const button: MouseButton = MouseHandler.mapButton(event.button);
      this.pressedButtons.add(button);

      if (this.eventHandler !== null) {
        const eventData: MouseEventData = {
          type: InputEventType.MouseDown,
          button,
          x: event.clientX,
          y: event.clientY,
          timestamp: performance.now(),
        };
        this.eventHandler(eventData);
      }
    };

    this.onMouseUpBound = (event: MouseEvent): void => {
      const button: MouseButton = MouseHandler.mapButton(event.button);
      this.pressedButtons.delete(button);

      if (this.eventHandler !== null) {
        const eventData: MouseEventData = {
          type: InputEventType.MouseUp,
          button,
          x: event.clientX,
          y: event.clientY,
          timestamp: performance.now(),
        };
        this.eventHandler(eventData);
      }
    };

    this.onMouseMoveBound = (event: MouseEvent): void => {
      this.delta = {
        x: event.clientX - this.position.x,
        y: event.clientY - this.position.y,
      };
      this.position = { x: event.clientX, y: event.clientY };

      if (this.eventHandler !== null) {
        const eventData: MouseEventData = {
          type: InputEventType.MouseMove,
          button: MouseButton.Left,
          x: event.clientX,
          y: event.clientY,
          timestamp: performance.now(),
        };
        this.eventHandler(eventData);
      }
    };

    this.onWheelBound = (event: WheelEvent): void => {
      this.scrollDelta = event.deltaY;

      if (this.eventHandler !== null) {
        const eventData: MouseEventData = {
          type: InputEventType.MouseWheel,
          button: MouseButton.Left,
          x: event.clientX,
          y: event.clientY,
          timestamp: performance.now(),
        };
        this.eventHandler(eventData);
      }
    };

    window.addEventListener('mousedown', this.onMouseDownBound);
    window.addEventListener('mouseup', this.onMouseUpBound);
    window.addEventListener('mousemove', this.onMouseMoveBound);
    window.addEventListener('wheel', this.onWheelBound, { passive: true });
  }

  /** 销毁，移除所有事件监听并清理状态 */
  destroy(): void {
    if (this.onMouseDownBound !== null) {
      window.removeEventListener('mousedown', this.onMouseDownBound);
      this.onMouseDownBound = null;
    }
    if (this.onMouseUpBound !== null) {
      window.removeEventListener('mouseup', this.onMouseUpBound);
      this.onMouseUpBound = null;
    }
    if (this.onMouseMoveBound !== null) {
      window.removeEventListener('mousemove', this.onMouseMoveBound);
      this.onMouseMoveBound = null;
    }
    if (this.onWheelBound !== null) {
      window.removeEventListener('wheel', this.onWheelBound);
      this.onWheelBound = null;
    }
    this.pressedButtons.clear();
    this.eventHandler = null;
  }

  /** 获取当前鼠标位置 */
  getPosition(): { readonly x: number; readonly y: number } {
    return { x: this.position.x, y: this.position.y };
  }

  /** 获取上一帧鼠标移动增量 */
  getDelta(): { readonly x: number; readonly y: number } {
    return { x: this.delta.x, y: this.delta.y };
  }

  /** 获取上一帧鼠标滚动增量 */
  getScrollDelta(): number {
    return this.scrollDelta;
  }

  /** 判断指定鼠标按钮是否处于按下状态 */
  isButtonDown(button: MouseButton): boolean {
    return this.pressedButtons.has(button);
  }

  /** 获取当前所有按下按钮的副本 */
  getPressedButtons(): Set<MouseButton> {
    return new Set(this.pressedButtons);
  }

  /** 重置帧增量数据，在 poll() 开始时调用 */
  resetFrameDelta(): void {
    this.delta = { x: 0, y: 0 };
    this.scrollDelta = 0;
  }
}