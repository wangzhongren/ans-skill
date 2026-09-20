// Provider 层统一入口
// 装配角色维护，其他角色通过此入口引用 Provider 实现

// Render (re-export existing render public entry)
export {
  CanvasRenderer,
  CanvasRendererConfig,
  Renderer,
  SpriteBatch,
  SpriteBatcher,
  TextureLoadOptions,
  TextureManager,
} from './render';

// Input
export { type InputEventHandler, type InputProvider } from '../abstract/input';
export { BrowserInputProvider } from '../impl/input/input.provider';

// Audio
export { type AudioProvider } from '../abstract/audio';
export { GameAudioProvider } from '../impl/audio/audio.provider';

// Resource
export { type ResourceCacheStats, type ResourceProvider } from '../abstract/resource';
export { AudioLoader } from '../impl/resource/audio.loader';
export { DataLoader } from '../impl/resource/data.loader';
export { GameResourceLoader } from '../impl/resource/resource.loader';
export { ImageLoader } from '../impl/resource/image.loader';