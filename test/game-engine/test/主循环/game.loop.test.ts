/**
 * GameLoop 游戏主循环单元测试
 */

import { EngineConfig, EngineState, FrameTiming } from '../../src/models/engine';
import { PerformanceTimer } from '../../src/services/impl/timer/timer';
import { FixedTimestep } from '../../src/pipelines/gameloop/fixed.timestep';
import { DefaultGameLoop, GameLoop, GameLoopCallbacks } from '../../src/pipelines/gameloop/game.loop';

describe('DefaultGameLoop', () => {
  let config: EngineConfig;
  let timer: PerformanceTimer;
  let fixedTimestep: FixedTimestep;
  let gameLoop: GameLoop;

  beforeEach(() => {
    config = {
      canvasId: 'test-canvas',
      width: 800,
      height: 600,
      maxFps: 60,
      fixedTimestep: 1 / 60,
    };
    timer = new PerformanceTimer();
    fixedTimestep = new FixedTimestep(1 / 60);
    gameLoop = new DefaultGameLoop(config, timer, fixedTimestep);
  });

  describe('initial state', () => {
    test('should be Stopped after construction', () => {
      expect(gameLoop.getState()).toBe(EngineState.Stopped);
    });

    test('should return 0 FPS before starting', () => {
      expect(gameLoop.getFps()).toBe(0);
    });
  });

  describe('state transitions', () => {
    test('start should transition to Running', () => {
      const callbacks: GameLoopCallbacks = {
        onFixedUpdate: jest.fn(),
        onRender: jest.fn(),
      };
      gameLoop.start(callbacks);
      expect(gameLoop.getState()).toBe(EngineState.Running);
    });

    test('pause should transition to Paused', () => {
      const callbacks: GameLoopCallbacks = {
        onFixedUpdate: jest.fn(),
        onRender: jest.fn(),
      };
      gameLoop.start(callbacks);
      gameLoop.pause();
      expect(gameLoop.getState()).toBe(EngineState.Paused);
    });

    test('resume should transition back to Running', () => {
      const callbacks: GameLoopCallbacks = {
        onFixedUpdate: jest.fn(),
        onRender: jest.fn(),
      };
      gameLoop.start(callbacks);
      gameLoop.pause();
      gameLoop.resume();
      expect(gameLoop.getState()).toBe(EngineState.Running);
    });

    test('stop from Running should transition to Stopped', () => {
      const callbacks: GameLoopCallbacks = {
        onFixedUpdate: jest.fn(),
        onRender: jest.fn(),
      };
      gameLoop.start(callbacks);
      gameLoop.stop();
      expect(gameLoop.getState()).toBe(EngineState.Stopped);
    });

    test('stop from Paused should transition to Stopped', () => {
      const callbacks: GameLoopCallbacks = {
        onFixedUpdate: jest.fn(),
        onRender: jest.fn(),
      };
      gameLoop.start(callbacks);
      gameLoop.pause();
      gameLoop.stop();
      expect(gameLoop.getState()).toBe(EngineState.Stopped);
    });
  });

  describe('no-op transitions', () => {
    test('starting twice should not throw', () => {
      const callbacks: GameLoopCallbacks = {
        onFixedUpdate: jest.fn(),
        onRender: jest.fn(),
      };
      gameLoop.start(callbacks);
      expect(() => gameLoop.start(callbacks)).not.toThrow();
    });

    test('stopping twice should not throw', () => {
      gameLoop.stop();
      expect(() => gameLoop.stop()).not.toThrow();
    });

    test('pausing when Stopped should not throw', () => {
      expect(() => gameLoop.pause()).not.toThrow();
    });

    test('resuming when Stopped should not throw', () => {
      expect(() => gameLoop.resume()).not.toThrow();
    });

    test('pausing when Paused should not throw', () => {
      const callbacks: GameLoopCallbacks = {
        onFixedUpdate: jest.fn(),
        onRender: jest.fn(),
      };
      gameLoop.start(callbacks);
      gameLoop.pause();
      expect(() => gameLoop.pause()).not.toThrow();
    });
  });

  describe('FPS tracking', () => {
    test('should start with 0 FPS', () => {
      expect(gameLoop.getFps()).toBe(0);
    });
  });
});