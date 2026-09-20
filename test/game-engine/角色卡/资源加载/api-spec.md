# API 规范: 资源加载

## 导出

### 模型 (`src/models/resource.ts`)

| 导出 | 类型 | 说明 |
| --- | --- | --- |
| `ResourceType` | `enum` | 资源类型枚举: Image, Audio, Data, Font |
| `ResourceDescriptor` | `interface` | 资源描述符，包含 key, type, src |
| `Resource<T>` | `interface` | 已加载的资源，包含 descriptor, data, loadedAt |
| `ResourceManifest` | `interface` | 资源清单，包含 resources 数组 |
| `LoadProgress` | `interface` | 加载进度，包含 total, loaded, failed, percent |
| `ResourceEvent` | `interface` | 资源加载事件，包含 key, type, success, error |

### 提供者契约 (`src/providers/abstract/resource.ts`)

| 导出 | 类型 | 说明 |
| --- | --- | --- |
| `ResourceProvider` | `interface` | 资源加载提供者抽象接口 |
| `ResourceCacheStats` | `interface` | 资源缓存统计信息 |

`ResourceProvider` 接口方法:

| 方法 | 签名 | 说明 |
| --- | --- | --- |
| `load` | `(descriptor: ResourceDescriptor) => Promise<Resource>` | 加载单个资源 |
| `loadMany` | `(manifest: ResourceManifest, onProgress?: callback) => Promise<Resource[]>` | 批量加载资源 |
| `get` | `(key: string) => Resource \| undefined` | 从缓存获取资源 |
| `has` | `(key: string) => boolean` | 检查资源是否已缓存 |
| `release` | `(key: string) => void` | 释放指定资源 |
| `releaseAll` | `() => void` | 释放所有资源 |
| `getProgress` | `() => LoadProgress` | 获取当前加载进度 |
| `onProgress` | `(callback) => void` | 注册进度回调 |
| `offProgress` | `(callback) => void` | 移除进度回调 |
| `getStats` | `() => ResourceCacheStats` | 获取缓存统计 |
| `getLoadedCount` | `() => number` | 获取已加载数量 |
| `getTotalCount` | `() => number` | 获取请求总数 |

### 提供者实现 (`src/providers/impl/resource/resource.loader.ts`)

| 导出 | 类型 | 说明 |
| --- | --- | --- |
| `GameResourceLoader` | `class` | 资源加载器实现 |
| `ResourceDataLoader` | `interface` | 资源数据加载器内部接口 |

### 图片加载器 (`src/providers/impl/resource/image.loader.ts`)

| 导出 | 类型 | 说明 |
| --- | --- | --- |
| `ImageLoader` | `class` | 图片资源加载器（implements ResourceDataLoader） |

### 音频加载器 (`src/providers/impl/resource/audio.loader.ts`)

| 导出 | 类型 | 说明 |
| --- | --- | --- |
| `AudioLoader` | `class` | 音频资源加载器（implements ResourceDataLoader） |

### 数据加载器 (`src/providers/impl/resource/data.loader.ts`)

| 导出 | 类型 | 说明 |
| --- | --- | --- |
| `DataLoader` | `class` | 数据资源加载器（implements ResourceDataLoader） |

## 依赖

| 依赖模块 | 引用方式 | 说明 |
| --- | --- | --- |
| `src/models/resource.ts` | 直接 import | 资源类型定义 |
| 无其他内部依赖 | — | 资源加载不依赖其他角色模块 |

## 装配说明

```typescript
import { GameResourceLoader } from './providers/impl/resource/resource.loader';
import { ImageLoader } from './providers/impl/resource/image.loader';
import { AudioLoader } from './providers/impl/resource/audio.loader';
import { DataLoader } from './providers/impl/resource/data.loader';
import { type ResourceProvider } from './providers/abstract/resource';
import { type ResourceManifest } from './models/resource';

// 创建加载器实例并注入子加载器
const resourceLoader: ResourceProvider = new GameResourceLoader([
  new ImageLoader(),
  new AudioLoader(),
  new DataLoader(),
]);

// 加载单个资源
const image = await resourceLoader.load({
  key: 'player_sprite',
  type: ResourceType.Image,
  src: './assets/player.png',
});

// 批量加载资源
const manifest: ResourceManifest = {
  resources: [
    { key: 'bgm', type: ResourceType.Audio, src: './assets/bgm.mp3' },
    { key: 'config', type: ResourceType.Data, src: './assets/config.json' },
  ],
};
const resources = await resourceLoader.loadMany(manifest, (progress) => {
  console.log(`Loading: ${progress.percent}%`);
});

// 使用已加载的资源
const cachedImage = resourceLoader.get('player_sprite');

// 释放资源
resourceLoader.release('player_sprite');
```

## 其他角色集成要点

- **渲染**: 通过 `ResourceProvider.get(key)` 获取已加载的图片资源
  （`HTMLImageElement`），传递给渲染器的 `drawTexture` 方法
- **音频**: 资源加载模块负责加载音频数据到 `HTMLAudioElement`，
  音频角色通过 `ResourceProvider.get(key)` 获取后控制播放
- **装配**: 创建 `GameResourceLoader` 实例，注入所有需要的子加载器，
  将其纳入引擎上下文供其他角色使用
- **场景管理**: 场景切换时调用 `releaseAll()` 清空资源缓存