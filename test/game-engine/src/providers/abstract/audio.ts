// 音频提供者契约
// 职责: 定义音频播放抽象接口，供浏览器 AudioContext / Web Audio API 实现遵循

import {
  AudioConfig,
  AudioProviderState,
  MusicPlayOptions,
  PlaybackState,
  SoundPlayOptions,
} from '../../models/audio';

/** 音频提供者抽象接口 */
export interface AudioProvider {
  /** 初始化音频上下文并创建音频管理器 */
  initialize(): void;

  // ---- 音效 ----

  /** 加载音效资源，加载完成后可通过 playSound 播放 */
  loadSound(key: string, src: string): Promise<void>;

  /** 播放已加载的音效，返回唯一播放标识用于控制 */
  playSound(key: string, options?: SoundPlayOptions): string;

  /** 停止指定音效的播放 */
  stopSound(soundId: string): void;

  // ---- 音乐 ----

  /** 加载音乐资源，加载完成后可通过 playMusic 播放 */
  loadMusic(key: string, src: string): Promise<void>;

  /** 播放指定音乐，自动停止当前正在播放的音乐 */
  playMusic(key: string, options?: MusicPlayOptions): void;

  /** 暂停当前音乐 */
  pauseMusic(): void;

  /** 恢复当前暂停的音乐 */
  resumeMusic(): void;

  /** 停止当前音乐 */
  stopMusic(): void;

  /** 获取当前音乐的播放状态 */
  getMusicState(): PlaybackState;

  /** 获取当前正在播放的音乐 key，无音乐播放时返回 null */
  getCurrentMusicKey(): string | null;

  // ---- 音量控制 ----

  /** 设置主音量（0-1） */
  setMasterVolume(volume: number): void;

  /** 设置音效通道音量（0-1） */
  setSfxVolume(volume: number): void;

  /** 设置音乐通道音量（0-1） */
  setMusicVolume(volume: number): void;

  /** 获取当前音频配置 */
  getConfig(): AudioConfig;

  // ---- 静音 ----

  /** 静音所有音频 */
  mute(): void;

  /** 取消静音 */
  unmute(): void;

  /** 是否处于静音状态 */
  isMuted(): boolean;

  // ---- 状态 ----

  /** 获取音频提供者完整状态快照 */
  getState(): AudioProviderState;

  // ---- 销毁 ----

  /** 停止所有播放并释放音频资源 */
  destroy(): void;
}