// 音频类型定义
// 主拥有者: 音频
// 其他角色以只读方式引用

/** 音频资源类型 */
export enum AudioType {
  SoundEffect = 'sfx',
  Music = 'music',
}

/** 音频资源引用 */
export interface AudioResource {
  readonly key: string;
  readonly type: AudioType;
  readonly src: string;
  readonly duration: number;
}

/** 播放状态 */
export enum PlaybackState {
  Stopped = 'stopped',
  Playing = 'playing',
  Paused = 'paused',
}

/** 音频配置 */
export interface AudioConfig {
  readonly masterVolume: number;
  readonly sfxVolume: number;
  readonly musicVolume: number;
  readonly muted: boolean;
}

/** 音效播放选项 */
export interface SoundPlayOptions {
  readonly volume?: number;
  readonly loop?: boolean;
  readonly playbackRate?: number;
}

/** 音乐播放选项 */
export interface MusicPlayOptions {
  readonly volume?: number;
  readonly loop?: boolean;
  readonly fadeInDuration?: number;
}

/** 音频提供者状态快照 */
export interface AudioProviderState {
  readonly config: AudioConfig;
  readonly currentMusicKey: string | null;
  readonly musicState: PlaybackState;
  readonly activeSoundCount: number;
}