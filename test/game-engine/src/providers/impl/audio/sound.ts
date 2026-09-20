// 音效播放实现
// 职责: 管理音效资源的加载、缓存和播放，支持多实例重叠播放

import { SoundPlayOptions } from '../../../models/audio';

/** 活跃音效实例信息 */
interface ActiveSoundInfo {
  readonly id: string;
  readonly key: string;
  sourceNode: AudioBufferSourceNode;
  gainNode: GainNode;
}

/** 音效管理器 — 管理短音效的加载与播放 */
export class SoundManager {
  private readonly audioContext: AudioContext;
  private readonly bufferCache: Map<string, AudioBuffer> = new Map();
  private readonly pendingLoads: Map<string, Promise<void>> = new Map();
  private readonly activeSounds: Map<string, ActiveSoundInfo> = new Map();
  private nextSoundId: number = 0;
  private sfxGainNode: GainNode;
  private masterGainNode: GainNode;

  constructor(audioContext: AudioContext, masterGainNode: GainNode) {
    this.audioContext = audioContext;
    this.masterGainNode = masterGainNode;

    this.sfxGainNode = audioContext.createGain();
    this.sfxGainNode.gain.value = 1;
    this.sfxGainNode.connect(masterGainNode);
  }

  /** 获取当前 sfx 增益值 */
  getVolume(): number {
    return this.sfxGainNode.gain.value;
  }

  /** 设置 sfx 通道音量 */
  setVolume(volume: number): void {
    this.sfxGainNode.gain.value = Math.max(0, Math.min(1, volume));
  }

  /** 加载音效文件并解码为 AudioBuffer 存入缓存 */
  async loadSound(key: string, src: string): Promise<void> {
    const cached = this.bufferCache.get(key);
    if (cached !== undefined) {
      return;
    }

    const pending = this.pendingLoads.get(key);
    if (pending !== undefined) {
      return pending;
    }

    const loadPromise = this.loadSoundInternal(key, src);
    this.pendingLoads.set(key, loadPromise);

    try {
      await loadPromise;
    } finally {
      this.pendingLoads.delete(key);
    }
  }

  /** 播放已加载的音效，返回唯一播放标识 */
  playSound(key: string, options?: SoundPlayOptions): string {
    const buffer = this.bufferCache.get(key);
    if (buffer === undefined) {
      console.error(`Sound not loaded: ${key}`);
      return '';
    }

    const soundId = `sfx_${this.nextSoundId}`;
    this.nextSoundId += 1;

    try {
      const sourceNode = this.audioContext.createBufferSource();
      const soundGainNode = this.audioContext.createGain();

      sourceNode.buffer = buffer;

      const playbackRate = options?.playbackRate ?? 1;
      sourceNode.playbackRate.value = playbackRate;

      const loop = options?.loop ?? false;
      sourceNode.loop = loop;

      const relativeVolume = options?.volume ?? 1;
      soundGainNode.gain.value = relativeVolume;

      sourceNode.connect(soundGainNode);
      soundGainNode.connect(this.sfxGainNode);

      sourceNode.start(0);

      const soundInfo: ActiveSoundInfo = {
        id: soundId,
        key,
        sourceNode,
        gainNode: soundGainNode,
      };

      this.activeSounds.set(soundId, soundInfo);

      sourceNode.onended = () => {
        this.cleanupSound(soundId);
      };

      return soundId;
    } catch (error) {
      console.error(`Failed to play sound ${key}:`, error);
      return '';
    }
  }

  /** 停止指定音效播放 */
  stopSound(soundId: string): void {
    const info = this.activeSounds.get(soundId);
    if (info === undefined) {
      return;
    }

    try {
      info.sourceNode.stop();
      info.sourceNode.disconnect();
      info.gainNode.disconnect();
    } catch (error) {
      console.error(`Failed to stop sound ${soundId}:`, error);
    }

    this.activeSounds.delete(soundId);
  }

  /** 停止所有正在播放的音效 */
  stopAllSounds(): void {
    const soundIds = Array.from(this.activeSounds.keys());
    for (const soundId of soundIds) {
      this.stopSound(soundId);
    }
  }

  /** 当前活跃音效数量 */
  getActiveSoundCount(): number {
    return this.activeSounds.size;
  }

  /** 检查指定 key 的音效是否已加载 */
  isLoaded(key: string): boolean {
    return this.bufferCache.has(key);
  }

  /** 获取已加载的音效数量 */
  getLoadedCount(): number {
    return this.bufferCache.size;
  }

  /** 释放所有音效资源 */
  destroy(): void {
    this.stopAllSounds();
    this.bufferCache.clear();
    this.pendingLoads.clear();
    this.sfxGainNode.disconnect();
  }

  /** 移除已结束的音效实例 */
  private cleanupSound(soundId: string): void {
    const info = this.activeSounds.get(soundId);
    if (info !== undefined) {
      try {
        info.sourceNode.disconnect();
        info.gainNode.disconnect();
      } catch (error) {
        console.error(`Error during sound cleanup ${soundId}:`, error);
      }
      this.activeSounds.delete(soundId);
    }
  }

  /** 内部加载音效: 从 URL 获取数据并解码 */
  private async loadSoundInternal(key: string, src: string): Promise<void> {
    let arrayBuffer: ArrayBuffer;

    try {
      const response = await fetch(src);
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: Failed to load sound from ${src}`);
      }
      arrayBuffer = await response.arrayBuffer();
    } catch (error) {
      console.error(`Failed to fetch sound ${key} from ${src}:`, error);
      throw error;
    }

    try {
      const audioBuffer = await this.audioContext.decodeAudioData(arrayBuffer);
      this.bufferCache.set(key, audioBuffer);
    } catch (error) {
      console.error(`Failed to decode sound data for ${key}:`, error);
      throw error;
    }
  }
}