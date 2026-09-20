# 功能描述: 音频

## 架构概览

```
┌──────────────────────────────────────────────────────────────┐
│                     AudioProvider                             │  ← 公共接口
├──────────────────────────────────────────────────────────────┤
│                    GameAudioProvider                          │  ← 实现
│  ┌──────────────────┐    ┌──────────────────────────────┐    │
│  │   SoundManager    │    │        MusicManager          │    │
│  │  (音效管理)       │    │      (音乐管理)              │    │
│  │  - AudioBuffer 缓存 │   │  - HTMLAudioElement 播放     │    │
│  │  - 多实例重叠播放  │    │  - 单轨道管理               │    │
│  │  - 独立增益节点    │    │  - 淡入效果                 │    │
│  └────────┬─────────┘    └──────────────┬───────────────┘    │
│           │                             │                    │
│           └──────────────┬──────────────┘                    │
│                          ▼                                   │
│                  MasterGainNode                               │
│                  (主音量/静音)                                 │
└──────────────────────────┬───────────────────────────────────┘
                           ▼
                    AudioContext.destination
```

## 分层说明

### 模型层 (`src/models/audio.ts`)

音频系统的类型定义。作为音频角色的主拥有模型，其他角色以只读方式引用。

**关键类型：**
- `AudioType` — 音频资源类型枚举（`sfx` / `music`）
- `AudioResource` — 音频资源引用，包含 key、类型、路径、时长
- `PlaybackState` — 播放状态枚举（`stopped` / `playing` / `paused`）
- `AudioConfig` — 音频配置，包含主音量、音效音量、音乐音量、静音标识
- `SoundPlayOptions` — 音效播放选项（音量倍率、循环、播放速率）
- `MusicPlayOptions` — 音乐播放选项（音量倍率、循环、淡入时长）
- `AudioProviderState` — 音频提供者状态快照

### 提供者契约 (`src/providers/abstract/audio.ts`)

`AudioProvider` 接口定义音频播放的公共契约，包含：
- 生命周期: `initialize`, `destroy`
- 音效: `loadSound`, `playSound`, `stopSound`
- 音乐: `loadMusic`, `playMusic`, `pauseMusic`, `resumeMusic`, `stopMusic`, `getMusicState`, `getCurrentMusicKey`
- 音量: `setMasterVolume`, `setSfxVolume`, `setMusicVolume`, `getConfig`
- 静音: `mute`, `unmute`, `isMuted`
- 状态: `getState`

### 音效管理器 (`src/providers/impl/audio/sound.ts`)

`SoundManager` 使用 Web Audio API (`AudioContext`) 管理短音效的加载与播放。

- 使用 `fetch` + `decodeAudioData` 加载并解码音频文件
- 使用 `Map<string, AudioBuffer>` 缓存已解码的音频数据
- 每次 `playSound` 创建新的 `AudioBufferSourceNode`，支持多实例重叠播放
- 每个音效实例有独立的 `GainNode` 支持独立音量倍率
- 提供音效 ID 以支持停止指定音效
- 音效播放结束后自动清理资源

### 音乐管理器 (`src/providers/impl/audio/music.ts`)

`MusicManager` 使用 HTMLAudioElement 管理背景音乐的单轨道播放。

- 使用 `Map<string, string>` 记录已加载音乐 URL（通过 HEAD 请求验证）
- 使用 HTMLAudioElement 播放，利用浏览器原生流式加载能力
- 支持淡入效果：通过定时器阶梯式递增音量
- 支持暂停/恢复/停止
- 播放结束时自动更新状态
- 切换音乐时自动停止当前播放并清理资源

### 音频提供者实现 (`src/providers/impl/audio/audio.provider.ts`)

`GameAudioProvider` 实现 `AudioProvider` 接口，整合音效与音乐管理器。

**工作流程：**

1. **初始化**: 创建 `AudioContext` → 创建 `MasterGainNode` → 创建 `SoundManager` → 创建 `MusicManager`
2. **音效播放**: `loadSound` 获取并解码音频 (`fetch` + `decodeAudioData`) → 缓存 `AudioBuffer` → `playSound` 创建 `AudioBufferSourceNode` 连接至 `sfxGainNode`
3. **音乐播放**: `loadMusic` 验证 URL → `playMusic` 创建 `HTMLAudioElement`，包装为 `MediaElementAudioSourceNode` 连接至 `musicGainNode`
4. **音量控制**: `setMasterVolume` / `setSfxVolume` / `setMusicVolume` 分别调整对应 `GainNode.gain.value`，值被钳制到 [0, 1]
5. **静音**: `mute` 将 `masterGainNode.gain.value` 置 0 但保留配置值；`unmute` 恢复
6. **销毁**: 停止所有音效 → 停止音乐 → 断开所有节点 → 关闭 `AudioContext`

## 依赖关系

| 组件 | 依赖 |
| --- | --- |
| `GameAudioProvider` | `SoundManager`, `MusicManager` |
| `SoundManager` | Web Audio API (`AudioContext`, `AudioBuffer`, `AudioBufferSourceNode`) |
| `MusicManager` | Web Audio API (`AudioContext`, `MediaElementAudioSourceNode`), HTMLAudioElement |
| 所有组件 | `src/models/audio.ts` 类型定义 |

## 设计决策

1. **音效用 Web Audio API，音乐用 HTMLAudioElement**：音效需要低延迟和重叠播放能力（Web Audio API）；音乐文件较大，使用 HTMLAudioElement 可以利用浏览器的流式加载，无需将整个文件加载到内存。
2. **独立的 GainNode 层级**：MasterGainNode → SfxGainNode / MusicGainNode → 实例级 GainNode（音效），支持精细音量控制。
3. **音效自动清理**：通过 `sourceNode.onended` 回调自动断开节点并移除追踪，防止内存泄漏。
4. **音量值钳制**：所有音量设置均被钳制到 [0, 1] 范围，防止异常值导致音频失真。
5. **状态快照不可变**：`getConfig()` 和 `getState()` 返回新对象，防止外部直接修改。

## 关键代码位置

| 文件 | 功能 |
| --- | --- |
| `src/models/audio.ts` | 音频类型定义 |
| `src/providers/abstract/audio.ts` | 音频提供者契约 |
| `src/providers/impl/audio/audio.provider.ts` | 音频提供者实现 |
| `src/providers/impl/audio/sound.ts` | 音效管理器 |
| `src/providers/impl/audio/music.ts` | 音乐管理器 |

## 质量约束满足情况

- **相邻层合规**: Provider 层只引用 Model 层类型（`src/models/audio.ts`），不跨越 Service/Pipeline 层
- **代码质量**: 所有方法均有真实实现；变量名使用完整描述性命名；无三元运算符；每个 try/catch 都输出错误信息
- **安全**: 音量值钳制到 [0, 1]；调用未初始化的提供者会抛出清晰错误；音效自动清理防泄漏