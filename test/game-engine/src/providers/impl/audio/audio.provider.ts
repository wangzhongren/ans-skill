// 音频提供者实现
// 职责: 整合音效与音乐管理器，对外暴露统一的 AudioProvider 接口

import {
  AudioConfig,
  AudioProviderState,
  MusicPlayOptions,
  PlaybackState,
  SoundPlayOptions,
} from '../../../models/audio';
import { AudioProvider } from '../../abstract/audio';
import { MusicManager } from './music';
import { SoundManager } from './sound';

/** 默认音频配置 */
const DEFAULT_AUDIO_CONFIG: AudioConfig = {
  masterVolume: 1,
  sfxVolume: 1,
  musicVolume: 1,
  muted: false,
};

/** GameAudioProvider — 游戏音频提供者实现 */
export class GameAudioProvider implements AudioProvider {
  private audioContext: AudioContext | null = null;
  private masterGainNode: GainNode | null = null;
  private soundManager: SoundManager | null = null;
  private musicManager: MusicManager | null = null;
  private config: AudioConfig = { ...DEFAULT_AUDIO_CONFIG };
  private initialized: boolean = false;

  initialize(): void {
    if (this.initialized) {
      return;
    }

    try {
      this.audioContext = new AudioContext();

      this.masterGainNode = this.audioContext.createGain();
      this.masterGainNode.gain.value = this.config.masterVolume;
      this.masterGainNode.connect(this.audioContext.destination);

      this.soundManager = new SoundManager(this.audioContext, this.masterGainNode);
      this.musicManager = new MusicManager(this.audioContext, this.masterGainNode);

      this.initialized = true;
    } catch (error) {
      console.error('Failed to initialize AudioProvider:', error);
      throw error;
    }
  }

  // ---- 音效 ----

  async loadSound(key: string, src: string): Promise<void> {
    this.ensureInitialized();
    await this.soundManager!.loadSound(key, src);
  }

  playSound(key: string, options?: SoundPlayOptions): string {
    this.ensureInitialized();
    return this.soundManager!.playSound(key, options);
  }

  stopSound(soundId: string): void {
    this.ensureInitialized();
    this.soundManager!.stopSound(soundId);
  }

  // ---- 音乐 ----

  async loadMusic(key: string, src: string): Promise<void> {
    this.ensureInitialized();
    await this.musicManager!.loadMusic(key, src);
  }

  playMusic(key: string, options?: MusicPlayOptions): void {
    this.ensureInitialized();
    this.musicManager!.playMusic(key, options);
  }

  pauseMusic(): void {
    this.ensureInitialized();
    this.musicManager!.pauseMusic();
  }

  resumeMusic(): void {
    this.ensureInitialized();
    this.musicManager!.resumeMusic();
  }

  stopMusic(): void {
    this.ensureInitialized();
    this.musicManager!.stopMusic();
  }

  getMusicState(): PlaybackState {
    if (this.musicManager === null) {
      return PlaybackState.Stopped;
    }
    return this.musicManager.getState();
  }

  getCurrentMusicKey(): string | null {
    if (this.musicManager === null) {
      return null;
    }
    return this.musicManager.getCurrentKey();
  }

  // ---- 音量控制 ----

  setMasterVolume(volume: number): void {
    const clampedVolume = Math.max(0, Math.min(1, volume));
    this.config = { ...this.config, masterVolume: clampedVolume };

    if (this.masterGainNode !== null) {
      this.masterGainNode.gain.value = this.config.muted ? 0 : clampedVolume;
    }
  }

  setSfxVolume(volume: number): void {
    const clampedVolume = Math.max(0, Math.min(1, volume));
    this.config = { ...this.config, sfxVolume: clampedVolume };

    if (this.soundManager !== null) {
      this.soundManager.setVolume(clampedVolume);
    }
  }

  setMusicVolume(volume: number): void {
    const clampedVolume = Math.max(0, Math.min(1, volume));
    this.config = { ...this.config, musicVolume: clampedVolume };

    if (this.musicManager !== null) {
      this.musicManager.setVolume(clampedVolume);
    }
  }

  getConfig(): AudioConfig {
    return { ...this.config };
  }

  // ---- 静音 ----

  mute(): void {
    this.config = { ...this.config, muted: true };
    if (this.masterGainNode !== null) {
      this.masterGainNode.gain.value = 0;
    }
  }

  unmute(): void {
    this.config = { ...this.config, muted: false };
    if (this.masterGainNode !== null) {
      this.masterGainNode.gain.value = this.config.masterVolume;
    }
  }

  isMuted(): boolean {
    return this.config.muted;
  }

  // ---- 状态 ----

  getState(): AudioProviderState {
    let activeSoundCount = 0;
    if (this.soundManager !== null) {
      activeSoundCount = this.soundManager.getActiveSoundCount();
    }

    let musicState = PlaybackState.Stopped;
    if (this.musicManager !== null) {
      musicState = this.musicManager.getState();
    }

    let currentMusicKey: string | null = null;
    if (this.musicManager !== null) {
      currentMusicKey = this.musicManager.getCurrentKey();
    }

    return {
      config: { ...this.config },
      currentMusicKey,
      musicState,
      activeSoundCount,
    };
  }

  // ---- 销毁 ----

  destroy(): void {
    if (this.soundManager !== null) {
      try {
        this.soundManager.destroy();
      } catch (error) {
        console.error('Error destroying SoundManager:', error);
      }
      this.soundManager = null;
    }

    if (this.musicManager !== null) {
      try {
        this.musicManager.destroy();
      } catch (error) {
        console.error('Error destroying MusicManager:', error);
      }
      this.musicManager = null;
    }

    if (this.masterGainNode !== null) {
      try {
        this.masterGainNode.disconnect();
      } catch (error) {
        console.error('Error disconnecting master gain node:', error);
      }
      this.masterGainNode = null;
    }

    if (this.audioContext !== null) {
      try {
        this.audioContext.close();
      } catch (error) {
        console.error('Error closing AudioContext:', error);
      }
      this.audioContext = null;
    }

    this.initialized = false;
    this.config = { ...DEFAULT_AUDIO_CONFIG };
  }

  /** 确保音频提供者已初始化 */
  private ensureInitialized(): void {
    if (!this.initialized || this.soundManager === null || this.musicManager === null) {
      throw new Error('AudioProvider has not been initialized. Call initialize() first.');
    }
  }
}