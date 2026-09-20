// Canvas 渲染器实现
// 职责: 基于 Canvas 2D API 实现渲染器接口

import { Camera, Color, Rect, RenderStats, SpriteData, Texture } from '../../../models/render';
import { Renderer } from '../../abstract/renderer';
import { SpriteBatcher } from './sprite.batcher';
import { TextureManager } from './texture';

/** Canvas 渲染器配置 */
export interface CanvasRendererConfig {
  readonly clearColor: Color;
  readonly enableBatch: boolean;
}

/** Canvas 2D 渲染器实现 */
export class CanvasRenderer implements Renderer {
  private canvas: HTMLCanvasElement | null = null;
  private context: CanvasRenderingContext2D | null = null;
  private batcher: SpriteBatcher;
  private textureManager: TextureManager;
  private drawCalls: number = 0;
  private spriteCount: number = 0;
  private frameStartTime: number = 0;
  private culledCount: number = 0;

  constructor(
    private readonly config: CanvasRendererConfig = {
      clearColor: { r: 0, g: 0, b: 0, a: 255 },
      enableBatch: true,
    },
  ) {
    this.batcher = new SpriteBatcher();
    this.textureManager = new TextureManager();
  }

  /** 获取纹理管理器引用 */
  get textures(): TextureManager {
    return this.textureManager;
  }

  initialize(canvas: HTMLCanvasElement): void {
    this.canvas = canvas;
    const ctx = canvas.getContext('2d');
    if (ctx === null) {
      throw new Error('Failed to get 2D rendering context from canvas');
    }
    this.context = ctx;
  }

  beginFrame(camera: Camera): void {
    this.drawCalls = 0;
    this.spriteCount = 0;
    this.culledCount = 0;
    this.frameStartTime = performance.now();

    const ctx = this.context;
    if (ctx === null || this.canvas === null) {
      return;
    }

    ctx.save();
    ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

    // 应用相机变换
    ctx.translate(
      this.canvas.width / 2 - camera.position.x * camera.zoom,
      this.canvas.height / 2 - camera.position.y * camera.zoom,
    );
    ctx.scale(camera.zoom, camera.zoom);
  }

  endFrame(): void {
    if (this.config.enableBatch) {
      this.flushBatches();
    }

    if (this.context !== null) {
      this.context.restore();
    }
  }

  clear(color: Color): void {
    const ctx = this.context;
    if (ctx === null || this.canvas === null) {
      return;
    }

    ctx.save();
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    ctx.fillStyle = this.colorToRgba(color);
    ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
    ctx.restore();
    this.drawCalls++;
  }

  drawSprite(sprite: SpriteData): void {
    if (this.config.enableBatch) {
      this.batcher.add(sprite);
      return;
    }
    this.renderSpriteDirect(sprite);
  }

  drawRect(rect: Rect, color: Color): void {
    const ctx = this.context;
    if (ctx === null) {
      return;
    }

    ctx.fillStyle = this.colorToRgba(color);
    ctx.fillRect(rect.x, rect.y, rect.width, rect.height);
    this.drawCalls++;
  }

  drawTexture(texture: Texture, dest: Rect, source?: Rect): void {
    const ctx = this.context;
    if (ctx === null) {
      return;
    }

    const sx = source?.x ?? 0;
    const sy = source?.y ?? 0;
    const sw = source?.width ?? texture.width;
    const sh = source?.height ?? texture.height;

    ctx.drawImage(texture.source, sx, sy, sw, sh, dest.x, dest.y, dest.width, dest.height);
    this.drawCalls++;
  }

  getStats(): RenderStats {
    return {
      drawCalls: this.drawCalls,
      spriteCount: this.spriteCount,
      textureCount: this.textureManager.size,
      frameTime: performance.now() - this.frameStartTime,
      culledCount: this.culledCount,
    };
  }

  destroy(): void {
    this.batcher.clear();
    this.textureManager.clear();
    this.context = null;
    this.canvas = null;
  }

  /** 渲染单个精灵（非批处理模式） */
  private renderSpriteDirect(sprite: SpriteData): void {
    const ctx = this.context;
    if (ctx === null) {
      return;
    }

    const texture = this.textureManager.get(sprite.textureKey);
    if (texture === undefined) {
      return;
    }

    ctx.save();
    ctx.translate(sprite.transform.position.x, sprite.transform.position.y);
    ctx.rotate(sprite.transform.rotation);
    ctx.scale(sprite.transform.scale.x, sprite.transform.scale.y);
    ctx.globalAlpha = sprite.color.a / 255;
    ctx.drawImage(
      texture.source,
      sprite.sourceRect.x,
      sprite.sourceRect.y,
      sprite.sourceRect.width,
      sprite.sourceRect.height,
      sprite.destRect.x,
      sprite.destRect.y,
      sprite.destRect.width,
      sprite.destRect.height,
    );
    ctx.restore();
    this.drawCalls++;
    this.spriteCount++;
  }

  /** 提交所有批处理批次 */
  private flushBatches(): void {
    const batches = this.batcher.flush();
    for (const batch of batches) {
      this.renderBatch(batch);
    }
  }

  /** 渲染单个批次 */
  private renderBatch(batch: {
    textureKey: string;
    sprites: readonly SpriteData[];
    layer: number;
  }): void {
    const texture = this.textureManager.get(batch.textureKey);
    if (texture === undefined) {
      return;
    }

    const ctx = this.context;
    if (ctx === null) {
      return;
    }

    for (const sprite of batch.sprites) {
      ctx.save();
      ctx.translate(sprite.transform.position.x, sprite.transform.position.y);
      ctx.rotate(sprite.transform.rotation);
      ctx.scale(sprite.transform.scale.x, sprite.transform.scale.y);
      ctx.globalAlpha = sprite.color.a / 255;
      ctx.drawImage(
        texture.source,
        sprite.sourceRect.x,
        sprite.sourceRect.y,
        sprite.sourceRect.width,
        sprite.sourceRect.height,
        sprite.destRect.x,
        sprite.destRect.y,
        sprite.destRect.width,
        sprite.destRect.height,
      );
      ctx.restore();
      this.spriteCount++;
    }
    this.drawCalls++;
  }

  /** 将 Color 转为 Canvas rgba 字符串 */
  private colorToRgba(color: Color): string {
    return `rgba(${color.r},${color.g},${color.b},${color.a / 255})`;
  }
}