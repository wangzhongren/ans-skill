/**
 * 引擎外观单元测试
 * 装配角色维护
 */

import { EngineConfig, EngineState } from '../../src/models/engine';
import { GameEngine } from '../../src/interface/engine';

describe('EngineConfig', () => {
  test('should create with minimum required fields', () => {
    const config: EngineConfig = {
      canvasId: 'test-canvas',
      width: 800,
      height: 600,
    };
    expect(config.canvasId).toBe('test-canvas');
    expect(config.width).toBe(800);
    expect(config.height).toBe(600);
  });

  test('should create with all optional fields', () => {
    const config: EngineConfig = {
      canvasId: 'game',
      width: 1024,
      height: 768,
      backgroundColor: { r: 0, g: 0, b: 0, a: 255 },
      fixedTimestep: 1 / 30,
      maxFps: 30,
      debug: true,
    };
    expect(config.fixedTimestep).toBeCloseTo(1 / 30);
    expect(config.maxFps).toBe(30);
    expect(config.debug).toBe(true);
    expect(config.backgroundColor).toBeDefined();
  });
});

describe('GameEngine state transitions (DOM-dependent)', () => {
  let mockCanvas: HTMLCanvasElement;
  let mockContext: CanvasRenderingContext2D;
  let config: EngineConfig;

  beforeAll(() => {
    // Create mock canvas with getContext
    mockCanvas = document.createElement('canvas');
    mockContext = mockCanvas.getContext('2d') as CanvasRenderingContext2D;

    // Mock getElementById to return our canvas
    jest.spyOn(document, 'getElementById').mockImplementation(
      (id: string): HTMLElement | null => {
        if (id === 'test-canvas') {
          return mockCanvas;
        }
        return null;
      },
    );
  });

  afterAll(() => {
    jest.restoreAllMocks();
  });

  beforeEach(() => {
    config = {
      canvasId: 'test-canvas',
      width: 800,
      height: 600,
      debug: false,
    };
  });

  test('should create engine instance with config', () => {
    const engine = new GameEngine(config);
    expect(engine).toBeInstanceOf(GameEngine);
    expect(engine.getState()).toBe(EngineState.Stopped);
  });

  test('should initialize subsystems', async () => {
    const engine = new GameEngine(config);
    await engine.initialize();
    expect(engine.getState()).toBe(EngineState.Stopped);
  });

  test('should start and transition to Running', async () => {
    const engine = new GameEngine(config);
    await engine.initialize();
    engine.start();
    expect(engine.getState()).toBe(EngineState.Running);
  });

  test('should pause and transition to Paused', async () => {
    const engine = new GameEngine(config);
    await engine.initialize();
    engine.start();
    engine.pause();
    expect(engine.getState()).toBe(EngineState.Paused);
  });

  test('should resume from Paused to Running', async () => {
    const engine = new GameEngine(config);
    await engine.initialize();
    engine.start();
    engine.pause();
    engine.resume();
    expect(engine.getState()).toBe(EngineState.Running);
  });

  test('should stop and transition to Stopped', async () => {
    const engine = new GameEngine(config);
    await engine.initialize();
    engine.start();
    engine.stop();
    expect(engine.getState()).toBe(EngineState.Stopped);
  });

  test('should destroy and prevent further use', async () => {
    const engine = new GameEngine(config);
    await engine.initialize();
    await engine.destroy();

    // Calling methods on destroyed engine should throw
    expect(() => engine.getEntityService()).toThrow(
      'Engine has been destroyed',
    );
  });

  test('should return subsystem references after initialization', async () => {
    const engine = new GameEngine(config);
    await engine.initialize();

    expect(engine.getEntityService()).toBeDefined();
    expect(engine.getSceneManager()).toBeDefined();
    expect(engine.getInputProvider()).toBeDefined();
    expect(engine.getAudioProvider()).toBeDefined();
    expect(engine.getResourceProvider()).toBeDefined();
    expect(engine.getRenderPipeline()).toBeDefined();
  });

  test('should throw when accessing subsystems before init', () => {
    const engine = new GameEngine(config);
    expect(() => engine.getEntityService()).toThrow(
      'Engine has not been initialized',
    );
  });

  test('should not re-initialize if already initialized', async () => {
    const engine = new GameEngine(config);
    await engine.initialize();
    await engine.initialize(); // second call should be no-op
    expect(engine.getState()).toBe(EngineState.Stopped);
  });

  test('should start with 0 FPS', async () => {
    const engine = new GameEngine(config);
    await engine.initialize();
    expect(engine.getFps()).toBe(0);
  });
});