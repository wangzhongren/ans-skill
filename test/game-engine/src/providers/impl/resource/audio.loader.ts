// 音频资源加载器
// 负责加载音频类型的资源，返回 HTMLAudioElement

import {
  type ResourceDescriptor,
  ResourceType,
} from '../../../models/resource';
import { type ResourceDataLoader } from './resource.loader';

/**
 * 音频资源加载器
 *
 * 使用 HTML Audio 对象加载音频资源，加载完成后返回 HTMLAudioElement。
 * 支持音效短音频和音乐长音频的加载，加载后可通过 Audio 接口控制播放。
 */
export class AudioLoader implements ResourceDataLoader {
  readonly type: ResourceType = ResourceType.Audio;

  /**
   * 加载音频资源
   * @param descriptor 资源描述符
   * @returns 加载完成的 HTMLAudioElement
   */
  load(descriptor: ResourceDescriptor): Promise<unknown> {
    return new Promise<HTMLAudioElement>((resolve, reject) => {
      const audio = new Audio();

      audio.preload = 'auto';

      audio.addEventListener('canplaythrough', () => {
        resolve(audio);
      });

      audio.addEventListener('error', () => {
        let errorMessage = 'Unknown audio error';

        if (audio.error !== null) {
          const errorCodes: Record<number, string> = {
            1: 'Audio loading aborted',
            2: 'Audio network error',
            3: 'Audio decoding error',
            4: 'Audio source not supported',
          };
          errorMessage = errorCodes[audio.error.code] ?? errorMessage;
        }

        reject(
          new Error(
            `Failed to load audio resource "${descriptor.key}" from "${descriptor.src}": ${errorMessage}`
          )
        );
      });

      audio.src = descriptor.src;
      audio.load();
    });
  }

  /**
   * 释放音频资源
   * @param data 音频数据（HTMLAudioElement）
   */
  release(data: unknown): void {
    const audio = data as HTMLAudioElement;
    audio.pause();
    audio.removeAttribute('src');
    audio.load();
  }
}