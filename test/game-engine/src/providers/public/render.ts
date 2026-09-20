// 渲染提供者公共入口
// Pipeline 层通过此入口引用 Provider 实现

export { Renderer } from '../abstract/renderer';
export { CanvasRenderer, CanvasRendererConfig } from '../impl/render/canvas.renderer';
export { TextureManager, TextureLoadOptions } from '../impl/render/texture';
export { SpriteBatcher, SpriteBatch } from '../impl/render/sprite.batcher';