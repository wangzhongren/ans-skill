// 渲染管线 — 单元测试
// 测试渲染管线生命周期、命令排队与执行

import { RenderPipeline } from '../../src/pipelines/render/render.pipeline';
import { CanvasRenderer } from '../../src/providers/impl/render/canvas.renderer';
import { Camera, Color, Rect, RenderPipelineConfig, SpriteData } from '../../src/models/render';

/** 创建测试用 Canvas */
function createTestCanvas(): HTMLCanvasElement {
  const canvas = document.createElement('canvas');
  canvas.width = 320;
  canvas.height = 240;
  return canvas;
}

/** 创建测试相机 */
function createTestCamera(): Camera {
  return {
    position: { x: 0, y: 0 },
    zoom: 1,
    viewport: { x: 0, y: 0, width: 320, height: 240 },
  };
}

/** 默认管线配置 */
function createDefaultConfig(): RenderPipelineConfig {
  return {
    clearColor: { r: 0, g: 0, b: 0, a: 255 },
    layers: [
      { name: 'background', zIndex: 0, visible: true },
      { name: 'default', zIndex: 1, visible: true },
      { name: 'ui', zIndex: 10, visible: true },
    ],
    defaultCamera: createTestCamera(),
  };
}

// ---------------------------------------------------------------------------
// 渲染管线生命周期
// ---------------------------------------------------------------------------

export function testPipelineBeginEndFrame(): boolean {
  const canvas = createTestCanvas();
  const renderer = new CanvasRenderer();
  renderer.initialize(canvas);
  const pipeline = new RenderPipeline(renderer, createDefaultConfig());

  pipeline.beginFrame();
  pipeline.endFrame();

  const stats = pipeline.getStats();
  const passed = stats.drawCalls >= 0 && pipeline.totalFrames === 1;

  pipeline.destroy();
  return passed;
}

export function testPipelineSubmitRect(): boolean {
  const canvas = createTestCanvas();
  const renderer = new CanvasRenderer();
  renderer.initialize(canvas);
  const pipeline = new RenderPipeline(renderer, createDefaultConfig());

  pipeline.beginFrame();
  pipeline.submitRect({ x: 0, y: 0, width: 50, height: 50 }, { r: 255, g: 0, b: 0, a: 255 }, 0);
  pipeline.endFrame();

  const stats = pipeline.getStats();
  const passed = stats.drawCalls > 0;

  pipeline.destroy();
  return passed;
}

export function testPipelineConfigUpdate(): boolean {
  const renderer = new CanvasRenderer();
  const pipeline = new RenderPipeline(renderer, createDefaultConfig());
  const newColor: Color = { r: 128, g: 128, b: 128, a: 255 };

  pipeline.updateConfig({ clearColor: newColor });

  const passed = true; // 更新无异常
  pipeline.destroy();
  return passed;
}

// ---------------------------------------------------------------------------
// 纹理管理器
// ---------------------------------------------------------------------------

export function testTextureManagerEmptyOnCreate(): boolean {
  const TextureManager = require('../../src/providers/impl/render/texture').TextureManager;
  const tm = new TextureManager();
  return tm.size === 0;
}

// ---------------------------------------------------------------------------
// 精灵批处理器
// ---------------------------------------------------------------------------

export function testBatcherAddAndFlush(): boolean {
  const { SpriteBatcher } = require('../../src/providers/impl/render/sprite.batcher');
  const batcher = new SpriteBatcher();

  batcher.addSimple('tex1', { x: 0, y: 0, width: 32, height: 32 }, 0);
  batcher.addSimple('tex2', { x: 10, y: 10, width: 32, height: 32 }, 1);

  const batches = batcher.flush();

  return batches.length === 2 && batcher.queuedCount === 0;
}

export function testBatcherGroupsByTexture(): boolean {
  const { SpriteBatcher } = require('../../src/providers/impl/render/sprite.batcher');
  const batcher = new SpriteBatcher();

  batcher.addSimple('tex1', { x: 0, y: 0, width: 16, height: 16 }, 0);
  batcher.addSimple('tex1', { x: 20, y: 0, width: 16, height: 16 }, 0);
  batcher.addSimple('tex2', { x: 0, y: 20, width: 16, height: 16 }, 0);

  const batches = batcher.flush();

  return batches.length === 2 && batches[0].sprites.length === 2 && batches[1].sprites.length === 1;
}

export function testBatcherClear(): boolean {
  const { SpriteBatcher } = require('../../src/providers/impl/render/sprite.batcher');
  const batcher = new SpriteBatcher();

  batcher.addSimple('tex1', { x: 0, y: 0, width: 16, height: 16 }, 0);
  batcher.clear();

  return batcher.queuedCount === 0;
}