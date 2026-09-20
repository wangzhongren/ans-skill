# API 规范: 音频

## 导出

### 模型 (`src/models/audio.ts`)

| 导出 | 类型 | 说明 |
| --- | --- | --- |
| `AudioType` | `enum` | 音频资源类型枚举（`sfx` / `music`） |
| `AudioResource` | `interface` | 音频资源引用，包含 key、类型、src、duration |
| `PlaybackState` | `enum` | 播放状态枚举（`stopped` / `playing` / `paused`） |
| `AudioConfig` | `interface` | 音频配置（masterVolume, sfxVolume, musicVolume, muted） |
| `SoundPlayOptions` | `interface` | 音效播放选项（volume, loop, playbackRate） |
| `MusicPlayOptions` | `interface` | 音乐播放选项（volume, loop, fadeInDuration） |
| `AudioProviderState` | `interface` | 音频提供者状态快照（config, currentMusicKey, musicState, activeSoundCount） |

### 提供者契约 (`src/providers/abstract/audio.ts`)

| 导出 | 类型 | 说明 |
| --- | --- | --- |
| `AudioProvider` | `interface` | 音频提供者公共接口 |

### 提供者实现 (`src/providers/impl/audio/audio.provider.ts`)

| 导出 | 类型 | 说明 |
| --- | --- | --- |
| `GameAudioProvider` | `class` | 音频提供者实现 |

### 音效管理器 (`src/providers/impl/audio/sound.ts`)

| 导出 | 类型 | 说明 |
| --- | --- | --- |
| `SoundManager` | `class` | 音效管理器（内部使用，不建议对外导出） |

### 音乐管理器 (`src/providers/impl/audio/music.ts`)

| 导出 | 类型 | 说明 |
| --- | --- | --- |
| `MusicManager` | `class` | 音乐管理器（内部使用，不建议对外导出） |

## AudioProvider 接口

### 生命周期

| 方法 | 签名 | 说明 |
| --- | --- | --- |
| `initialize` | `(): void` | 初始化音频上下文并创建音频管理器 |
| `destroy` | `(): void` | 停止所有播放并释放音频资源 |

### 音效

| 方法 | 签名 | 说明 |
| --- | --- | --- |
| `loadSound` | `(key: string, src: string): Promise<void>` | 加载音效资源 |
| `playSound` | `(key: string, options?: SoundPlayOptions): string` | 播放已加载的音效，返回音效 ID |
| `stopSound` | `(soundId: string): void` | 停止指定音效 |

### 音乐

| 方法 | 签名 | 说明 |
| --- | --- | --- |
| `loadMusic` | `(key: string, src: string): Promise<void>` | 加载音乐资源 |
| `playMusic` | `(key: string, options?: MusicPlayOptions): void` | 播放指定音乐 |
| `pauseMusic` | `(): void` | 暂停当前音乐 |
| `resumeMusic` | `(): void` | 恢复当前暂停的音乐 |
| `stopMusic` | `(): void` | 停止当前音乐 |
| `getMusicState` | `(): PlaybackState` | 获取当前音乐播放状态 |
| `getCurrentMusicKey` | `(): string \| null` | 获取当前音乐 key |

### 音量控制

| 方法 | 签名 | 说明 |
| --- | --- | --- |
| `setMasterVolume` | `(volume: number): void` | 设置主音量（0-1） |
| `setSfxVolume` | `(volume: number): void` | 设置音效通道音量（0-1） |
| `setMusicVolume` | `(volume: number): void` | 设置音乐通道音量（0-1） |
| `getConfig` | `(): AudioConfig` | 获取当前音频配置 |

### 静音

| 方法 | 签名 | 说明 |
| --- | --- | --- |
| `mute` | `(): void` | 静音所有音频 |
| `unmute` | `(): void` | 取消静音 |
| `isMuted` | `(): boolean` | 是否处于静音状态 |

### 状态

| 方法 | 签名 | 说明 |
| --- | --- | --- |
| `getState` | `(): AudioProviderState` | 获取音频提供者完整状态快照 |

## 依赖

| 依赖模块 | 引用方式 | 说明 |
| --- | --- | --- |
| `src/models/audio.ts` | 直接 import | 音频类型定义 |
| 无其他内部依赖 | — | 音频提供者不依赖其他角色模块 |

## 装配说明

```typescript
import { GameAudioProvider } from './src/providers/impl/audio/audio.provider';
import { type AudioProvider } from './src/providers/abstract/audio';
import { type MusicPlayOptions, type SoundPlayOptions } from './src/models/audio';

// 创建音频提供者实例
const audioProvider: AudioProvider = new GameAudioProvider();

// 初始化
audioProvider.initialize();

// 加载音效
await audioProvider.loadSound('explosion', 'assets/sfx/explosion.mp3');

// 播放音效
const soundId: string = audioProvider.playSound('explosion', { volume: 0.8 });

// 停止指定音效
audioProvider.stopSound(soundId);

// 加载并播放音乐
await audioProvider.loadMusic('bgm_main', 'assets/music/main_theme.mp3');
const musicOptions: MusicPlayOptions = { volume: 0.5, loop: true, fadeInDuration: 2 };
audioProvider.playMusic('bgm_main', musicOptions);

// 暂停/恢复音乐
audioProvider.pauseMusic();
audioProvider.resumeMusic();

// 停止音乐
audioProvider.stopMusic();

// 音量控制
audioProvider.setMasterVolume(0.8);
audioProvider.setSfxVolume(1.0);
audioProvider.setMusicVolume(0.7);

// 静音
audioProvider.mute();
audioProvider.unmute();

// 查询状态
const config = audioProvider.getConfig();
const state = audioProvider.getState();
console.log(config.masterVolume, state.musicState);

// 销毁
audioProvider.destroy();
```

## 其他角色集成要点

- **资源加载**: 通过 `loadSound` / `loadMusic` 方法加载音频资源（或由资源加载角色统一管理后提供 URL）。
- **主循环**: 音频提供者不需要每帧更新，音乐状态变化通过内部事件处理。
- **装配**: `GameAudioProvider` 在引擎初始化时创建，通过 `AudioProvider` 接口注入到需要音频功能的模块。