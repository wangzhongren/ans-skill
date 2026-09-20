/**
 * Timer 计时器单元测试
 */

import { PerformanceTimer } from '../../src/services/impl/timer/timer';

describe('PerformanceTimer', () => {
  let timer: PerformanceTimer;

  beforeEach(() => {
    timer = new PerformanceTimer();
  });

  describe('initial state', () => {
    test('should not be running after construction', () => {
      expect(timer.isRunning()).toBe(false);
    });

    test('should return zero for all timing values when not started', () => {
      expect(timer.getDeltaTime()).toBe(0);
      expect(timer.getElapsedTime()).toBe(0);
      expect(timer.getFrameCount()).toBe(0);
    });
  });

  describe('start', () => {
    test('should set running to true', () => {
      timer.start();
      expect(timer.isRunning()).toBe(true);
    });

    test('should reset frame count to zero', () => {
      timer.start();
      timer.tick();
      timer.tick();
      expect(timer.getFrameCount()).toBe(2);
      timer.start();
      expect(timer.getFrameCount()).toBe(0);
    });
  });

  describe('tick', () => {
    test('should return 0 on first tick after start', () => {
      timer.start();
      const delta: number = timer.tick();
      expect(delta).toBe(0);
    });

    test('should increment frame count on each tick', () => {
      timer.start();
      timer.tick();
      timer.tick();
      expect(timer.getFrameCount()).toBe(2);
    });

    test('should return 0 when not running', () => {
      const delta: number = timer.tick();
      expect(delta).toBe(0);
    });

    test('should return positive delta between ticks', () => {
      timer.start();
      timer.tick(); // first tick, returns 0
      const delta: number = timer.tick(); // second tick
      expect(delta).toBeGreaterThanOrEqual(0);
    });

    test('should cap deltaTime at 1000ms', () => {
      jest.useFakeTimers();
      timer.start();
      timer.tick(); // first tick, delta = 0

      // Advance time by 2000ms
      jest.advanceTimersByTime(2000);
      const delta: number = timer.tick();

      expect(delta).toBeLessThanOrEqual(1.0);
      jest.useRealTimers();
    });
  });

  describe('stop', () => {
    test('should set running to false', () => {
      timer.start();
      timer.stop();
      expect(timer.isRunning()).toBe(false);
    });

    test('should not affect already stopped timer', () => {
      timer.stop();
      expect(timer.isRunning()).toBe(false);
    });
  });

  describe('reset', () => {
    test('should reset all values to initial state', () => {
      timer.start();
      timer.tick();
      timer.tick();
      timer.reset();
      expect(timer.isRunning()).toBe(false);
      expect(timer.getDeltaTime()).toBe(0);
      expect(timer.getElapsedTime()).toBe(0);
      expect(timer.getFrameCount()).toBe(0);
    });
  });

  describe('getElapsedTime', () => {
    test('should increase over time while running', () => {
      jest.useFakeTimers();
      timer.start();
      const timeBefore: number = timer.getElapsedTime();
      jest.advanceTimersByTime(100);
      const timeAfter: number = timer.getElapsedTime();
      expect(timeAfter).toBeGreaterThanOrEqual(timeBefore);
      jest.useRealTimers();
    });

    test('should freeze after stop', () => {
      timer.start();
      timer.stop();
      const frozenTime: number = timer.getElapsedTime();
      expect(timer.getElapsedTime()).toBe(frozenTime);
    });
  });
});