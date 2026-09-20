// 渲染提供者契约
// 职责: 定义渲染器抽象接口，供 Canvas/WebGL 等实现遵循

import { Camera, Color, Rect, RenderStats, SpriteData, Texture } from '../../models/render';

/** 渲染器抽象接口 */
export interface Renderer {
  /** 使用指定 canvas 初始化渲染器 */
  initialize(canvas: HTMLCanvasElement): void;

  /** 开始新帧，设置相机变换 */
  beginFrame(camera: Camera): void;

  /** 结束当前帧，提交所有绘制 */
  endFrame(): void;

  /** 用纯色清空画布 */
  clear(color: Color): void;

  /** 绘制单个精灵 */
  drawSprite(sprite: SpriteData): void;

  /** 绘制填充矩形 */
  drawRect(rect: Rect, color: Color): void;

  /** 绘制纹理到目标区域，可选源区域裁剪 */
  drawTexture(texture: Texture, dest: Rect, source?: Rect): void;

  /** 获取当前帧渲染统计 */
  getStats(): RenderStats;

  /** 销毁渲染器，释放资源 */
  destroy(): void;
}