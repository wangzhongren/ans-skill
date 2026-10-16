---
id: boundary-yaml-validation
type: change
title: 独立验证边界 Markdown 与同名 YAML
created: "2026-10-16"
updated: "2026-10-16"
timezone: Asia/Shanghai
status: verified
related: [boundary-yaml-design, boundary-yaml-change, boundary-yaml-feature]
events:
  - date: "2026-10-16"
    kind: verified
    summary: 独立解析并核对五组边界副本及失配检测情形
---

# 独立验证边界 Markdown 与同名 YAML

本轮为三份实际角色边界、本地治理覆盖和内置 Governance 参考检查了同名 YAML 副本。五组均能按 Markdown Section 1 保留原条目与表外限制；内存中的越界或失配副本均被检查器拒绝，正确同步的修改通过。

## 输入与候选

- 基线为 `main` Git `9cbd26be36ec0b1cb61c980601b01516c886a86e`。初始十份 Governance 准备变更和项目管理方案作为已授权、受保护输入。项目管理工程法案 DOC-01 要求沿用现有 `docs/` 功能与历史结构；TASK-01 涉及的工具和任务记录在本轮没有改动。
- 规范候选包括 11 个固定路径：`SKILL.md`、`SKILL.zh.md`、`README.md`、`references/module-boundary.md`、`references/role-card.md`、`references/bootstrap-workflow.md`、`references/built-in-boundary.md`、`references/built-in-boundary.yaml`、`角色卡/技能规范/feature-map.md`、`角色卡/技能规范/docs/feature/boundary-yaml.md`、`角色卡/技能规范/docs/change/2026-10-16_change_boundary-yaml.md`。按 UTF-8 相对路径、NUL、文件原始字节、NUL 的固定顺序聚合，SHA-256 为 `b4675cdb74798ffae198c598ccf744e2f5d0704bb56947ffc9041469a15504e5`。规范 owner 随后只更新 feature-map 行、feature/change 的状态与验证事件及结果链接；项目管理只更新本轮方案状态、事件和结果。短复核确认收尾事实与验证证据一致，规则内容未变；以上哈希是最终 11 路径候选值。
- 四份 Governance 产出的实际角色/本地覆盖 YAML，按 `角色卡/项目管理/boundary.yaml`、`角色卡/技能规范/boundary.yaml`、`角色卡/测试/boundary.yaml`、`角色卡/governance-boundary.yaml` 的固定顺序聚合，SHA-256 为 `7d92188248da2da2947f5fc916278f26fb49a52f69dba271a1bf83cf71ecb032`。
- 独立检查输入：三个实际[角色边界](../../../项目管理/boundary.md)、[本地治理覆盖](../../../governance-boundary.md)、[内置边界参考](../../../../references/built-in-boundary.md)及五份对应 YAML。技能仓库中另有八份旧 `test/game-engine` 边界，本轮按方案未批量迁移；最终集中规则明确，既有边界在下次获准 Governance 维护时补副本。

## 实际解析与逐项比对

执行环境为系统 Ruby `2.6.10p210`。运行一次性只读 Ruby heredoc 检查器，使用 `YAML.safe_load` 实际解析五份 YAML；检查器按每个源 MD 的 Section 1 提取表格行，去掉条目展示用反引号，并按原顺序提取权限说明和列表文字，再与 YAML 的 `source`、`section1.entries`、`section1.notes` 逐项比较。检查代码只在 shell 输入中运行，没有保存为产品或测试源码。

| 边界对 | 预期条目 / notes | 实际结果 |
| --- | ---: | --- |
| [项目管理](../../../项目管理/boundary.md) / [YAML](../../../项目管理/boundary.yaml) | 10 / 1 | 解析成功，来源文件名、所有字段、条目次序与完整 note 原文一致 |
| [技能规范](../../../技能规范/boundary.md) / [YAML](../../../技能规范/boundary.yaml) | 32 / 1 | 解析成功，来源文件名、所有字段、条目次序与完整 note 原文一致 |
| [测试](../../../测试/boundary.md) / [YAML](../../../测试/boundary.yaml) | 7 / 1 | 解析成功，来源文件名、所有字段、条目次序与完整 note 原文一致 |
| [本地 Governance 覆盖](../../../governance-boundary.md) / [YAML](../../../governance-boundary.yaml) | 14 / 3 | 解析成功；保留覆盖范围、候选不自动激活、默认只读的三项完整说明及原顺序 |
| [内置 Governance 参考](../../../../references/built-in-boundary.md) / [YAML](../../../../references/built-in-boundary.yaml) | 5 / 9 | 解析成功；保留单文件、四个条件目录类型和九项职责／限制说明。条件条目仍保留源类型，表外条件全文位于 `notes` |

五组共 68 个条目和 15 项 notes 均通过。逐项比较确认 `source` 是相邻 Markdown basename；`type`、`path`、`purpose` 与 Markdown 同序且只移除了反引号，替代路径、占位路径、待新增单文件类型和真实条件说明未拆分、规范化或扩大范围。`notes` 的原句、顺序、默认只读声明、表外条件、Governance 职责及本地覆盖优先级一致。

## 失配检测与同步更新正例

在 Ruby 内存中复制已解析的数据，使用同一比较器实际执行以下十种注入。结果均与预期一致：

| 注入 | 预期 | 实际 |
| --- | --- | --- |
| 删去一个 Section 1 条目 | 拒绝 | 拒绝，条目数量/序列不一致 |
| 只改 YAML 的一项 `purpose`，MD 保持原值 | 拒绝 | 拒绝，源条目内容不一致 |
| 只改 MD 的一项 `purpose`，保留原 YAML | 拒绝 | 拒绝，源条目内容不一致；此场景另用 Ruby 内存检查器实际执行 |
| 将单文件 `type` 改成目录 | 拒绝 | 拒绝，源条目内容不一致 |
| 加入 Markdown 未列出的额外目录授权 | 拒绝 | 拒绝，出现额外 YAML 条目 |
| 增加额外的顶层 `writeFiles` 授权字段 | 拒绝 | 拒绝，顶层结构不符合 schema |
| 将内置边界的 `Conditional directory` 改为普通目录 | 拒绝 | 拒绝，条件类型不一致 |
| 删掉表外“仅角色建立/重构任务适用”的条件 note | 拒绝 | 拒绝，notes 不一致 |
| 添加源文件没有的 `condition` | 拒绝 | 拒绝，条件没有源文件依据 |
| 调整 notes 次序 | 拒绝 | 拒绝，notes 顺序与源文件不一致 |

随后在内存中同步修改一份 Markdown 的 `purpose` 和对应 YAML 字段，Ruby 检查器先确认“仅改 MD、YAML 过期”时拒绝，再确认同步更新 `section1.entries` 后通过，验证检查不会把正确同步的源变更永久判错。以上是本测试角色自行写的一次性文档一致性比较器与失配模拟，不是 ANS 新增的 CLI、YAML 权限解析器或文件系统拦截器。

## 入口、格式与工具范围

只读审阅英文和中文技能入口、README、角色卡模板、bootstrap 新旧项目路由、内置边界说明及当前 feature/change：均指出 Markdown Section 1 是唯一授权源，sidecar 使用相邻同 basename；入口和模板链接存在。功能说明流程覆盖新建/调整边界、同步副本、差异修复、其他 Markdown 不生成副本和原获准任务继续按 Markdown 执行。功能图及历史链接、方案/变更/feature 元数据通过检查。最终文档间的报告链接在本报告创建后复查。

`task_ops.py` SHA-256 仍为 `90c8644f202913144a5f83e01b7276f14f67240f55519b5c6435775cd21f1017`，`coordination_store.py` 仍为 `c7228255969f1c9710cf57abe739d761de91765c4a021ac13543bcc538c63431`；两个文件、执行配置和旧 `test/game-engine` 文件均未在本轮修改。只读源码检查发现任务配置校验仍读取指定角色边界 Markdown 的 Section 1；本轮没有运行 `task_ops` 程序权限测试，也不声称它解析 YAML。

使用 Ruby YAML 而非 Python PyYAML；`python3 -c 'import yaml'` 在当前 Python 3.14.7 环境失败，错误为 `ModuleNotFoundError`，没有安装依赖。此结论只覆盖五组文件结构与文档一致性，不能证明工具执行、角色运行时服从或文件系统授权行为。

## 相关记录

- 设计方案：[边界文档同时交付同名 YAML 副本](../../../项目管理/docs/design/2026-10-16_design_boundary-yaml.md)
- 当前流程：[边界文档的同名 YAML 副本](../../../技能规范/docs/feature/boundary-yaml.md)
- 规范变更：[为边界文档增加同名 YAML 副本规范](../../../技能规范/docs/change/2026-10-16_change_boundary-yaml.md)
