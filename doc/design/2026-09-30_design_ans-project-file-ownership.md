---
id: ans-project-file-ownership
type: design
title: ANS 仓库文件归属候选清单
created: "2026-09-30"
updated: "2026-09-30"
timezone: Asia/Shanghai
status: draft
related: [ans-project-role-plan]
events:
  - date: "2026-09-30"
    kind: created
    summary: 按当前 Git 文件清单拟定唯一归属，不授予修改权限
---

# ANS 仓库文件归属候选清单

这是[角色划分方案](2026-09-30_design_ans-project-roles.md)的明细，尚未生效，不是可直接执行的 boundary.md。

清单以 GitLab 工作仓库提交 `a0ba8e9` 的 247 个已跟踪文件为基线，每个文件只出现一次。GitHub 对应版本为 `075c7a4`，额外的 LICENSE 单独说明在方案中。当前新增的两份方案文档不计入这个历史基线。

“按任务维护”表示拟由该角色维护，仍需要任务授权；“历史/样例保留”表示仅负责查找和保管，不能据此改写内容。创建正式边界时，把前者转成具体文件条目，后者放进只读说明，不抄进修改白名单。忽略的 output、缓存、运行数据库和项目 Key 不属于本清单，不通过初始化角色上传或处理。


| 拟负责角色 | 基线文件数 | 拟按任务维护 | 保留只读 |
| --- | --- | --- | --- |
| 项目管理 | 42 | 0 | 42 |
| 技能规范 | 36 | 31 | 5 |
| 执行协作 | 9 | 9 | 0 |
| 可视化工具 | 19 | 19 | 0 |
| 云端与同步 | 43 | 43 | 0 |
| 测试 | 98 | 3 | 95 |

## 项目管理

| 实际路径 | 用途 | 处理方式 |
| --- | --- | --- |
| `doc/change/2026-09-17_change_action-and-communication.md` | 现有历史文档 | 历史保留，默认只读 |
| `doc/change/2026-09-20_change_coordination-table.md` | 现有历史文档 | 历史保留，默认只读 |
| `doc/change/2026-09-20_change_default-project-dashboard.md` | 现有历史文档 | 历史保留，默认只读 |
| `doc/change/2026-09-20_change_optional-code-atlas.md` | 现有历史文档 | 历史保留，默认只读 |
| `doc/change/2026-09-20_change_project-integration-design.md` | 现有历史文档 | 历史保留，默认只读 |
| `doc/change/2026-09-20_change_project-scheduler-role.md` | 现有历史文档 | 历史保留，默认只读 |
| `doc/change/2026-09-20_change_resolve-role-governance-conflicts.md` | 现有历史文档 | 历史保留，默认只读 |
| `doc/change/2026-09-24_change_dashboard-base-path.md` | 现有历史文档 | 历史保留，默认只读 |
| `doc/change/2026-09-24_change_dashboard-project-databases.md` | 现有历史文档 | 历史保留，默认只读 |
| `doc/change/2026-09-25_change_dashboard-admin-simplified.md` | 现有历史文档 | 历史保留，默认只读 |
| `doc/change/2026-09-25_change_local-project-id-first.md` | 现有历史文档 | 历史保留，默认只读 |
| `doc/change/2026-09-26_change_plain-language.md` | 现有历史文档 | 历史保留，默认只读 |
| `doc/change/2026-09-27_change_document-first-handoff.md` | 现有历史文档 | 历史保留，默认只读 |
| `doc/change/2026-09-27_change_human-first-docs.md` | 现有历史文档 | 历史保留，默认只读 |
| `doc/change/2026-09-27_change_readme-quickstart.md` | 现有历史文档 | 历史保留，默认只读 |
| `doc/change/2026-09-27_change_remove-role-sync-preflight.md` | 现有历史文档 | 历史保留，默认只读 |
| `doc/change/2026-09-29_change_readme-architecture-first.md` | 现有历史文档 | 历史保留，默认只读 |
| `doc/change/2026-09-30_change_role-common-and-testing.md` | 现有历史文档 | 历史保留，默认只读 |
| `doc/change/2026-09-30_change_role-feature-docs.md` | 现有历史文档 | 历史保留，默认只读 |
| `doc/change/2026-09-30_change_role-maintainer-stance.md` | 现有历史文档 | 历史保留，默认只读 |
| `doc/design/2026-09-26_design_cloud-first-dashboard.md` | 现有历史文档 | 历史保留，默认只读 |
| `doc/design/2026-09-26_design_manual-bidirectional-sync.md` | 现有历史文档 | 历史保留，默认只读 |
| `doc/design/2026-09-27_design_role-feature-points.md` | 现有历史文档 | 历史保留，默认只读 |
| `doc/design/2026-09-28_design_configurable-document-history.md` | 现有历史文档 | 历史保留，默认只读 |
| `doc/design/2026-09-29_design_role-architecture-viewer.md` | 现有历史文档 | 历史保留，默认只读 |
| `doc/feature/2026-09-12_feature_atlas-queries.md` | 现有历史文档 | 历史保留，默认只读 |
| `doc/feature/2026-09-20_feature_role-dashboard.md` | 现有历史文档 | 历史保留，默认只读 |
| `doc/feature/2026-09-20_feature_role-function-graphs.md` | 现有历史文档 | 历史保留，默认只读 |
| `doc/feature/2026-09-20_feature_task-operations.md` | 现有历史文档 | 历史保留，默认只读 |
| `doc/feature/2026-09-24_feature_dashboard-container.md` | 现有历史文档 | 历史保留，默认只读 |
| `doc/feature/2026-09-24_feature_role-project-context.md` | 现有历史文档 | 历史保留，默认只读 |
| `doc/feature/2026-09-24_feature_shared-dashboard.md` | 现有历史文档 | 历史保留，默认只读 |
| `doc/feature/2026-09-25_feature_dashboard-auto-update.md` | 现有历史文档 | 历史保留，默认只读 |
| `doc/feature/2026-09-25_feature_local-dashboard-config.md` | 现有历史文档 | 历史保留，默认只读 |
| `doc/feature/2026-09-25_feature_role-channel.md` | 现有历史文档 | 历史保留，默认只读 |
| `doc/feature/2026-09-25_feature_role-sync-preflight.md` | 现有历史文档 | 历史保留，默认只读 |
| `doc/feature/2026-09-26_feature_flow-purpose-branch-graph.md` | 现有历史文档 | 历史保留，默认只读 |
| `doc/feature/2026-09-26_feature_manual-versioned-sync.md` | 现有历史文档 | 历史保留，默认只读 |
| `doc/fix/2026-09-20_fix_atlas-root-and-output.md` | 现有历史文档 | 历史保留，默认只读 |
| `doc/fix/2026-09-25_fix_key-creation-feedback.md` | 现有历史文档 | 历史保留，默认只读 |
| `doc/fix/2026-09-25_fix_sync-status-tempdir.md` | 现有历史文档 | 历史保留，默认只读 |
| `doc/guide/2026-09-25_guide_ans-skill-overview.md` | 现有历史文档 | 历史保留，默认只读 |

## 技能规范

| 实际路径 | 用途 | 处理方式 |
| --- | --- | --- |
| `README.md` | 技能产品入口和基础说明 | 按任务维护 |
| `SKILL.md` | 技能产品入口和基础说明 | 按任务维护 |
| `SKILL.zh.md` | 技能产品入口和基础说明 | 按任务维护 |
| `memory/evidence-definition.md` | 技能产品入口和基础说明 | 按任务维护 |
| `references/action-policy.md` | 对外提供的技能规则或使用说明 | 按任务维护 |
| `references/api-spec.md` | 对外提供的技能规则或使用说明 | 按任务维护 |
| `references/architecture.md` | 对外提供的技能规则或使用说明 | 按任务维护 |
| `references/bootstrap-workflow.md` | 对外提供的技能规则或使用说明 | 按任务维护 |
| `references/built-in-assembly.md` | 对外提供的技能规则或使用说明 | 按任务维护 |
| `references/built-in-boundary.md` | 对外提供的技能规则或使用说明 | 按任务维护 |
| `references/documentation-change.md` | 对外提供的技能规则或使用说明 | 按任务维护 |
| `references/documentation-design.md` | 对外提供的技能规则或使用说明 | 按任务维护 |
| `references/documentation-feature.md` | 对外提供的技能规则或使用说明 | 按任务维护 |
| `references/documentation-fix.md` | 对外提供的技能规则或使用说明 | 按任务维护 |
| `references/documentation.md` | 对外提供的技能规则或使用说明 | 按任务维护 |
| `references/entrypoint.md` | 对外提供的技能规则或使用说明 | 按任务维护 |
| `references/evidence.md` | 对外提供的技能规则或使用说明 | 按任务维护 |
| `references/feature-point.md` | 对外提供的技能规则或使用说明 | 按任务维护 |
| `references/functional-description.md` | 对外提供的技能规则或使用说明 | 按任务维护 |
| `references/interface.md` | 对外提供的技能规则或使用说明 | 按任务维护 |
| `references/model.md` | 对外提供的技能规则或使用说明 | 按任务维护 |
| `references/module-boundary.md` | 对外提供的技能规则或使用说明 | 按任务维护 |
| `references/pipeline.md` | 对外提供的技能规则或使用说明 | 按任务维护 |
| `references/project-role.md` | 对外提供的技能规则或使用说明 | 按任务维护 |
| `references/provider.md` | 对外提供的技能规则或使用说明 | 按任务维护 |
| `references/role-card.md` | 对外提供的技能规则或使用说明 | 按任务维护 |
| `references/service.md` | 对外提供的技能规则或使用说明 | 按任务维护 |
| `references/shared-directories.md` | 对外提供的技能规则或使用说明 | 按任务维护 |
| `references/test-role.md` | 对外提供的技能规则或使用说明 | 按任务维护 |
| `references/testing.md` | 对外提供的技能规则或使用说明 | 按任务维护 |
| `references/workflow.md` | 对外提供的技能规则或使用说明 | 按任务维护 |
| `test/documentation-samples/README.md` | 文档写法样例 | 历史样例保留，默认只读 |
| `test/documentation-samples/change/2026-09-27_change_save-exit-feedback.md` | 文档写法样例 | 历史样例保留，默认只读 |
| `test/documentation-samples/design/2026-09-27_design_work-order-draft.md` | 文档写法样例 | 历史样例保留，默认只读 |
| `test/documentation-samples/feature/2026-09-27_feature_save-work-order-draft.md` | 文档写法样例 | 历史样例保留，默认只读 |
| `test/documentation-samples/fix/2026-09-27_fix_close-after-save-failure.md` | 文档写法样例 | 历史样例保留，默认只读 |

## 执行协作

| 实际路径 | 用途 | 处理方式 |
| --- | --- | --- |
| `.gitignore` | 仓库工程配置 | 按任务维护 |
| `references/coordination.md` | 对外提供的技能规则或使用说明 | 按任务维护 |
| `references/scheduler.md` | 对外提供的技能规则或使用说明 | 按任务维护 |
| `references/task-operations.md` | 对外提供的技能规则或使用说明 | 按任务维护 |
| `scripts/coordination_store.py` | 工具实现或入口 | 按任务维护 |
| `scripts/scaffold.ps1` | 工具实现或入口 | 按任务维护 |
| `scripts/scaffold.sh` | 工具实现或入口 | 按任务维护 |
| `scripts/task_ops.py` | 工具实现或入口 | 按任务维护 |
| `scripts/tests/test_task_ops.py` | 本能力的测试/夹具 | 按任务维护 |

## 可视化工具

| 实际路径 | 用途 | 处理方式 |
| --- | --- | --- |
| `assets/architecture-viewer/app.js` | 旧图谱展示资源 | 按任务维护 |
| `assets/architecture-viewer/index.html` | 旧图谱展示资源 | 按任务维护 |
| `assets/architecture-viewer/style.css` | 旧图谱展示资源 | 按任务维护 |
| `assets/code-atlas/viewer.html` | 旧图谱展示资源 | 按任务维护 |
| `assets/role-atlas/index.html` | 旧图谱展示资源 | 按任务维护 |
| `references/code-atlas.md` | 对外提供的技能规则或使用说明 | 按任务维护 |
| `references/role-architecture-viewer.md` | 对外提供的技能规则或使用说明 | 按任务维护 |
| `references/role-atlas.md` | 对外提供的技能规则或使用说明 | 按任务维护 |
| `scripts/query_atlas.py` | 工具实现或入口 | 按任务维护 |
| `scripts/render_architecture.py` | 工具实现或入口 | 按任务维护 |
| `scripts/role_atlas.py` | 工具实现或入口 | 按任务维护 |
| `scripts/sync_atlas.py` | 工具实现或入口 | 按任务维护 |
| `scripts/tests/fixtures/architecture-example.json` | 本能力的测试/夹具 | 按任务维护 |
| `scripts/tests/helpers/architecture_viewer.cjs` | 本能力的测试/夹具 | 按任务维护 |
| `scripts/tests/test_atlas_layout.py` | 本能力的测试/夹具 | 按任务维护 |
| `scripts/tests/test_query_atlas.py` | 本能力的测试/夹具 | 按任务维护 |
| `scripts/tests/test_render_architecture.py` | 本能力的测试/夹具 | 按任务维护 |
| `scripts/tests/test_role_atlas.py` | 本能力的测试/夹具 | 按任务维护 |
| `scripts/tests/test_sync_atlas.py` | 本能力的测试/夹具 | 按任务维护 |

## 云端与同步

| 实际路径 | 用途 | 处理方式 |
| --- | --- | --- |
| `dashboard/.dockerignore` | Dashboard、同步或部署 | 按任务维护 |
| `dashboard/.env.example` | Dashboard、同步或部署 | 按任务维护 |
| `dashboard/Dockerfile` | Dashboard、同步或部署 | 按任务维护 |
| `dashboard/README.md` | Dashboard、同步或部署 | 按任务维护 |
| `dashboard/__init__.py` | Dashboard、同步或部署 | 按任务维护 |
| `dashboard/admin.py` | Dashboard、同步或部署 | 按任务维护 |
| `dashboard/app.js` | Dashboard、同步或部署 | 按任务维护 |
| `dashboard/auth.css` | Dashboard、同步或部署 | 按任务维护 |
| `dashboard/auto_update.sh` | Dashboard、同步或部署 | 按任务维护 |
| `dashboard/channel.js` | Dashboard、同步或部署 | 按任务维护 |
| `dashboard/channel_cli.py` | Dashboard、同步或部署 | 按任务维护 |
| `dashboard/channel_store.py` | Dashboard、同步或部署 | 按任务维护 |
| `dashboard/cloud_store.py` | Dashboard、同步或部署 | 按任务维护 |
| `dashboard/compose.yaml` | Dashboard、同步或部署 | 按任务维护 |
| `dashboard/context_store.py` | Dashboard、同步或部署 | 按任务维护 |
| `dashboard/index.html` | Dashboard、同步或部署 | 按任务维护 |
| `dashboard/install_auto_update.sh` | Dashboard、同步或部署 | 按任务维护 |
| `dashboard/local_config.py` | Dashboard、同步或部署 | 按任务维护 |
| `dashboard/login.html` | Dashboard、同步或部署 | 按任务维护 |
| `dashboard/login.js` | Dashboard、同步或部署 | 按任务维护 |
| `dashboard/manage.css` | Dashboard、同步或部署 | 按任务维护 |
| `dashboard/manage.html` | Dashboard、同步或部署 | 按任务维护 |
| `dashboard/manage.js` | Dashboard、同步或部署 | 按任务维护 |
| `dashboard/paths.py` | Dashboard、同步或部署 | 按任务维护 |
| `dashboard/server.py` | Dashboard、同步或部署 | 按任务维护 |
| `dashboard/style.css` | Dashboard、同步或部署 | 按任务维护 |
| `dashboard/sync.py` | Dashboard、同步或部署 | 按任务维护 |
| `dashboard/sync_runtime.py` | Dashboard、同步或部署 | 按任务维护 |
| `dashboard/versioned_sync.py` | Dashboard、同步或部署 | 按任务维护 |
| `dashboard/write_queue.py` | Dashboard、同步或部署 | 按任务维护 |
| `references/dashboard.md` | 对外提供的技能规则或使用说明 | 按任务维护 |
| `references/project-context.md` | 对外提供的技能规则或使用说明 | 按任务维护 |
| `scripts/check_dashboard_sync.py` | 工具实现或入口 | 按任务维护 |
| `scripts/context_store.py` | 工具实现或入口 | 按任务维护 |
| `scripts/serve_dashboard.py` | 工具实现或入口 | 按任务维护 |
| `scripts/tests/test_auto_update.py` | 本能力的测试/夹具 | 按任务维护 |
| `scripts/tests/test_cloud_dashboard.py` | 本能力的测试/夹具 | 按任务维护 |
| `scripts/tests/test_context_store.py` | 本能力的测试/夹具 | 按任务维护 |
| `scripts/tests/test_dashboard.py` | 本能力的测试/夹具 | 按任务维护 |
| `scripts/tests/test_dashboard_local_config.py` | 本能力的测试/夹具 | 按任务维护 |
| `scripts/tests/test_role_channel.py` | 本能力的测试/夹具 | 按任务维护 |
| `scripts/tests/test_sync_runtime.py` | 本能力的测试/夹具 | 按任务维护 |
| `scripts/tests/test_versioned_sync.py` | 本能力的测试/夹具 | 按任务维护 |

## 测试

| 实际路径 | 用途 | 处理方式 |
| --- | --- | --- |
| `scripts/tests/fixtures/timer-repair.json` | 跨角色回放的检查与修复夹具 | 按任务维护 |
| `scripts/tests/helpers/timer_regression.cjs` | 跨角色回放的检查与修复夹具 | 按任务维护 |
| `scripts/validate_task_flow.py` | 工具实现或入口 | 按任务维护 |
| `test/game-engine/doc/design/role-flows.json` | 游戏引擎验证样例（非 ANS 生产代码） | 样例基线保留，默认只读 |
| `test/game-engine/main.ts` | 游戏引擎验证样例（非 ANS 生产代码） | 样例基线保留，默认只读 |
| `test/game-engine/src/interface/engine.ts` | 游戏引擎验证样例（非 ANS 生产代码） | 样例基线保留，默认只读 |
| `test/game-engine/src/models/audio.ts` | 游戏引擎验证样例（非 ANS 生产代码） | 样例基线保留，默认只读 |
| `test/game-engine/src/models/ecs.ts` | 游戏引擎验证样例（非 ANS 生产代码） | 样例基线保留，默认只读 |
| `test/game-engine/src/models/engine.ts` | 游戏引擎验证样例（非 ANS 生产代码） | 样例基线保留，默认只读 |
| `test/game-engine/src/models/input.ts` | 游戏引擎验证样例（非 ANS 生产代码） | 样例基线保留，默认只读 |
| `test/game-engine/src/models/render.ts` | 游戏引擎验证样例（非 ANS 生产代码） | 样例基线保留，默认只读 |
| `test/game-engine/src/models/resource.ts` | 游戏引擎验证样例（非 ANS 生产代码） | 样例基线保留，默认只读 |
| `test/game-engine/src/models/scene.ts` | 游戏引擎验证样例（非 ANS 生产代码） | 样例基线保留，默认只读 |
| `test/game-engine/src/pipelines/gameloop/fixed.timestep.ts` | 游戏引擎验证样例（非 ANS 生产代码） | 样例基线保留，默认只读 |
| `test/game-engine/src/pipelines/gameloop/game.loop.ts` | 游戏引擎验证样例（非 ANS 生产代码） | 样例基线保留，默认只读 |
| `test/game-engine/src/pipelines/render/render.pipeline.ts` | 游戏引擎验证样例（非 ANS 生产代码） | 样例基线保留，默认只读 |
| `test/game-engine/src/providers/abstract/audio.ts` | 游戏引擎验证样例（非 ANS 生产代码） | 样例基线保留，默认只读 |
| `test/game-engine/src/providers/abstract/input.ts` | 游戏引擎验证样例（非 ANS 生产代码） | 样例基线保留，默认只读 |
| `test/game-engine/src/providers/abstract/renderer.ts` | 游戏引擎验证样例（非 ANS 生产代码） | 样例基线保留，默认只读 |
| `test/game-engine/src/providers/abstract/resource.ts` | 游戏引擎验证样例（非 ANS 生产代码） | 样例基线保留，默认只读 |
| `test/game-engine/src/providers/impl/audio/audio.provider.ts` | 游戏引擎验证样例（非 ANS 生产代码） | 样例基线保留，默认只读 |
| `test/game-engine/src/providers/impl/audio/music.ts` | 游戏引擎验证样例（非 ANS 生产代码） | 样例基线保留，默认只读 |
| `test/game-engine/src/providers/impl/audio/sound.ts` | 游戏引擎验证样例（非 ANS 生产代码） | 样例基线保留，默认只读 |
| `test/game-engine/src/providers/impl/input/gamepad.ts` | 游戏引擎验证样例（非 ANS 生产代码） | 样例基线保留，默认只读 |
| `test/game-engine/src/providers/impl/input/input.provider.ts` | 游戏引擎验证样例（非 ANS 生产代码） | 样例基线保留，默认只读 |
| `test/game-engine/src/providers/impl/input/keyboard.ts` | 游戏引擎验证样例（非 ANS 生产代码） | 样例基线保留，默认只读 |
| `test/game-engine/src/providers/impl/input/mouse.ts` | 游戏引擎验证样例（非 ANS 生产代码） | 样例基线保留，默认只读 |
| `test/game-engine/src/providers/impl/render/canvas.renderer.ts` | 游戏引擎验证样例（非 ANS 生产代码） | 样例基线保留，默认只读 |
| `test/game-engine/src/providers/impl/render/sprite.batcher.ts` | 游戏引擎验证样例（非 ANS 生产代码） | 样例基线保留，默认只读 |
| `test/game-engine/src/providers/impl/render/texture.ts` | 游戏引擎验证样例（非 ANS 生产代码） | 样例基线保留，默认只读 |
| `test/game-engine/src/providers/impl/resource/audio.loader.ts` | 游戏引擎验证样例（非 ANS 生产代码） | 样例基线保留，默认只读 |
| `test/game-engine/src/providers/impl/resource/data.loader.ts` | 游戏引擎验证样例（非 ANS 生产代码） | 样例基线保留，默认只读 |
| `test/game-engine/src/providers/impl/resource/image.loader.ts` | 游戏引擎验证样例（非 ANS 生产代码） | 样例基线保留，默认只读 |
| `test/game-engine/src/providers/impl/resource/resource.loader.ts` | 游戏引擎验证样例（非 ANS 生产代码） | 样例基线保留，默认只读 |
| `test/game-engine/src/providers/public/index.ts` | 游戏引擎验证样例（非 ANS 生产代码） | 样例基线保留，默认只读 |
| `test/game-engine/src/providers/public/render.ts` | 游戏引擎验证样例（非 ANS 生产代码） | 样例基线保留，默认只读 |
| `test/game-engine/src/services/abstract/entity.ts` | 游戏引擎验证样例（非 ANS 生产代码） | 样例基线保留，默认只读 |
| `test/game-engine/src/services/abstract/scene.ts` | 游戏引擎验证样例（非 ANS 生产代码） | 样例基线保留，默认只读 |
| `test/game-engine/src/services/abstract/timer.ts` | 游戏引擎验证样例（非 ANS 生产代码） | 样例基线保留，默认只读 |
| `test/game-engine/src/services/impl/entity/component.container.ts` | 游戏引擎验证样例（非 ANS 生产代码） | 样例基线保留，默认只读 |
| `test/game-engine/src/services/impl/entity/entity.service.ts` | 游戏引擎验证样例（非 ANS 生产代码） | 样例基线保留，默认只读 |
| `test/game-engine/src/services/impl/scene/scene.manager.ts` | 游戏引擎验证样例（非 ANS 生产代码） | 样例基线保留，默认只读 |
| `test/game-engine/src/services/impl/scene/scene.ts` | 游戏引擎验证样例（非 ANS 生产代码） | 样例基线保留，默认只读 |
| `test/game-engine/src/services/impl/timer/timer.ts` | 游戏引擎验证样例（非 ANS 生产代码） | 样例基线保留，默认只读 |
| `test/game-engine/src/services/public/index.ts` | 游戏引擎验证样例（非 ANS 生产代码） | 样例基线保留，默认只读 |
| `test/game-engine/test/主循环/fixed.timestep.test.ts` | 游戏引擎验证样例（非 ANS 生产代码） | 样例基线保留，默认只读 |
| `test/game-engine/test/主循环/game.loop.test.ts` | 游戏引擎验证样例（非 ANS 生产代码） | 样例基线保留，默认只读 |
| `test/game-engine/test/主循环/timer.test.ts` | 游戏引擎验证样例（非 ANS 生产代码） | 样例基线保留，默认只读 |
| `test/game-engine/test/场景管理/scene.manager.test.ts` | 游戏引擎验证样例（非 ANS 生产代码） | 样例基线保留，默认只读 |
| `test/game-engine/test/场景管理/scene.test.ts` | 游戏引擎验证样例（非 ANS 生产代码） | 样例基线保留，默认只读 |
| `test/game-engine/test/实体管理/entity.service.test.ts` | 游戏引擎验证样例（非 ANS 生产代码） | 样例基线保留，默认只读 |
| `test/game-engine/test/渲染/render.test.ts` | 游戏引擎验证样例（非 ANS 生产代码） | 样例基线保留，默认只读 |
| `test/game-engine/test/装配/engine.test.ts` | 游戏引擎验证样例（非 ANS 生产代码） | 样例基线保留，默认只读 |
| `test/game-engine/test/音频/audio.test.ts` | 游戏引擎验证样例（非 ANS 生产代码） | 样例基线保留，默认只读 |
| `test/game-engine/角色卡/主循环/boundary.md` | 游戏引擎验证样例（非 ANS 生产代码） | 样例基线保留，默认只读 |
| `test/game-engine/角色卡/主循环/docs/api-spec.md` | 游戏引擎验证样例（非 ANS 生产代码） | 样例基线保留，默认只读 |
| `test/game-engine/角色卡/主循环/docs/changelog.md` | 游戏引擎验证样例（非 ANS 生产代码） | 样例基线保留，默认只读 |
| `test/game-engine/角色卡/主循环/docs/functional-description.md` | 游戏引擎验证样例（非 ANS 生产代码） | 样例基线保留，默认只读 |
| `test/game-engine/角色卡/主循环/role-card.md` | 游戏引擎验证样例（非 ANS 生产代码） | 样例基线保留，默认只读 |
| `test/game-engine/角色卡/场景管理/api-spec.md` | 游戏引擎验证样例（非 ANS 生产代码） | 样例基线保留，默认只读 |
| `test/game-engine/角色卡/场景管理/boundary.md` | 游戏引擎验证样例（非 ANS 生产代码） | 样例基线保留，默认只读 |
| `test/game-engine/角色卡/场景管理/changelog.md` | 游戏引擎验证样例（非 ANS 生产代码） | 样例基线保留，默认只读 |
| `test/game-engine/角色卡/场景管理/docs/design/scene-management.md` | 游戏引擎验证样例（非 ANS 生产代码） | 样例基线保留，默认只读 |
| `test/game-engine/角色卡/场景管理/functional-description.md` | 游戏引擎验证样例（非 ANS 生产代码） | 样例基线保留，默认只读 |
| `test/game-engine/角色卡/场景管理/role-card.md` | 游戏引擎验证样例（非 ANS 生产代码） | 样例基线保留，默认只读 |
| `test/game-engine/角色卡/实体管理/api-spec.md` | 游戏引擎验证样例（非 ANS 生产代码） | 样例基线保留，默认只读 |
| `test/game-engine/角色卡/实体管理/boundary.md` | 游戏引擎验证样例（非 ANS 生产代码） | 样例基线保留，默认只读 |
| `test/game-engine/角色卡/实体管理/changelog.md` | 游戏引擎验证样例（非 ANS 生产代码） | 样例基线保留，默认只读 |
| `test/game-engine/角色卡/实体管理/docs/design/architecture.md` | 游戏引擎验证样例（非 ANS 生产代码） | 样例基线保留，默认只读 |
| `test/game-engine/角色卡/实体管理/functional-description.md` | 游戏引擎验证样例（非 ANS 生产代码） | 样例基线保留，默认只读 |
| `test/game-engine/角色卡/实体管理/role-card.md` | 游戏引擎验证样例（非 ANS 生产代码） | 样例基线保留，默认只读 |
| `test/game-engine/角色卡/渲染/boundary.md` | 游戏引擎验证样例（非 ANS 生产代码） | 样例基线保留，默认只读 |
| `test/game-engine/角色卡/渲染/docs/change/changelog.md` | 游戏引擎验证样例（非 ANS 生产代码） | 样例基线保留，默认只读 |
| `test/game-engine/角色卡/渲染/docs/design/api-spec.md` | 游戏引擎验证样例（非 ANS 生产代码） | 样例基线保留，默认只读 |
| `test/game-engine/角色卡/渲染/docs/feature/functional-description.md` | 游戏引擎验证样例（非 ANS 生产代码） | 样例基线保留，默认只读 |
| `test/game-engine/角色卡/渲染/role-card.md` | 游戏引擎验证样例（非 ANS 生产代码） | 样例基线保留，默认只读 |
| `test/game-engine/角色卡/装配/boundary.md` | 游戏引擎验证样例（非 ANS 生产代码） | 样例基线保留，默认只读 |
| `test/game-engine/角色卡/装配/docs/api-spec.md` | 游戏引擎验证样例（非 ANS 生产代码） | 样例基线保留，默认只读 |
| `test/game-engine/角色卡/装配/docs/changelog.md` | 游戏引擎验证样例（非 ANS 生产代码） | 样例基线保留，默认只读 |
| `test/game-engine/角色卡/装配/docs/functional-description.md` | 游戏引擎验证样例（非 ANS 生产代码） | 样例基线保留，默认只读 |
| `test/game-engine/角色卡/装配/role-card.md` | 游戏引擎验证样例（非 ANS 生产代码） | 样例基线保留，默认只读 |
| `test/game-engine/角色卡/资源加载/api-spec.md` | 游戏引擎验证样例（非 ANS 生产代码） | 样例基线保留，默认只读 |
| `test/game-engine/角色卡/资源加载/boundary.md` | 游戏引擎验证样例（非 ANS 生产代码） | 样例基线保留，默认只读 |
| `test/game-engine/角色卡/资源加载/changelog.md` | 游戏引擎验证样例（非 ANS 生产代码） | 样例基线保留，默认只读 |
| `test/game-engine/角色卡/资源加载/functional-description.md` | 游戏引擎验证样例（非 ANS 生产代码） | 样例基线保留，默认只读 |
| `test/game-engine/角色卡/资源加载/role-card.md` | 游戏引擎验证样例（非 ANS 生产代码） | 样例基线保留，默认只读 |
| `test/game-engine/角色卡/输入/api-spec.md` | 游戏引擎验证样例（非 ANS 生产代码） | 样例基线保留，默认只读 |
| `test/game-engine/角色卡/输入/boundary.md` | 游戏引擎验证样例（非 ANS 生产代码） | 样例基线保留，默认只读 |
| `test/game-engine/角色卡/输入/changelog.md` | 游戏引擎验证样例（非 ANS 生产代码） | 样例基线保留，默认只读 |
| `test/game-engine/角色卡/输入/docs/change/model-enhancement.md` | 游戏引擎验证样例（非 ANS 生产代码） | 样例基线保留，默认只读 |
| `test/game-engine/角色卡/输入/docs/design/input-architecture.md` | 游戏引擎验证样例（非 ANS 生产代码） | 样例基线保留，默认只读 |
| `test/game-engine/角色卡/输入/functional-description.md` | 游戏引擎验证样例（非 ANS 生产代码） | 样例基线保留，默认只读 |
| `test/game-engine/角色卡/输入/role-card.md` | 游戏引擎验证样例（非 ANS 生产代码） | 样例基线保留，默认只读 |
| `test/game-engine/角色卡/音频/boundary.md` | 游戏引擎验证样例（非 ANS 生产代码） | 样例基线保留，默认只读 |
| `test/game-engine/角色卡/音频/docs/api-spec.md` | 游戏引擎验证样例（非 ANS 生产代码） | 样例基线保留，默认只读 |
| `test/game-engine/角色卡/音频/docs/changelog.md` | 游戏引擎验证样例（非 ANS 生产代码） | 样例基线保留，默认只读 |
| `test/game-engine/角色卡/音频/docs/functional-description.md` | 游戏引擎验证样例（非 ANS 生产代码） | 样例基线保留，默认只读 |
| `test/game-engine/角色卡/音频/role-card.md` | 游戏引擎验证样例（非 ANS 生产代码） | 样例基线保留，默认只读 |
