---
id: role-function-graphs-feature
type: feature
title: Dashboard 内的角色图谱与功能逐步演示
created: "2026-09-20"
updated: "2026-09-20"
timezone: Asia/Shanghai
status: verified
related:
  - role-dashboard-feature
  - optional-code-atlas-change
events:
  - date: "2026-09-20"
    kind: created
    summary: 按角色和功能浏览图谱，支持总览与逐步演示
  - date: "2026-09-20"
    kind: implemented
    summary: 生成角色视图和源码定位步骤，嵌入 Dashboard 并同步角色选择
  - date: "2026-09-20"
    kind: verified
    summary: 62 项测试通过，浏览器验证前进回退、自动播放与 Dashboard 标签切换
---

# 角色功能图谱

1. **按角色生成**：从边界 Section 1 收集声明文件和只读引用，只扩展直接已知引用及功能步骤所需的外部节点。角色图谱彼此独立；全项目静态图谱仍默认关闭。
2. **按功能演示**：依据已有功能描述与源码编排声明式步骤，生成每步的源码行号、片段、哈希和示例状态。支持功能/场景选择、上一/下一步、重置、点击节点和自动播放。
3. **同一 Dashboard**：新增“角色功能图谱”标签；角色详情可直接定位对应角色。嵌入视图隐藏重复导航，同步父页面角色选择和高度。离开图谱标签暂停播放，返回保留当前步骤。
4. **明确证据边界**：演示顺序不冒充运行时跟踪；示例值不由业务源码执行产生。源码/描述/流程定义变化时标为过期并暂停播放。当前主循环暂停恢复清零问题有明确提示，不把隔离验证修复冒充已合入。

## 实现文件

- [生成器](../../scripts/role_atlas.py)
- [功能查看器](../../assets/role-atlas/index.html)
- [Dashboard](../../assets/role-dashboard/index.html)
- [本地只读服务](../../scripts/serve_dashboard.py)
- [角色图谱测试](../../scripts/tests/test_role_atlas.py)
- [使用规范和数据格式](../../references/role-atlas.md)

当前 game-engine 的示例定义位于 `test/game-engine/doc/design/role-flows.json`，输出在项目根 `doc/role-atlas/`。共 8 个角色、9 个功能、50 个步骤，包含资源缓存命中/成功/失败及场景不存在的分支。发现功能描述处于既有嵌套目录时只读兼容，不移动原文件。

## 验证

```sh
python3 scripts/role_atlas.py --root test/game-engine --flows doc/design/role-flows.json
python3 scripts/serve_dashboard.py --root test/game-engine --port 8768
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s scripts/tests -q
```

全部 62 项测试通过。新增 10 项覆盖角色范围、外部单跳引用、状态快照、源码锚点缺失拒绝覆盖、过期识别、空功能、越界读取、重复 ID、单角色更新及纯数据步骤。HTTP 测试增加同源嵌入策略：功能页仅允许同源嵌入，Dashboard 本身禁止被嵌入。

浏览器实测：推进一帧第 3 步显示帧号 11、delta 0.05、更新次数 2、插值 0.5；回退到第 2 步恢复更新次数和插值为 0；切换暂停恢复功能清空旧状态；自动播放到第 4 步停止并显示已知缺陷。集成后 URL 保持 Dashboard 根路径，角色选择进入嵌入视图，下一步联动有效；离开标签后返回仍停留第 2 步且播放已暂停。桌面/窄视图布局已截图检查。

## 限制与发布状态

未启动真实游戏、未发送 Provider 请求、未更新调度状态或授予角色权限。步骤语义由编排者核对，源码片段匹配只证明定位及新鲜度，不等于完整语义证明。依赖提取目前对 JS/TS 使用启发式，其他语言可通过声明式源码步骤展示功能，但不宣称完整静态解析。

业务源码未修改。保留之前的工作区改动，未提交、推送或覆盖本地安装 Skill。
