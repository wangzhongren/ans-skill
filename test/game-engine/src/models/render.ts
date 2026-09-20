// 渲染类型定义
// 主拥有者: 渲染
// 其他角色以只读方式引用

/** 2D 向量 */
export interface Vector2 {
  x: number;
  y: number;
}

/** 变换 */
export interface Transform {
  position: Vector2;
  rotation: number;
  scale: Vector2;
}

/** 纹理引用 */
export interface Texture {
  readonly key: string;
  readonly width: number;
  readonly height: number;
  readonly source: HTMLImageElement | HTMLCanvasElement;
}

/** 颜色 */
export interface Color {
  readonly r: number;
  readonly g: number;
  readonly b: number;
  readonly a: number;
}

/** 矩形区域 */
export interface Rect {
  readonly x: number;
  readonly y: number;
  readonly width: number;
  readonly height: number;
}

/** 渲染层配置 */
export interface RenderLayerConfig {
  readonly name: string;
  readonly zIndex: number;
  readonly visible: boolean;
}

/** 相机 */
export interface Camera {
  readonly position: Vector2;
  readonly zoom: number;
  readonly viewport: Rect;
}

/** 精灵数据 — 描述一个待绘制的精灵实例 */
export interface SpriteData {
  readonly textureKey: string;
  readonly sourceRect: Rect;
  readonly destRect: Rect;
  readonly transform: Transform;
  readonly color: Color;
  readonly layer: number;
}

/** 渲染命令类型 */
export enum RenderCommandType {
  Clear = 'clear',
  Sprite = 'sprite',
  Rect = 'rect',
  Text = 'text',
}

/** 渲染命令 */
export interface RenderCommand {
  readonly type: RenderCommandType;
  readonly layer: number;
  readonly data: SpriteData | Rect | string;
  readonly color?: Color;
}

/** 渲染统计信息 */
export interface RenderStats {
  readonly drawCalls: number;
  readonly spriteCount: number;
  readonly textureCount: number;
  readonly frameTime: number;
  readonly culledCount: number;
}

/** 渲染管线配置 */
export interface RenderPipelineConfig {
  readonly clearColor: Color;
  readonly layers: readonly RenderLayerConfig[];
  readonly defaultCamera: Camera;
}