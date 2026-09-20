// 音乐播放实现
// 职责: 管理音乐资源的加载、缓存和播放，支持单轨道播放、暂停、恢复和淡入淡出

import { MusicPlayOptions, PlaybackState } from '../../../models/audio';

/** 音乐管理器 — 管理背景音乐的单轨道播放 */
export class MusicManager {
  private readonly audioContext: AudioContext;
  private readonly audioElementCache: Map<string, string> = new Map();
  private readonly pendingLoads: Map<string, Promise<void>> = new Map();
  private readonly musicGainNode: GainNode;
  private currentSourceNode: MediaElementAudioSourceNode | null = null;
  private currentAudioElement: HTMLAudioElement | null = null;
  private currentMusicKey: string | null = null;
  private musicState: PlaybackState = PlaybackState.Stopped;

  constructor(audioContext: AudioContext, masterGainNode: GainNode) {
    this.audioContext = audioContext;
    this.musicGainNode = audioContext.createGain();
    this.musicGainNode.gain.value = 1;
    this.musicGainNode.connect(masterGainNode);
  }

  /** 获取当前音乐通道音量 */
  getVolume(): number {
    return this.musicGainNode.gain.value;
  }

  /** 设置音乐通道音量 */
  setVolume(volume: number): void {
    this.musicGainNode.gain.value = Math.max(0, Math.min(1, volume));
  }

  /** 加载音乐资源（记录 URL 供后续播放使用） */
  async loadMusic(key: string, src: string): Promise<void> {
    const cached = this.audioElementCache.get(key);
    if (cached !== undefined) {
      return;
    }

    const pending = this.pendingLoads.get(key);
    if (pending !== undefined) {
      return pending;
    }

    const loadPromise = this.loadMusicInternal(key, src);
    this.pendingLoads.set(key, loadPromise);

    try {
      await loadPromise;
    } finally {
      this.pendingLoads.delete(key);
    }
  }

  /** 播放指定音乐，自动停止当前正在播放的音乐 */
  playMusic(key: string, options?: MusicPlayOptions): void {
    const src = this.audioElementCache.get(key);
    if (src === undefined) {
      console.error(`Music not loaded: ${key}`);
      return;
    }

    this.stopCurrentMusic();

    try {
      const audioElement = new Audio(src);
      audioElement.preload = 'auto';

      const loop = options?.loop ?? true;
      audioElement.loop = loop;

      const relativeVolume = options?.volume ?? 1;
      audioElement.volume = relativeVolume;

      const sourceNode = this.audioContext.createMediaElementSource(audioElement);
      sourceNode.connect(this.musicGainNode);

      this.currentAudioElement = audioElement;
      this.currentSourceNode = sourceNode;
      this.currentMusicKey = key;

      const fadeInDuration = options?.fadeInDuration ?? 0;
      if (fadeInDuration > 0) {
        this.applyFadeIn(fadeInDuration, relativeVolume);
      }

      audioElement.play().then(() => {
        this.musicState = PlaybackState.Playing;
      }).catch((error: Error) => {
        console.error(`Failed to play music ${key}:`, error);
        this.musicState = PlaybackState.Stopped;
      });

      audioElement.onended = () => {
        if (!audioElement.loop) {
          this.musicState = PlaybackState.Stopped;
          this.currentMusicKey = null;
        }
      };

      audioElement.onerror = () => {
        console.error(`Music playback error for ${key}`);
        this.musicState = PlaybackState.Stopped;
      };
    } catch (error) {
      console.error(`Failed to create music playback for ${key}:`, error);
    }
  }

  /** 暂停当前音乐 */
  pauseMusic(): void {
    if (this.currentAudioElement === null || this.musicState !== PlaybackState.Playing) {
      return;
    }

    try {
      this.currentAudioElement.pause();
      this.musicState = PlaybackState.Paused;
    } catch (error) {
      console.error('Failed to pause music:', error);
    }
  }

  /** 恢复当前暂停的音乐 */
  resumeMusic(): void {
    if (this.currentAudioElement === null || this.musicState !== PlaybackState.Paused) {
      return;
    }

    try {
      this.currentAudioElement.play().then(() => {
        this.musicState = PlaybackState.Playing;
      }).catch((error: Error) => {
        console.error('Failed to resume music:', error);
      });
    } catch (error) {
      console.error('Failed to resume music:', error);
    }
  }

  /** 停止当前音乐 */
  stopMusic(): void {
    this.stopCurrentMusic();
  }

  /** 获取当前音乐播放状态 */
  getState(): PlaybackState {
    return this.musicState;
  }

  /** 获取当前音乐 key */
  getCurrentKey(): string | null {
    return this.currentMusicKey;
  }

  /** 检查指定 key 的音乐是否已加载 */
  isLoaded(key: string): boolean {
    return this.audioElementCache.has(key);
  }

  /** 获取已加载的音乐数量 */
  getLoadedCount(): number {
    return this.audioElementCache.size;
  }

  /** 释放所有音乐资源 */
  destroy(): void {
    this.stopCurrentMusic();
    this.audioElementCache.clear();
    this.pendingLoads.clear();
    this.currentMusicKey = null;
    this.musicGainNode.disconnect();
  }

  /** 停止并清理当前音乐 */
  private stopCurrentMusic(): void {
    if (this.currentAudioElement !== null) {
      try {
        this.currentAudioElement.pause();
        this.currentAudioElement.src = '';
        this.currentAudioElement.load();
      } catch (error) {
        console.error('Error stopping current music:', error);
      }
      this.currentAudioElement = null;
    }

    if (this.currentSourceNode !== null) {
      try {
        this.currentSourceNode.disconnect();
      } catch (error) {
        console.error('Error disconnecting music source node:', error);
      }
      this.currentSourceNode = null;
    }

    this.musicState = PlaybackState.Stopped;
    this.currentMusicKey = null;
  }

  /** 应用淡入效果 */
  private applyFadeIn(duration: number, targetVolume: number): void {
    if (this.currentAudioElement === null) {
      return;
    }

    const startVolume = 0;
    const steps = 30;
    const intervalMs = (duration * 1000) / steps;
    const volumeIncrement = targetVolume / steps;
    let currentStep = 0;

    this.currentAudioElement.volume = startVolume;

    const fadeInterval = setInterval(() => {
      currentStep += 1;
      if (currentStep >= steps || this.currentAudioElement === null) {
        clearInterval(fadeInterval);
        if (this.currentAudioElement !== null) {
          this.currentAudioElement.volume = targetVolume;
        }
        return;
      }
      if (this.currentAudioElement !== null) {
        this.currentAudioElement.volume = volumeIncrement * currentStep;
      }
    }, intervalMs);
  }

  /** 内部加载音乐: 验证 URL 可访问 */
  private async loadMusicInternal(key: string, src: string): Promise<void> {
    try {
      const response = await fetch(src, { method: 'HEAD' });
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: Failed to load music from ${src}`);
      }
      this.audioElementCache.set(key, src);
    } catch (error) {
      console.error(`Failed to load music ${key} from ${src}:`, error);
      throw error;
    }
  }
}