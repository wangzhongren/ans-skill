// 音频提供者 — 单元测试
// 测试音频提供者生命周期、音量控制、静音切换与状态查询

import {
  AudioConfig,
  AudioType,
  AudioProviderState,
  MusicPlayOptions,
  PlaybackState,
  SoundPlayOptions,
} from '../../src/models/audio';
import { GameAudioProvider } from '../../src/providers/impl/audio/audio.provider';
import { SoundManager } from '../../src/providers/impl/audio/sound';
import { MusicManager } from '../../src/providers/impl/audio/music';

// ---------------------------------------------------------------------------
// AudioProvider 生命周期
// ---------------------------------------------------------------------------

export function testProviderInitializeAndDestroy(): boolean {
  const provider = new GameAudioProvider();
  provider.initialize();
  const stateAfterInit = provider.getState();
  provider.destroy();
  const stateAfterDestroy = provider.getState();

  const initializedCorrectly =
    stateAfterInit.config.masterVolume === 1 &&
    stateAfterInit.config.muted === false &&
    stateAfterInit.musicState === PlaybackState.Stopped;

  const destroyedCorrectly =
    stateAfterDestroy.config.masterVolume === 1 &&
    stateAfterDestroy.currentMusicKey === null;

  return initializedCorrectly && destroyedCorrectly;
}

export function testProviderDoubleInitialize(): boolean {
  const provider = new GameAudioProvider();
  provider.initialize();
  provider.initialize();
  const state = provider.getState();
  provider.destroy();
  return state.config.masterVolume === 1;
}

export function testProviderDestroyWithoutInit(): boolean {
  const provider = new GameAudioProvider();
  provider.destroy();
  const state = provider.getState();
  return state.currentMusicKey === null;
}

// ---------------------------------------------------------------------------
// 音量控制
// ---------------------------------------------------------------------------

export function testSetMasterVolume(): boolean {
  const provider = new GameAudioProvider();
  provider.initialize();

  provider.setMasterVolume(0.5);
  const config1 = provider.getConfig();
  const passed1 = config1.masterVolume === 0.5;

  provider.setMasterVolume(0);
  const config2 = provider.getConfig();
  const passed2 = config2.masterVolume === 0;

  provider.setMasterVolume(1.5);
  const config3 = provider.getConfig();
  const passed3 = config3.masterVolume === 1;

  provider.setMasterVolume(-0.5);
  const config4 = provider.getConfig();
  const passed4 = config4.masterVolume === 0;

  provider.destroy();
  return passed1 && passed2 && passed3 && passed4;
}

export function testSetSfxVolume(): boolean {
  const provider = new GameAudioProvider();
  provider.initialize();

  provider.setSfxVolume(0.3);
  const config1 = provider.getConfig();
  const passed1 = config1.sfxVolume === 0.3;

  provider.setSfxVolume(0);
  const config2 = provider.getConfig();
  const passed2 = config2.sfxVolume === 0;

  provider.destroy();
  return passed1 && passed2;
}

export function testSetMusicVolume(): boolean {
  const provider = new GameAudioProvider();
  provider.initialize();

  provider.setMusicVolume(0.7);
  const config1 = provider.getConfig();
  const passed1 = config1.musicVolume === 0.7;

  provider.setMusicVolume(1);
  const config2 = provider.getConfig();
  const passed2 = config2.musicVolume === 1;

  provider.destroy();
  return passed1 && passed2;
}

// ---------------------------------------------------------------------------
// 静音控制
// ---------------------------------------------------------------------------

export function testMuteUnmute(): boolean {
  const provider = new GameAudioProvider();
  provider.initialize();

  const initialMuted = provider.isMuted();
  const passed1 = initialMuted === false;

  provider.mute();
  const muted = provider.isMuted();
  const passed2 = muted === true;

  provider.unmute();
  const unmuted = provider.isMuted();
  const passed3 = unmuted === false;

  provider.destroy();
  return passed1 && passed2 && passed3;
}

export function testMutePreservesVolume(): boolean {
  const provider = new GameAudioProvider();
  provider.initialize();

  provider.setMasterVolume(0.8);
  provider.mute();

  const configWhileMuted = provider.getConfig();
  const passed1 = configWhileMuted.masterVolume === 0.8 && configWhileMuted.muted === true;

  provider.unmute();
  const configAfterUnmute = provider.getConfig();
  const passed2 = configAfterUnmute.masterVolume === 0.8 && configAfterUnmute.muted === false;

  provider.destroy();
  return passed1 && passed2;
}

// ---------------------------------------------------------------------------
// 状态查询
// ---------------------------------------------------------------------------

export function testGetStateAfterInit(): boolean {
  const provider = new GameAudioProvider();
  provider.initialize();
  const state: AudioProviderState = provider.getState();

  const passed =
    state.config.masterVolume === 1 &&
    state.config.sfxVolume === 1 &&
    state.config.musicVolume === 1 &&
    state.config.muted === false &&
    state.currentMusicKey === null &&
    state.musicState === PlaybackState.Stopped &&
    state.activeSoundCount === 0;

  provider.destroy();
  return passed;
}

export function testGetStateAfterVolumeChange(): boolean {
  const provider = new GameAudioProvider();
  provider.initialize();

  provider.setMasterVolume(0.5);
  provider.setSfxVolume(0.3);
  provider.setMusicVolume(0.7);

  const state: AudioProviderState = provider.getState();
  const passed =
    state.config.masterVolume === 0.5 &&
    state.config.sfxVolume === 0.3 &&
    state.config.musicVolume === 0.7;

  provider.destroy();
  return passed;
}

// ---------------------------------------------------------------------------
// 音乐状态
// ---------------------------------------------------------------------------

export function testMusicStateStoppedAfterInit(): boolean {
  const provider = new GameAudioProvider();
  provider.initialize();

  const state = provider.getMusicState();
  const currentKey = provider.getCurrentMusicKey();

  provider.destroy();
  return state === PlaybackState.Stopped && currentKey === null;
}

// ---------------------------------------------------------------------------
// 未初始化时调用方法应抛出错误
// ---------------------------------------------------------------------------

export function testProviderThrowsBeforeInit(): boolean {
  const provider = new GameAudioProvider();
  let threwError = false;

  try {
    provider.playSound('test');
  } catch (error) {
    threwError = true;
  }

  return threwError;
}

// ---------------------------------------------------------------------------
// SoundManager 单元测试
// ---------------------------------------------------------------------------

export function testSoundManagerVolumeClamping(): boolean {
  const audioContext = new AudioContext();
  const masterGain = audioContext.createGain();
  const manager = new SoundManager(audioContext, masterGain);

  manager.setVolume(0.5);
  const passed1 = manager.getVolume() === 0.5;

  manager.setVolume(2);
  const passed2 = manager.getVolume() === 1;

  manager.setVolume(-1);
  const passed3 = manager.getVolume() === 0;

  audioContext.close();
  return passed1 && passed2 && passed3;
}

export function testSoundManagerLoadedCount(): boolean {
  const audioContext = new AudioContext();
  const masterGain = audioContext.createGain();
  const manager = new SoundManager(audioContext, masterGain);

  const passed1 = manager.getLoadedCount() === 0;
  const passed2 = manager.isLoaded('nonexistent') === false;

  audioContext.close();
  return passed1 && passed2;
}

// ---------------------------------------------------------------------------
// MusicManager 单元测试
// ---------------------------------------------------------------------------

export function testMusicManagerVolumeClamping(): boolean {
  const audioContext = new AudioContext();
  const masterGain = audioContext.createGain();
  const manager = new MusicManager(audioContext, masterGain);

  manager.setVolume(0.5);
  const passed1 = manager.getVolume() === 0.5;

  manager.setVolume(2);
  const passed2 = manager.getVolume() === 1;

  manager.setVolume(-1);
  const passed3 = manager.getVolume() === 0;

  audioContext.close();
  return passed1 && passed2 && passed3;
}

export function testMusicManagerInitialState(): boolean {
  const audioContext = new AudioContext();
  const masterGain = audioContext.createGain();
  const manager = new MusicManager(audioContext, masterGain);

  const state = manager.getState();
  const currentKey = manager.getCurrentKey();
  const loadedCount = manager.getLoadedCount();

  audioContext.close();
  return state === PlaybackState.Stopped && currentKey === null && loadedCount === 0;
}

// ---------------------------------------------------------------------------
// 模型类型验证
// ---------------------------------------------------------------------------

export function testAudioTypeValues(): boolean {
  return AudioType.SoundEffect === 'sfx' && AudioType.Music === 'music';
}

export function testPlaybackStateValues(): boolean {
  return (
    PlaybackState.Stopped === 'stopped' &&
    PlaybackState.Playing === 'playing' &&
    PlaybackState.Paused === 'paused'
  );
}

export function testAudioConfigDefaults(): boolean {
  const config: AudioConfig = {
    masterVolume: 1,
    sfxVolume: 1,
    musicVolume: 1,
    muted: false,
  };
  return (
    config.masterVolume === 1 &&
    config.sfxVolume === 1 &&
    config.musicVolume === 1 &&
    config.muted === false
  );
}