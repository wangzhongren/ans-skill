// 引擎入口点
// 装配角色维护，负责 DOM 初始化、引擎实例化和系统启动

import { EngineConfig } from './src/models/engine';
import { GameEngine } from './src/interface/engine';

/**
 * 启动游戏引擎
 *
 * 该函数在 DOMContentLoaded 事件触发后执行：
 * 1. 从 HTML 中的 data-* 属性读取配置
 * 2. 创建引擎实例
 * 3. 初始化并启动引擎
 */
async function bootEngine(): Promise<void> {
  const rootElement: HTMLElement | null = document.getElementById('game-root');
  if (rootElement === null) {
    console.error('Boot failed: element #game-root not found in DOM');
    return;
  }

  const canvasId: string =
    rootElement.getAttribute('data-canvas-id') ?? 'game-canvas';
  const width: number = parseInt(
    rootElement.getAttribute('data-width') ?? '800',
    10,
  );
  const height: number = parseInt(
    rootElement.getAttribute('data-height') ?? '600',
    10,
  );
  const debug: boolean =
    rootElement.getAttribute('data-debug') === 'true';

  const config: EngineConfig = {
    canvasId,
    width,
    height,
    fixedTimestep: 1 / 60,
    debug,
  };

  const engine: GameEngine = new GameEngine(config);

  try {
    await engine.initialize();
    engine.start();

    if (debug) {
      exposeEngineForDebug(engine);
    }
  } catch (error) {
    console.error('Failed to boot engine:', error);
  }
}

/**
 * 将引擎实例暴露到全局作用域，便于调试
 * 仅在 debug 模式下生效
 */
function exposeEngineForDebug(engine: GameEngine): void {
  const globalWindow = window as Record<string, unknown>;
  globalWindow.__engine = engine;
  console.log('[Engine] Debug mode enabled. Access engine via window.__engine');
}

// 等待 DOM 就绪后启动
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    bootEngine().catch((error: unknown) => {
      console.error('Engine boot error:', error);
    });
  });
} else {
  bootEngine().catch((error: unknown) => {
    console.error('Engine boot error:', error);
  });
}