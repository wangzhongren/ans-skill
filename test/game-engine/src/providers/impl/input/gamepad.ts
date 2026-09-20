/**
 * 游戏手柄输入处理
 * 主拥有者: 输入
 * 使用 Navigator Gamepad API 轮询游戏手柄状态，支持连接/断开事件
 */

import {
  InputEventType,
  type GamepadAxisEvent,
  type GamepadButtonEvent,
  type GamepadButtonState,
  type GamepadState,
  type InputEvent,
} from '../../../models/input';

/** 游戏手柄事件回调类型 */
export type GamepadEventHandler = (event: InputEvent) => void;

/**
 * 游戏手柄输入处理器
 *
 * 监听 gamepadconnected / gamepaddisconnected 事件维护连接状态。
 * 在每帧 poll() 调用时通过 Navigator.getGamepads() 刷新按钮和轴数据。
 * 跟踪按钮的按下/释放过渡以触发 GamepadButtonDown / GamepadButtonUp 事件。
 */
export class GamepadHandler {
  private connected: boolean = false;
  private gamepadStates: Map<number, GamepadState> = new Map();
  private previousButtonStates: Map<number, boolean[]> = new Map();
  private eventHandler: GamepadEventHandler | null = null;

  private onGamepadConnectedBound: ((event: GamepadEvent) => void) | null = null;
  private onGamepadDisconnectedBound: ((event: GamepadEvent) => void) | null = null;

  /**
   * 注册外部事件回调
   * 由 InputProvider 在 initialize 时注入
   */
  setEventHandler(handler: GamepadEventHandler): void {
    this.eventHandler = handler;
  }

  /** 初始化，监听游戏手柄连接/断开事件 */
  initialize(): void {
    this.onGamepadConnectedBound = (event: GamepadEvent): void => {
      this.connected = true;
    };

    this.onGamepadDisconnectedBound = (event: GamepadEvent): void => {
      const gamepad: Gamepad | null = event.gamepad;
      this.gamepadStates.delete(gamepad.index);
      this.previousButtonStates.delete(gamepad.index);

      if (this.gamepadStates.size === 0) {
        this.connected = false;
      }
    };

    window.addEventListener('gamepadconnected', this.onGamepadConnectedBound);
    window.addEventListener('gamepaddisconnected', this.onGamepadDisconnectedBound);
  }

  /** 销毁，移除所有事件监听并清理状态 */
  destroy(): void {
    if (this.onGamepadConnectedBound !== null) {
      window.removeEventListener('gamepadconnected', this.onGamepadConnectedBound);
      this.onGamepadConnectedBound = null;
    }
    if (this.onGamepadDisconnectedBound !== null) {
      window.removeEventListener('gamepaddisconnected', this.onGamepadDisconnectedBound);
      this.onGamepadDisconnectedBound = null;
    }
    this.gamepadStates.clear();
    this.previousButtonStates.clear();
    this.connected = false;
    this.eventHandler = null;
  }

  /**
   * 轮询更新游戏手柄状态
   * 调用 Navigator.getGamepads() 获取最新状态，
   * 检测按钮过渡并触发对应事件
   */
  poll(): void {
    const gamepads: (Gamepad | null)[] = navigator.getGamepads
      ? navigator.getGamepads()
      : [];

    for (let index: number = 0; index < gamepads.length; index += 1) {
      const rawGamepad: Gamepad | null = gamepads[index];
      if (rawGamepad === null) {
        this.gamepadStates.delete(index);
        this.previousButtonStates.delete(index);
        continue;
      }

      this.connected = true;

      const buttons: GamepadButtonState[] = [];
      for (let b: number = 0; b < rawGamepad.buttons.length; b += 1) {
        buttons.push({
          pressed: rawGamepad.buttons[b].pressed,
          value: rawGamepad.buttons[b].value,
        });
      }

      const axes: number[] = [];
      for (let a: number = 0; a < rawGamepad.axes.length; a += 1) {
        axes.push(rawGamepad.axes[a]);
      }

      const state: GamepadState = {
        index: rawGamepad.index,
        connected: rawGamepad.connected,
        id: rawGamepad.id,
        buttons,
        axes,
      };

      // 在更新地图前获取上一帧的轴数据用于变化检测
      const previousAxes: readonly number[] = this.getPreviousAxes(index);

      this.gamepadStates.set(index, state);

      // 检测按钮过渡并触发事件
      this.detectButtonTransitions(index, rawGamepad);

      // 检测轴变化并触发事件（使用更新前的轴数据）
      this.detectAxisChanges(index, rawGamepad, previousAxes);
    }
  }

  /**
   * 检测游戏手柄按钮状态变化
   * 比较当前帧与上一帧的按钮按压状态，触发 down/up 事件
   */
  private detectButtonTransitions(index: number, rawGamepad: Gamepad): void {
    if (this.eventHandler === null) {
      const currentPressed: boolean[] = [];
      for (let b: number = 0; b < rawGamepad.buttons.length; b += 1) {
        currentPressed.push(rawGamepad.buttons[b].pressed);
      }
      this.previousButtonStates.set(index, currentPressed);
      return;
    }

    const previousPressed: boolean[] | undefined = this.previousButtonStates.get(index);
    const currentPressed: boolean[] = [];
    for (let b: number = 0; b < rawGamepad.buttons.length; b += 1) {
      currentPressed.push(rawGamepad.buttons[b].pressed);
    }

    if (previousPressed !== undefined) {
      for (let b: number = 0; b < currentPressed.length; b += 1) {
        const wasPressed: boolean = b < previousPressed.length && previousPressed[b];
        const isPressed: boolean = currentPressed[b];

        if (isPressed && !wasPressed) {
          const eventData: GamepadButtonEvent = {
            type: InputEventType.GamepadButtonDown,
            index,
            button: b,
            timestamp: performance.now(),
          };
          this.eventHandler(eventData);
        } else if (!isPressed && wasPressed) {
          const eventData: GamepadButtonEvent = {
            type: InputEventType.GamepadButtonUp,
            index,
            button: b,
            timestamp: performance.now(),
          };
          this.eventHandler(eventData);
        }
      }
    }

    this.previousButtonStates.set(index, currentPressed);
  }

  /**
   * 获取指定手柄的上一帧轴数据
   * 在更新 gamepadStates 之前调用以保存旧值用于变化检测
   */
  private getPreviousAxes(index: number): readonly number[] {
    const previousState: GamepadState | undefined = this.gamepadStates.get(index);
    if (previousState === undefined) {
      return [];
    }
    return previousState.axes;
  }

  /**
   * 检测游戏手柄轴值变化
   * 轴值变化超过阈值（0.01）时触发 GamepadAxis 事件
   * @param previousAxes 上一帧的轴数据，用于与当前帧比较
   */
  private detectAxisChanges(index: number, rawGamepad: Gamepad, previousAxes: readonly number[]): void {
    if (this.eventHandler === null) {
      return;
    }

    for (let a: number = 0; a < rawGamepad.axes.length; a += 1) {
      const previousValue: number = a < previousAxes.length
        ? previousAxes[a]
        : 0;
      const currentValue: number = rawGamepad.axes[a];
      const difference: number = currentValue - previousValue;

      if (difference > 0.01 || difference < -0.01) {
        const eventData: GamepadAxisEvent = {
          type: InputEventType.GamepadAxis,
          index,
          axis: a,
          value: currentValue,
          timestamp: performance.now(),
        };
        this.eventHandler(eventData);
      }
    }
  }

  /** 获取指定索引的游戏手柄状态 */
  getState(index: number): GamepadState | null {
    const state: GamepadState | undefined = this.gamepadStates.get(index);
    if (state === undefined) {
      return null;
    }
    return state;
  }

  /** 是否有至少一个游戏手柄已连接 */
  isConnected(): boolean {
    return this.connected;
  }
}