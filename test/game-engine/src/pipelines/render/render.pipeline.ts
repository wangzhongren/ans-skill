// 渲染管线
// 职责: 编排渲染流程，管理渲染层和绘制顺序

import { Camera, Color, Rect, RenderCommand, RenderCommandType, RenderPipelineConfig, RenderStats, SpriteData } from '../../models/render';
import { Renderer } from '../../providers/abstract/renderer';

/** 渲染管线 — 管理帧渲染生命周期 */
export class RenderPipeline {
  private readonly commandQueue: RenderCommand[] = [];
  private frameCount: number = 0;

  constructor(
    private readonly renderer: Renderer,
    private config: RenderPipelineConfig,
  ) {}

  /** 更新管线配置 */
  updateConfig(config: Partial<RenderPipelineConfig>): void {
    this.config = { ...this.config, ...config };
  }

  /** 开始新帧 */
  beginFrame(camera?: Camera): void {
    const activeCamera = camera ?? this.config.defaultCamera;
    this.renderer.beginFrame(activeCamera);
    this.renderer.clear(this.config.clearColor);
    this.commandQueue.length = 0;
  }

  /** 提交一个渲染命令 */
  submitCommand(command: RenderCommand): void {
    this.commandQueue.push(command);
  }

  /** 提交精灵绘制到队列 */
  submitSprite(sprite: SpriteData): void {
    this.commandQueue.push({
      type: RenderCommandType.Sprite,
      layer: sprite.layer,
      data: sprite,
    });
  }

  /** 提交矩形绘制到队列 */
  submitRect(rect: Rect, color: Color, layer: number = 0): void {
    this.commandQueue.push({
      type: RenderCommandType.Rect,
      layer,
      data: rect,
      color,
    });
  }

  /** 结束当前帧，执行所有排队的渲染命令 */
  endFrame(): void {
    // 按图层排序
    const sorted = [...this.commandQueue].sort((a, b) => a.layer - b.layer);

    for (const command of sorted) {
      this.executeCommand(command);
    }

    this.renderer.endFrame();
    this.frameCount++;
  }

  /** 获取当前帧渲染统计 */
  getStats(): RenderStats {
    return this.renderer.getStats();
  }

  /** 获取已渲染的总帧数 */
  get totalFrames(): number {
    return this.frameCount;
  }

  /** 销毁管线 */
  destroy(): void {
    this.commandQueue.length = 0;
    this.renderer.destroy();
  }

  /** 执行单个渲染命令 */
  private executeCommand(command: RenderCommand): void {
    switch (command.type) {
      case RenderCommandType.Sprite: {
        const sprite = command.data as SpriteData;
        this.renderer.drawSprite(sprite);
        break;
      }
      case RenderCommandType.Rect: {
        const rect = command.data as Rect;
        this.renderer.drawRect(rect, command.color!);
        break;
      }
      case RenderCommandType.Clear: {
        this.renderer.clear(command.color!);
        break;
      }
      default:
        break;
    }
  }
}