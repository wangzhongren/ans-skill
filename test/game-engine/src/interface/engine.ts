// 引擎公共 API 外观
// 装配角色维护，其他角色通过此入口使用引擎功能

import { EngineConfig, EngineState, FrameTiming } from '../models/engine';
import { RenderPipelineConfig } from '../models/render';
import {
  DefaultGameLoop,
  GameLoop,
  GameLoopCallbacks,
} from '../pipelines/gameloop/game.loop';
import { FixedTimestep } from '../pipelines/gameloop/fixed.timestep';
import { RenderPipeline } from '../pipelines/render/render.pipeline';
import {
  AudioProvider,
  BrowserInputProvider,
  CanvasRenderer,
  GameAudioProvider,
  GameResourceLoader,
  ImageLoader,
  AudioLoader,
  DataLoader,
  InputProvider,
  ResourceProvider,
} from '../providers/public';
import {
  EntityService,
  GameEntityService,
  PerformanceTimer,
  SceneManager,
  SceneManagerImpl,
  Timer,
} from '../services/public';

/** 引擎公共接口 */
export interface Engine {
  /** 初始化引擎所有子系统 */
  initialize(): Promise<void>;

  /** 启动游戏主循环 */
  start(): void;

  /** 停止游戏主循环 */
  stop(): void;

  /** 暂停游戏主循环 */
  pause(): void;

  /** 恢复游戏主循环 */
  resume(): void;

  /** 销毁引擎，释放所有资源 */
  destroy(): Promise<void>;

  /** 获取当前引擎运行状态 */
  getState(): EngineState;

  /** 获取当前帧率估算值 */
  getFps(): number;

  // ---- 子系统访问 ----

  /** 获取实体管理服务 */
  getEntityService(): EntityService;

  /** 获取场景管理器 */
  getSceneManager(): SceneManager;

  /** 获取输入提供者 */
  getInputProvider(): InputProvider;

  /** 获取音频提供者 */
  getAudioProvider(): AudioProvider;

  /** 获取资源加载提供者 */
  getResourceProvider(): ResourceProvider;

  /** 获取渲染管线 */
  getRenderPipeline(): RenderPipeline;
}

/** 引擎默认实现 — 组合所有子系统并协调其生命周期 */
export class GameEngine implements Engine {
  private readonly config: EngineConfig;
  private entityService!: EntityService;
  private sceneManager!: SceneManager;
  private timer!: Timer;
  private inputProvider!: InputProvider;
  private audioProvider!: AudioProvider;
  private resourceProvider!: ResourceProvider;
  private canvasRenderer!: CanvasRenderer;
  private renderPipeline!: RenderPipeline;
  private fixedTimestep!: FixedTimestep;
  private gameLoop!: GameLoop;
  private initialized: boolean = false;
  private destroyed: boolean = false;

  constructor(config: EngineConfig) {
    this.config = { ...config };
  }

  /** 初始化引擎所有子系统 */
  async initialize(): Promise<void> {
    if (this.initialized) {
      return;
    }

    try {
      // 1. 获取 Canvas 元素
      const canvas: HTMLCanvasElement | null = document.getElementById(
        this.config.canvasId,
      ) as HTMLCanvasElement | null;
      if (canvas === null) {
        throw new Error(
          `Canvas element with id "${this.config.canvasId}" not found`,
        );
      }

      // 2. 设置 Canvas 尺寸
      canvas.width = this.config.width;
      canvas.height = this.config.height;

      // 3. 创建并初始化渲染器
      this.canvasRenderer = new CanvasRenderer({
        clearColor: this.config.backgroundColor ?? {
          r: 0,
          g: 0,
          b: 0,
          a: 255,
        },
        enableBatch: true,
      });
      this.canvasRenderer.initialize(canvas);

      // 4. 创建渲染管线
      const renderPipelineConfig: RenderPipelineConfig = {
        clearColor: this.config.backgroundColor ?? {
          r: 0,
          g: 0,
          b: 0,
          a: 255,
        },
        layers: [
          { name: 'default', zIndex: 0, visible: true },
        ],
        defaultCamera: {
          position: { x: 0, y: 0 },
          zoom: 1,
          viewport: {
            x: 0,
            y: 0,
            width: this.config.width,
            height: this.config.height,
          },
        },
      };
      this.renderPipeline = new RenderPipeline(
        this.canvasRenderer,
        renderPipelineConfig,
      );

      // 5. 创建实体管理服务
      this.entityService = new GameEntityService();

      // 6. 创建场景管理器
      this.sceneManager = new SceneManagerImpl();

      // 7. 创建计时器
      this.timer = new PerformanceTimer();

      // 8. 创建固定时间步长
      const fixedDt: number = this.config.fixedTimestep ?? (1 / 60);
      this.fixedTimestep = new FixedTimestep(fixedDt);

      // 9. 创建输入提供者并初始化
      this.inputProvider = new BrowserInputProvider();
      this.inputProvider.initialize();

      // 10. 创建音频提供者并初始化
      this.audioProvider = new GameAudioProvider();
      this.audioProvider.initialize();

      // 11. 创建资源加载器
      this.resourceProvider = new GameResourceLoader([
        new ImageLoader(),
        new AudioLoader(),
        new DataLoader(),
      ]);

      // 12. 创建游戏主循环
      this.gameLoop = new DefaultGameLoop(
        this.config,
        this.timer,
        this.fixedTimestep,
      );

      // 13. 加载初始资源清单（可选）
      if (this.config.resourceManifest !== undefined) {
        try {
          await this.resourceProvider.loadMany(this.config.resourceManifest);
        } catch (error) {
          console.error('Failed to load initial resources:', error);
        }
      }

      this.initialized = true;
    } catch (error) {
      console.error('Engine initialization failed:', error);
      throw error;
    }
  }

  /** 启动游戏主循环 */
  start(): void {
    this.ensureInitialized();
    this.ensureNotDestroyed();

    const callbacks: GameLoopCallbacks = {
      onFixedUpdate: (deltaTime: number) => {
        this.sceneManager.update(deltaTime);
      },
      onRender: (_interpolation: number, _frameTiming: FrameTiming) => {
        this.renderPipeline.beginFrame();
        this.renderPipeline.endFrame();
      },
    };

    this.gameLoop.start(callbacks);
  }

  /** 停止游戏主循环 */
  stop(): void {
    this.gameLoop.stop();
  }

  /** 暂停游戏主循环 */
  pause(): void {
    this.gameLoop.pause();
  }

  /** 恢复游戏主循环 */
  resume(): void {
    this.ensureInitialized();
    this.gameLoop.resume();
  }

  /** 销毁引擎，释放所有资源 */
  async destroy(): Promise<void> {
    if (this.destroyed) {
      return;
    }

    try {
      this.gameLoop.stop();

      this.audioProvider.destroy();

      this.inputProvider.destroy();

      this.renderPipeline.destroy();

      this.resourceProvider.releaseAll();

      this.destroyed = true;
      this.initialized = false;
    } catch (error) {
      console.error('Engine destruction error:', error);
      throw error;
    }
  }

  /** 获取当前引擎运行状态 */
  getState(): EngineState {
    return this.gameLoop.getState();
  }

  /** 获取当前帧率估算值 */
  getFps(): number {
    return this.gameLoop.getFps();
  }

  // ---- 子系统访问 ----

  getEntityService(): EntityService {
    this.ensureInitialized();
    this.ensureNotDestroyed();
    return this.entityService;
  }

  getSceneManager(): SceneManager {
    this.ensureInitialized();
    this.ensureNotDestroyed();
    return this.sceneManager;
  }

  getInputProvider(): InputProvider {
    this.ensureInitialized();
    this.ensureNotDestroyed();
    return this.inputProvider;
  }

  getAudioProvider(): AudioProvider {
    this.ensureInitialized();
    this.ensureNotDestroyed();
    return this.audioProvider;
  }

  getResourceProvider(): ResourceProvider {
    this.ensureInitialized();
    this.ensureNotDestroyed();
    return this.resourceProvider;
  }

  getRenderPipeline(): RenderPipeline {
    this.ensureInitialized();
    this.ensureNotDestroyed();
    return this.renderPipeline;
  }

  /** 确保引擎已初始化，否则抛出错误 */
  private ensureInitialized(): void {
    if (!this.initialized) {
      throw new Error(
        'Engine has not been initialized. Call initialize() first.',
      );
    }
  }

  /** 确保引擎未被销毁，否则抛出错误 */
  private ensureNotDestroyed(): void {
    if (this.destroyed) {
      throw new Error('Engine has been destroyed and cannot be used.');
    }
  }
}