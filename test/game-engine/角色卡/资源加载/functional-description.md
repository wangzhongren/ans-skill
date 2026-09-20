# 功能描述: 资源加载

## 概述

资源加载角色负责游戏引擎中各类资源的加载、缓存和释放管理，
支持图片、音频、数据和字体四种资源类型。本模块遵循 Provider
架构模式，通过抽象接口与具体实现分离，为上层系统提供统一的
资源管理能力。

## 核心功能

### 1. 资源加载

- **图片资源加载**: 使用 HTML `Image` 对象加载图片，支持跨域
  加载（`crossOrigin = 'anonymous'`），返回 `HTMLImageElement`
- **音频资源加载**: 使用 HTML `Audio` 对象加载音频，
  监控 `canplaythrough` 事件确保加载完成，返回 `HTMLAudioElement`
- **数据资源加载**: 使用 `Fetch API` 加载数据，支持 JSON 和
  文本（TXT/CSV/XML/YAML）格式，根据文件扩展名自动推断格式
- **字体资源加载**: 类型定义已预留（`ResourceType.Font`），
  由引擎装配方通过注入自定义加载器扩展

### 2. 缓存管理

- 已加载的资源按 `key` 缓存，避免重复加载
- 支持通过 `get(key)` 和 `has(key)` 查询缓存
- 支持单个资源释放（`release(key)`）和全部释放（`releaseAll()`）
- 缓存统计信息通过 `getStats()` 获取

### 3. 批量加载与进度通知

- `loadMany()` 方法支持按资源清单批量加载
- 支持可选的进度回调，每次加载完成后更新进度
- 进度信息包含总数、成功数、失败数和百分比
- 支持通过 `onProgress()` / `offProgress()` 注册/移除监听器

### 4. 资源释放

- 图片资源：清除 `src` 引用以帮助垃圾回收
- 音频资源：暂停播放、移除 `src`、调用 `load()` 重置
- 数据资源：依赖垃圾回收器自动回收内存

## 数据流

```
外部调用方
    │
    ├── load(descriptor) ──────────────────┐
    │                                       │
    ▼                                       │
┌──────────────────────────────────────┐    │
│        GameResourceLoader           │    │
│                                      │    │
│  ┌──────────┐  ┌──────────┐        │    │
│  │  Cache   │  │ Loaders  │        │    │
│  │ (已加载)  │  │ Map:     │        │    │
│  │          │  │ type ->  │        │    │
│  └──────────┘  │ loader   │        │    │
│                └────┬─────┘        │    │
│                     │              │    │
│  ProgressCallbacks──┤              │    │
└─────────────────────┼──────────────┘    │
                      │                  │
         ┌────────────┼────────────┐      │
         ▼            ▼            ▼      │
   ImageLoader  AudioLoader  DataLoader   │
         │            │            │      │
         ▼            ▼            ▼      │
   HTMLImage    HTMLAudio    JSON/Text ───┘
   Element      Element      (fetch)
```

## 与外部系统的关系

| 系统 | 关系 |
| --- | --- |
| 渲染 | `ResourceProvider.get(key)` 获取图片资源数据传递给渲染器 |
| 音频 | 资源加载加载音频数据后，音频角色负责播放控制 |
| 装配 | 创建 `GameResourceLoader` 实例并注入具体加载器，传递到引擎上下文 |
| 场景管理 | 场景切换时调用 `releaseAll()` 清理不需要的资源 |