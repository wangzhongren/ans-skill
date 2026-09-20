// 精灵批处理实现
// 职责: 合并精灵 draw call，减少上下文切换

import { Color, Rect, SpriteData, Transform, Vector2 } from '../../../models/render';

/** 批处理后的绘制批次 */
export interface SpriteBatch {
  readonly textureKey: string;
  readonly sprites: readonly SpriteData[];
  readonly layer: number;
}

/** 精灵批处理器 — 按纹理和图层合并精灵 */
export class SpriteBatcher {
  private readonly spriteQueue: SpriteData[] = [];
  private readonly defaultColor: Color = { r: 255, g: 255, b: 255, a: 255 };

  /** 向队列中添加精灵 */
  add(sprite: SpriteData): void {
    this.spriteQueue.push(sprite);
  }

  /** 快速添加精灵 — 使用默认白色和默认变换 */
  addSimple(
    textureKey: string,
    destRect: Rect,
    layer: number = 0,
    color?: Color,
  ): void {
    const transform: Transform = {
      position: { x: destRect.x, y: destRect.y },
      rotation: 0,
      scale: { x: 1, y: 1 },
    };
    const sourceRect: Rect = {
      x: 0,
      y: 0,
      width: destRect.width,
      height: destRect.height,
    };
    this.spriteQueue.push({
      textureKey,
      sourceRect,
      destRect,
      transform,
      color: color ?? this.defaultColor,
      layer,
    });
  }

  /** 按纹理和图层排序并生成批次 */
  flush(): readonly SpriteBatch[] {
    const sorted = [...this.spriteQueue].sort((a, b) => {
      if (a.layer !== b.layer) return a.layer - b.layer;
      return a.textureKey.localeCompare(b.textureKey);
    });

    const batches: SpriteBatch[] = [];
    let currentBatch: SpriteData[] = [];
    let currentKey = '';
    let currentLayer = -1;

    for (const sprite of sorted) {
      if (sprite.textureKey !== currentKey || sprite.layer !== currentLayer) {
        if (currentBatch.length > 0) {
          batches.push({
            textureKey: currentKey,
            sprites: currentBatch,
            layer: currentLayer,
          });
        }
        currentBatch = [];
        currentKey = sprite.textureKey;
        currentLayer = sprite.layer;
      }
      currentBatch.push(sprite);
    }

    if (currentBatch.length > 0) {
      batches.push({
        textureKey: currentKey,
        sprites: currentBatch,
        layer: currentLayer,
      });
    }

    this.spriteQueue.length = 0;
    return batches;
  }

  /** 当前队列中的精灵数量 */
  get queuedCount(): number {
    return this.spriteQueue.length;
  }

  /** 清空队列 */
  clear(): void {
    this.spriteQueue.length = 0;
  }
}