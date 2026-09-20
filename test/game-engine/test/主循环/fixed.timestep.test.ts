/**
 * FixedTimestep 固定时间步长单元测试
 */

import { FixedTimestep, FixedTimestepResult } from '../../src/pipelines/gameloop/fixed.timestep';

describe('FixedTimestep', () => {
  describe('constructor', () => {
    test('should create with default maxFrameTime', () => {
      const timestep: FixedTimestep = new FixedTimestep(1 / 60);
      expect(timestep.getFixedDeltaTime()).toBeCloseTo(1 / 60);
      expect(timestep.getAccumulator()).toBe(0);
    });

    test('should create with custom maxFrameTime', () => {
      const timestep: FixedTimestep = new FixedTimestep(1 / 60, 0.5);
      expect(timestep.getFixedDeltaTime()).toBeCloseTo(1 / 60);
    });

    test('should throw if fixedDeltaTime is zero', () => {
      expect(() => new FixedTimestep(0)).toThrow();
    });

    test('should throw if fixedDeltaTime is negative', () => {
      expect(() => new FixedTimestep(-0.1)).toThrow();
    });

    test('should throw if maxFrameTime is zero', () => {
      expect(() => new FixedTimestep(1 / 60, 0)).toThrow();
    });

    test('should throw if maxFrameTime is less than fixedDeltaTime', () => {
      expect(() => new FixedTimestep(0.1, 0.05)).toThrow();
    });
  });

  describe('update', () => {
    test('should return 0 steps when accumulator is below threshold', () => {
      const timestep: FixedTimestep = new FixedTimestep(1 / 60);
      const result: FixedTimestepResult = timestep.update(1 / 120);
      expect(result.steps).toBe(0);
    });

    test('should return 1 step when accumulator reaches threshold', () => {
      const timestep: FixedTimestep = new FixedTimestep(1 / 60);
      const result: FixedTimestepResult = timestep.update(1 / 60);
      expect(result.steps).toBe(1);
    });

    test('should return multiple steps for large deltaTime', () => {
      const timestep: FixedTimestep = new FixedTimestep(1 / 60);
      const result: FixedTimestepResult = timestep.update(1 / 30);
      expect(result.steps).toBe(2);
    });

    test('should accumulate remaining time as interpolation', () => {
      const timestep: FixedTimestep = new FixedTimestep(1 / 60);
      // deltaTime = 1/120, less than 1/60, so accumulator = 1/120, interpolation = 0.5
      const result: FixedTimestepResult = timestep.update(1 / 120);
      expect(result.steps).toBe(0);
      expect(result.interpolation).toBeCloseTo(0.5, 1);
    });

    test('should cap deltaTime at maxFrameTime', () => {
      const timestep: FixedTimestep = new FixedTimestep(1 / 60, 0.1);
      // Pass deltaTime much larger than maxFrameTime
      const result: FixedTimestepResult = timestep.update(10);
      // Should be capped at 0.1 / (1/60) = 6 steps
      expect(result.steps).toBe(6);
    });

    test('should return 0 steps for negative deltaTime', () => {
      const timestep: FixedTimestep = new FixedTimestep(1 / 60);
      const result: FixedTimestepResult = timestep.update(-0.1);
      expect(result.steps).toBe(0);
      expect(result.interpolation).toBe(0);
    });

    test('should accumulate across multiple updates', () => {
      const timestep: FixedTimestep = new FixedTimestep(1 / 60);
      timestep.update(1 / 120); // acc = 1/120
      const result: FixedTimestepResult = timestep.update(1 / 120); // acc = 1/60
      expect(result.steps).toBe(1);
    });

    test('should maintain remainder after consuming steps', () => {
      const timestep: FixedTimestep = new FixedTimestep(1 / 60);
      // delta = 1/30 = 2/60, steps = 2, remainder = 0
      const result: FixedTimestepResult = timestep.update(0.05);
      // 0.05 / 0.016666... = 3 steps with some remainder
      const expectedSteps: number = Math.floor(0.05 / (1 / 60));
      expect(result.steps).toBe(expectedSteps);
    });
  });

  describe('reset', () => {
    test('should clear accumulator to zero', () => {
      const timestep: FixedTimestep = new FixedTimestep(1 / 60);
      timestep.update(1 / 30);
      timestep.reset();
      expect(timestep.getAccumulator()).toBe(0);
    });

    test('should start fresh after reset', () => {
      const timestep: FixedTimestep = new FixedTimestep(1 / 60);
      timestep.update(1 / 30);
      timestep.reset();
      const result: FixedTimestepResult = timestep.update(1 / 60);
      expect(result.steps).toBe(1);
    });
  });

  describe('edge cases', () => {
    test('should handle exactly zero deltaTime', () => {
      const timestep: FixedTimestep = new FixedTimestep(1 / 60);
      const result: FixedTimestepResult = timestep.update(0);
      expect(result.steps).toBe(0);
    });

    test('should handle deltaTime exactly equal to fixedDeltaTime', () => {
      const timestep: FixedTimestep = new FixedTimestep(1 / 60);
      const result: FixedTimestepResult = timestep.update(1 / 60);
      expect(result.steps).toBe(1);
      expect(result.interpolation).toBeCloseTo(0, 1);
    });
  });
});