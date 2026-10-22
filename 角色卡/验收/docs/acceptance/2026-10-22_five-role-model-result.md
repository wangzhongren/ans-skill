# 五个内置管理角色候选返工复核：独立验收结果

日期：2026-10-22；作者：源仓库固定独立【验收 / acceptance】上下文。第一轮结论（第 1–8 节）：**返工**；第二轮定向复核结论（第 9 节）：**通过**；第三轮最终完整复核结论（第 10 节）：**返工**；第四轮最终定向复核结论（第 11 节）：**通过**。

计划任务 ID：`five-role-rework-2026-10-22`（调度计划标识，不是 `task_ops` 任务 ID）。本结论依据客户确认的同一版“五个内置管理角色”策划方案、[返工计划](../../../../docs/scheduling/2026-10-22_five-role-rework.md)和实际工作区候选。B1–B5、R1–R3、R5、R6、A1 的计划内修订均已实质关闭；但一致性扫描发现两张现行 worker 角色卡仍把“技术架构”交给项目管理，测试角色卡仍把一般“架构或设计问题”路由给项目管理，违反基线第 5 条“架构设计归策划”和 R6 的产品架构／实现设计区分，故不能判通过。

第一轮结论经协调方转达为返工（B1–B5、R1–R3、R5、R6），当时没有正式验收报告文件；本报告不补造前一轮文件，只记录本轮复核。

## 1. 验收基线与候选范围

- 分支：`feat/five-role-model`；已提交基线：`f76127d`（`f76127dd1043f033f462ce5874991a8530e004d7`）。
- 受验对象：当前工作区整体候选，不是 HEAD。写入本报告前 `git status --porcelain` 为 66 个已修改跟踪文件加 2 个未跟踪文件（返工计划、技能规范变更记录），共 68 个；本报告是 A1 授权的第 3 个未跟踪文件。计划第 1.2 节的 54 文件是返工前快照，返工新增的文件已逐项核对落在各角色 Section 1。
- 候选状态快照（写入本报告前）：`git status --porcelain | sort` 的 SHA-256 为 `859c132d2a3b8deffea8a97ab3e69a91c9bd004a76c948f41e25f40179cc043e`。
- 关键文件 SHA-256：

| 文件 | SHA-256 |
| --- | --- |
| `docs/scheduling/2026-10-22_five-role-rework.md` | `4931d1c5875dc3bfda34f52ca81d4ca0ac3211d59a75e1f9967e4381ff12c121` |
| `角色卡/技能规范/docs/change/2026-10-22_change_five-role-model.md` | `fe8c9b2c43a7df641f1d81c91bad828c3091f23321dfd1a3f64ceec335f8a623` |
| `角色卡/技能规范/docs/feature/role-authority-split.md` | `c143866b6ca688fad1692ab78ee2b66bd6b936c4ee68d5836d2f4595be04ac61` |
| `角色卡/技能规范/boundary.md` | `b06f7ab7821739dbde544af0fe5c95b2b457b6e02793cc7c26d30f1d83724281` |
| `角色卡/技能规范/boundary.yaml` | `03e135d525fea610bbe39319a3272258d4b337d3e2f67c0593687f637ae7db3a` |
| `角色卡/技能规范/changelog.md` | `794fef5146f264b32e0230437b0fe28f80c05b004e92a3b07ea0610eb6654f40` |
| `references/built-in-boundary.md` | `d5306e229d759efc04cbb36a6c93f3f5275fe531cb24c1dbd4bef4baaac55cf7` |
| `references/built-in-boundary.yaml` | `e9975baa5ea06488584b513a2742857d2ba04c6965fe58627154e1e49e156a4e` |
| `references/governance-changelog.md` | `ee850c4bbfa401ff87fb5586ea6a41b34d5c9e93b45661ddab12f969e7183818` |
| `角色卡/项目管理/docs/architecture.md` | `8653cf9c8299aa4833e30008fa0cc4fcd0e77ab57421d1c432ce15b512cf7cfd` |
| `角色卡/项目管理/docs/project-rules.md` | `3ccb7d133fb19a4ac378652fc04945ab8e573d1aa9581faf65fdc132e2ddd487` |
| `角色卡/项目管理/feature-map.md` | `7ea528d7f53d28d5da94dac4a072059ea6dc1da8fbff25fe3ed505eb83c6e279` |
| `角色卡/项目管理/memo.md` | `403d009c40b72eeb51512e4f8ee063e3aa8dc31bda2c3b46a25c40fb234f16e3` |
| `角色卡/策划/feature-map.md` | `a08c65238f8362677059eb86dc45bb2fa1226200db7cbfc3332313bfbddfabe8` |
| `角色卡/策划/memo.md` | `34ee2c249c53555e9952ed4a1be75d11dd99663536ad2bd887d7382850a01e42` |
| `SKILL.md` | `1fbc6605aa0b1ac9b071c10d62c4fd9da259131c77e7d3d9f35557cd7e45d9ab` |
| `SKILL.zh.md` | `8f2f92661f2925ea80ef4ddac33f8717d62558cc437b9f05060a634bf840c489` |
| `README.md` | `443e300a31c6f82d5b1f4ad8266a6f6f315689416f79146526aa71d456c48541` |
| `references/scheduler.md` | `8cec1a4773bedb16458db95d52b5e50e5048c7dd0e7fc9e7c87ef7742a7da41f` |
| `references/communication-role.md` | `ce09cd6b472e63237fe456f8346952dea181bc47ff83eec43f69171092ce61ce` |
| `references/planning-role.md` | `caf5b4f866ddf2a337dc516cc1a52af86dfd9119a9c6d39a146a97dbaafeb2f2` |
| `references/team-formation.md` | `a9dbf75937773ff717ed3a05104ab8abb58bf16dfc154880dab18d2146909e21` |
| `references/acceptance-role.md` | `dfa0b0adf8c6ec0de0a1a8857dba3deae77648635973dae8e0c896d3d9b5d5e3` |
| `references/test-role.md` | `6f4b98f823dc20c523f1b89366ff889dc4047cef03d9ef8bcfe93c2828746b94` |
| `references/project-role.md` | `e4b09962882ea4a31c42d18de59e2b615abd59c9466632d9ac47a058380450b8` |
| `references/project-context.md` | `c4ce138c1de390daf7e6b8a697480c841366282f49eb5a92b33874d0b23f7c35` |
| `references/role-architecture-viewer.md` | `e5bbc024f94e07ac3b46dccad597924fafd72a55bca76b54ad114f6d3165d54b` |
| `references/dashboard.md` | `92cd2b08481bdd509e6a7489a7be039be964cc34015b97629dc7892611cdb0dc` |

## 2. B1–B5、R1–R3、R5、R6、A1 逐项结论

| 项 | 结论 | 实际依据（以 `git diff HEAD` 和当前文件为准） |
| --- | --- | --- |
| B1 | 关闭 | [项目管理实现层架构](../../../项目管理/docs/architecture.md)第 3–14 行改为按计划建立的项目管理角色维护实现层架构，新增“架构归属”并把产品方案／架构设计归策划；Mermaid 流程改为沟通→策划→统筹判断团队→（必要时招募）→客户确认/授权→派发；原“唯一内置岗位为 ANS 团队组建”“项目管理负责技术架构”已删除。第 24–34 行职责表改为沟通、策划、招募、统筹、验收内置、项目管理按需建立。[项目工程法案](../../../项目管理/docs/project-rules.md)第 1 行升为版本 4（2026-10-22），ROLE-01 第 41 行改为五内置角色模型，第 54 行追加历史条目；未改 Section 1 路径或 CLI 契约。 |
| B2（PM 部分） | 关闭 | [PM 功能导航](../../../项目管理/feature-map.md)第 3 行明确“按需建立、不拥有或改写整体架构”，第 5–9 行导航改为策划角色定义、项目管理角色定义、统筹调度角色定义、条件性实现层架构说明、工程法案；历史方案链接保留。PM memo 第 14 行删除旧路由“策划产品／需求方案 → PM 技术架构／实现设计与技术评审”，改为现行模型。 |
| B2（策划部分） | 关闭 | [策划功能导航](../../../策划/feature-map.md)第 3 行改为策划产出产品方案、架构设计、共有业务契约与完成标准，项目管理仅在团队计划建立时负责实现设计与技术契约；第 5–9 行把 PM `docs/architecture.md` 改为“仅当统筹团队计划建立项目管理角色时适用”，第 11 节历史方案标注“历史，不重写、不复制”。[策划 memo](../../../策划/memo.md)第 8、15、17 行同步；历史方案摘要保留。 |
| B3 | 关闭 | [角色权责拆分功能说明](../../../技能规范/docs/feature/role-authority-split.md)标题、开篇、交接表、Mermaid 流程图、文档权限段和验证历史均已改为现行流程；第 95–99 行保留历史并追加 2026-10-22 事件；不再写“项目管理默认做技术架构”或“团队组建先建全部角色”。 |
| B4（治理记录） | 关闭 | [治理变更记录](../../../../references/governance-changelog.md)第 15 行 B4 条如实记录 `references/architecture.md` 正文已在同一候选修改，并给出 `git diff HEAD -- references/architecture.md` 的行级依据；[技能规范 changelog](../../../技能规范/changelog.md)第 45–54 行追加更正条目，明确原“只调整边界归属、不修改正文”不再成立；第 43 行是同日更早的历史条目，按“changelog 追加、不重写历史”保留，但其后同文件条目和 [boundary 说明](../../../技能规范/boundary.md)第 63 行已明确取代，不构成现行错误声明。boundary MD/YAML 同步。 |
| B4（实际变更记录） | 关闭 | [技能规范变更记录](../../../技能规范/docs/change/2026-10-22_change_five-role-model.md)第 22–29 行列出技能规范 Section 1 内的全部入口、宣传页和 21 份共享参考；与实际修改的 26 个技能规范所属文件逐一对齐（3 入口 + 2 宣传页 + 21 参考），并明确排除 7 份角色定义类参考。第 31–74 行逐文件摘要与 `git diff HEAD` 抽查一致（architecture、role-card、bootstrap-workflow、module-boundary、documentation、proposal-review、workflow、feature-point、project-rules、role-memo、meeting、task-operations、shared-directories、api-spec、testing、evidence、coordination、group-leadership、三份 legacy 参考均能对上）。第 105–111 行不预写验收结论。 |
| B5 | 关闭 | [内置边界](../../../../references/built-in-boundary.md)第 7–20 行 Section 1 不再有 `references/` 目录授权；改为五个内置角色定义、三个 worker 角色定义、本边界对、治理变更记录的精确单文件；`角色卡/<role>/` 仅限 role-card/boundary/YAML/changelog 四类治理资料，并限定“统筹已授权团队计划列明该角色”时才建/改；`SKILL.md`/`SKILL.zh.md`、`docs/` 脚手架、装配入口均为条件项；明确不授权共享格式/流程/宣传页、业务代码、执行配置、任务状态、活动调度记录、他人工作文档和五个内置默认目录。YAML 第 1–40 行与 MD 逐项对应。 |
| R1 | 关闭 | [技能规范 boundary](../../../技能规范/boundary.md)第 30–32 行把 `references/project-context.md`、`role-architecture-viewer.md`、`dashboard.md` 作为 legacy 单文件加入，注明“仅客户明确要求时使用；默认阅读路径以策划方案为准”；YAML 第 74–82 行同步；三份正文仍保留 legacy 定位（分别见其第 3 行、第 3 行、第 3 行），默认阅读路径改为策划 `docs/planning/`，项目管理 `docs/architecture.md` 仅在该角色建立后补充。 |
| R2 | 关闭 | [技能规范 boundary](../../../技能规范/boundary.md)第 28–29 行不再有“待新增单文件／接入后方可创建”，改为“文件已实际存在”并写明用途；YAML 第 69–73 行同步；[changelog](../../../技能规范/changelog.md)第 52 行和[治理变更记录](../../../../references/governance-changelog.md)第 18 行记录更正，并如实说明此前创建授权依据未能核实、不补造历史授权。 |
| R3 | 关闭 | [README](../../../../README.md)第 262 行和[文档规则](../../../../references/documentation.md)第 54、72 行均明确“顶层历史 `doc/`（单数）保留、不迁移、不改名；五个内置角色默认写 `docs/communication/`、`docs/planning/`、`docs/scheduling/`、`docs/acceptance/`，招募写 `角色卡/` 治理资料；两者并存，不产生第二套当前文档”。 |
| R5 | 关闭 | 统一顺序“策划完成（产品方案、架构设计、共有契约与完成标准）→ 统筹判断团队（不变/新招/拆分）→ 必要时招募按计划建卡与边界 → 客户确认/实施授权（经沟通）→ 统筹派发”已落在 [SKILL.md](../../../../SKILL.md)第 18 行、[SKILL.zh.md](../../../../SKILL.zh.md)第 10、21 行、[README](../../../../README.md)第 53、89、97 行、[workflow](../../../../references/workflow.md)第 79 行、[documentation](../../../../references/documentation.md)第 26 行、[scheduler](../../../../references/scheduler.md)第 3、7、13–15、64 行、[communication-role](../../../../references/communication-role.md)第 10、27、36–38 行、[planning-role](../../../../references/planning-role.md)第 66 行、[team-formation](../../../../references/team-formation.md)第 18 行、[acceptance-role](../../../../references/acceptance-role.md)第 20 行、[project-role](../../../../references/project-role.md)第 3 行、[test-role](../../../../references/test-role.md)第 41 行、[统筹角色卡](../../../统筹调度/role-card.md)第 6 行。同版同范围授权复用规则保留。 |
| R6 | 计划内关闭 | [acceptance-role](../../../../references/acceptance-role.md)第 20 行和 [test-role](../../../../references/test-role.md)第 41 行均已区分“产品方案／架构设计问题交策划；实现设计／技术契约问题交已按团队计划建立的项目管理角色；未建立时不虚构，由统筹安排”。但 [测试角色卡](../../../测试/role-card.md)第 31 行仍是旧的一般路由（见阻塞项 K3），属于同一区分的现行文档缺口。 |
| A1 | 关闭 | [验收 boundary](../../boundary.md)第 13 行和 [boundary.yaml](../../boundary.yaml)第 24 行已加入本报告精确路径；[验收 changelog](../../changelog.md)记录治理变更。报告由本验收上下文写盘，招募未代写、未改结论。 |

## 3. 硬约束检查

| 约束 | 结论 | 依据 |
| --- | --- | --- |
| 招募不得私自招人 | 满足 | [内置边界](../../../../references/built-in-boundary.md)第 24–26 行、[团队组建定义](../../../../references/team-formation.md)第 11–14 行、[调度定义](../../../../references/scheduler.md)第 13–15 行、[统筹角色卡](../../../统筹调度/role-card.md)第 6 行均明确：统筹写入 `docs/scheduling/` 的团队计划是唯一依据；无计划时招募停下报告，不提议、不决定、不先建卡。 |
| 验收不得自造标准 | 满足 | [独立验收定义](../../../../references/acceptance-role.md)第 7、20 行、[验收角色卡](../../../验收/role-card.md)第 5、20 行、[验收边界](../../boundary.md)第 15 行均要求按同一版已确认策划方案写标准；缺标准退回策划；不得加需求、放宽或加严。 |
| 角色不写自己的角色定义 | 满足 | 五张内置角色卡均在开头或原则中写明角色卡／边界由 ANS 团队组建（招募）维护（[技能规范](../../../技能规范/role-card.md)、[策划](../../../策划/role-card.md)、[统筹](../../../统筹调度/role-card.md)、[项目管理](../../../项目管理/role-card.md)、[验收](../../../验收/role-card.md)）；[治理边界](../../../governance-boundary.md)第 65 行统一收归招募。 |
| 五个内置角色默认窄写权 | 满足 | [SKILL.md](../../../../SKILL.md)第 103–105 行、[SKILL.zh.md](../../../../SKILL.zh.md)第 23 行、[README](../../../../README.md)第 78–82 行、五份角色定义均写明：沟通 `docs/communication/`、策划 `docs/planning/`、调度 `docs/scheduling/`、验收 `docs/acceptance/`、招募 `角色卡/` 治理资料；不自动获得业务代码写权。 |
| 架构设计归策划 | **不满足（阻塞）** | 共享文档、角色定义和五张内置角色卡已满足；但 [任务工具角色卡](../../../任务工具/role-card.md)第 22 行和[测试角色卡](../../../测试/role-card.md)第 24 行仍写“项目管理的技术架构/实现设计”，[测试角色卡](../../../测试/role-card.md)第 31 行仍把一般“架构或设计问题”交项目管理评估。这直接违反基线第 5 条和 R6 的区分，见 K1–K3。 |
| PM 按需建立 | 满足 | [项目管理定义](../../../../references/project-role.md)第 3 行、[PM 角色卡](../../../项目管理/role-card.md)第 5 行、[PM 边界](../../../项目管理/boundary.md)第 21 行、[PM 功能导航](../../../项目管理/feature-map.md)第 3 行、[SKILL.md](../../../../SKILL.md)第 109 行、[README](../../../../README.md)第 82 行均写明项目管理不是默认角色。 |

## 4. 边界覆盖与 YAML 一致性

- 对 68 个受验文件（66 个已修改跟踪文件 + 返工计划 + 技能规范变更记录）逐个匹配所有 Section 1：**68/68 恰好一个所有者，无重复、无未归属**。本报告路径只出现在[验收 boundary](../../boundary.md)第 13 行。
- 对 9 对边界（技能规范、策划、统筹调度、项目管理、验收、任务工具、测试、治理覆盖、内置边界）比较 MD 表格与同名 YAML 的条目集合、类型和路径：**全部一致**；内置边界的路径写法差异仅为 MD 的多反引号显示，语义相同。
- 未归属 `references` 文件：任务简报所述 11 个仍无 Section 1 所有者，即 `code-atlas.md`、`documentation-change.md`、`documentation-design.md`、`documentation-feature.md`、`documentation-fix.md`、`interface.md`、`model.md`、`pipeline.md`、`provider.md`、`role-atlas.md`、`service.md`。另外扫描到第 12 个无所有者文件 `references/functional-description.md`，见残留项 N1。

## 5. 一致性扫描：阻塞项与残留项

### 5.1 阻塞项（必须返工）

| 编号 | 文件与行 | 现行旧说法 | 应改为什么 |
| --- | --- | --- | --- |
| K1 | [任务工具角色卡](../../../任务工具/role-card.md)第 22 行 | “策划确认的用户目标与产品流程方案、项目管理的技术架构/实现设计及验收标准” | “策划确认的产品方案、架构设计与共有业务契约；如按团队计划建立项目管理角色，其实现设计、技术契约和技术评审；验收标准来自策划方案”。 |
| K2 | [测试角色卡](../../../测试/role-card.md)第 24 行 | “策划确认的用户目标与产品流程方案，以及项目管理的技术架构/实现设计” | 同 K1：产品方案／架构设计归策划；实现设计／技术契约仅在项目管理角色按计划建立时由其负责。 |
| K3 | [测试角色卡](../../../测试/role-card.md)第 31 行 | “如涉及架构或设计问题，统筹再交项目管理评估” | 按 R6 区分：“产品方案／架构设计问题交策划；实现设计／技术契约问题交已按团队计划建立的项目管理角色；未建立时不虚构该角色，由统筹安排”。 |

这 3 处不是新需求：它们直接对应客户确认的基线第 5 条（架构设计归策划）和 R6（区分产品架构与实现设计）。两张角色卡已在[治理边界](../../../governance-boundary.md)第 31–34、19–22 行的 Section 1 内，招募按统筹团队计划修正即可，无需新增路径或权限；角色卡仍由招募维护，不由任务工具／测试角色自写。

### 5.2 残留项（本轮不阻塞，但应记录）

| 编号 | 文件与行 | 事实 | 处理建议 |
| --- | --- | --- | --- |
| N1 | [references/functional-description.md](../../../../references/functional-description.md)第 5 行 | “Project management owns overall architecture and role collaboration in its own docs/architecture.md.” 这是旧模型表述；该文件不在任何 Section 1。 | 由招募在后续治理轮次决定归属（建议归技能规范作为共享格式参考）并改为“策划拥有 `docs/planning/` 的产品方案与架构设计；按团队计划建立的项目管理角色只维护实现层 `docs/architecture.md`”。本轮因无所有者、无授权路径，验收不自行修改。 |
| N2 | [项目管理 memo](../../../项目管理/memo.md)第 7 行 | “负责架构、契约评审……”未限定“实现层架构”，与同文件第 14 行的现行模型表述存在歧义。 | 建议 PM 在自身 memo 内改为“负责实现层架构、技术评审、技术契约……”，避免被读成整体架构设计。 |
| N3 | [治理边界](../../../governance-boundary.md)第 59 行及 [YAML](../../../governance-boundary.yaml)第 135 行 | “策划写用户目标和产品流程方案，项目管理负责技术架构与实现设计……”是上一轮授权沿革的历史说明；同文件第 65 行已按 2026-10-22 治理原则收归角色定义并写明架构设计归策划。 | 作为历史沿革保留；下次修改该文件时可加“（已被 2026-10-22 五内置管理角色模型取代）”以免误读。 |
| N4 | `site/index.html`、`site/en/index.html` | 8 个 `/ans-skill/...` 站点根绝对路径不是仓库相对文件；与 HEAD 版本一致，是 GitHub Pages 部署路由。 | 不视为未解析本地链接。 |

扫描未见其他违规：共享入口、宣传页、21 份技能规范共享参考、8 份角色定义（含 built-in-assembly）、五张内置角色卡、策划／统筹／PM／验收工作文档均已按现行模型更新；技能规范角色卡第 24 行和技能规范功能导航第 8 行的“技术架构／技术设计”是职责分工话题，不是所有权断言；各 memo 中带 2026-10-19 日期的旧路由描述属历史工作线索，不作为现行规则。

## 6. 实际命令与结果

| 检查 | 命令／方法 | 实际结果 |
| --- | --- | --- |
| 程序测试 | `python3 -m unittest discover -s scripts/tests -q` | `Ran 236 tests in 67.324s`，`OK`，退出码 0。原日志 `/tmp/ans-five-role-acceptance-tests.log`，SHA-256 `8f4c8c3c4f3ed4602e271fbcc4cd5eb343f2e122999aadd0844d8b61de5aec3a`。测试通过只说明脚本测试集通过，不代替文档一致性或验收判断。 |
| 空白检查 | `git diff --check HEAD` | 退出码 0，无空白错误。 |
| 本地链接 | 对全部受验 `.md`/`.html` 解析 Markdown 行内链接、HTML `href` 并解析相对路径 | 写本报告前 61 个文件、617 个链接；除本报告（写盘前不存在，A1 已授权）外 0 个未解析仓库相对目标；本报告写盘后另核 89 个本地链接，0 未解析；`site` 的 8 个 `/ans-skill/...` 为部署绝对路由，与 HEAD 相同。 |
| 边界归属 | 解析 9 对 boundary.md Section 1，逐个匹配 68 个受验文件 | 68/68 恰好一个所有者；无重复、无未归属。 |
| MD/YAML 一致 | 比较 9 对边界的条目集合、类型、路径 | 9/9 一致。 |
| 治理记录与 diff | 逐项对照 `git diff HEAD`、治理 changelog、技能规范 changelog、变更记录 | B4、B5、R1、R2、R5、R6、A1 记录均与实际 diff 一致；无“未修改正文”与事实相反。 |

## 7. 结论及理由

**结论：返工。**

理由：

1. 计划内的 B1–B5、R1–R3、R5、R6（references 两文件）、A1 均已实质关闭；程序测试、链接、边界覆盖、MD/YAML 一致性和治理记录核对均通过。返工不是因为这些项目未完成。
2. 客户确认的基线第 5 条“架构设计归策划”和 R6 的“产品架构 vs 实现设计”区分，在两张现行 worker 角色卡中仍未落实：K1、K2 仍把“技术架构”交给项目管理，K3 仍把一般“架构或设计问题”路由给项目管理。角色卡是现行治理文档，且已在招募 Section 1 内，不属于可忽略的历史记录。
3. 这 3 处修正范围小、路径已授权、无需新增角色或权限：由统筹把修正写入团队计划，招募按计划改两张角色卡并在对应 changelog／治理变更记录中留痕，然后重新冻结候选。验收只需复核这 3 处的实际 diff 及未受影响的关键文件哈希，不要求重做本轮全部检查。
4. 残留项 N1–N4 不阻塞本轮，但 N1（未归属 `references/functional-description.md` 的旧模型句）应在后续治理轮次处理；N2 建议顺手澄清；N3 保留为历史沿革；N4 不是文档链接缺陷。

本报告只写本角色获准的路径；未修改程序、测试、其他角色文档、角色卡、边界或任务状态，未 commit、未 push、未安装、未发布。结论只对上述冻结候选和同一版策划方案有效；候选或方案实质变化须重新核对。

## 8. 证据入口

- [返工计划](../../../../docs/scheduling/2026-10-22_five-role-rework.md)（计划任务 ID `five-role-rework-2026-10-22`）
- [技能规范实际变更记录](../../../技能规范/docs/change/2026-10-22_change_five-role-model.md)
- [角色权责拆分当前功能说明](../../../技能规范/docs/feature/role-authority-split.md)
- [治理变更记录](../../../../references/governance-changelog.md)
- [技能规范 changelog](../../../技能规范/changelog.md)、[boundary](../../../技能规范/boundary.md)、[boundary.yaml](../../../技能规范/boundary.yaml)
- [内置边界](../../../../references/built-in-boundary.md)、[内置边界 YAML](../../../../references/built-in-boundary.yaml)
- [PM 实现层架构](../../../项目管理/docs/architecture.md)、[PM 工程法案](../../../项目管理/docs/project-rules.md)、[PM 功能导航](../../../项目管理/feature-map.md)、[PM memo](../../../项目管理/memo.md)
- [策划功能导航](../../../策划/feature-map.md)、[策划 memo](../../../策划/memo.md)
- [任务工具角色卡](../../../任务工具/role-card.md)、[测试角色卡](../../../测试/role-card.md)
- [测试日志](/tmp/ans-five-role-acceptance-tests.log)

## 9. 第二轮定向复核（2026-10-22）

本节为第二轮定向复核，只覆盖 K1–K3 三处阻塞项、N1/N2 两个非阻塞项、定向测试和本次修复范围；不重做第一轮全部检查。第 1–8 节保持第一轮记录原样，仅标题行补注两轮结论。

### 9.1 复核范围与候选快照

- 验收基线不变：客户确认的五内置管理角色方案——策划负责产品方案、架构设计与可验收标准；统筹判断团队，必要时按计划招募，取得客户确认/授权后派发；招募只按统筹计划写卡；验收按同一版策划方案判断；项目管理按需建立，只负责实现设计、技术契约和实现层架构，不拥有整体架构。K1–K3 直接对应基线第 5 条和第一轮 R6 的区分，不是新需求。
- 分支 `feat/five-role-model`，已提交基线 `f76127d`；复核对象为当前工作区候选，不 commit。
- 写本节前 `git status --porcelain -uall | sort` 为 73 条：70 个已修改跟踪文件 + 3 个未跟踪文件（返工计划、技能规范变更记录、本报告）。候选快照（文件名与状态码，排序后）SHA-256：`acbe1c7998c066629f413e92c757d16002de34e862701c24ab6cc213050a5731`。计划第 9.2 节的 69 条是第二轮修正前的计数；本轮修正使两张角色卡和两份角色 changelog 由未修改转入已修改，恰好 +4。
- 本轮三处修正文件及留痕文件 SHA-256：

| 文件 | SHA-256 |
| --- | --- |
| `角色卡/任务工具/role-card.md` | `4d68d62862ac26afaf5ae6177e59a28515976620e1db7f416dc6b38928569627` |
| `角色卡/测试/role-card.md` | `fc1226529bc919007518cd273ae8a7e1dd8c6e87b77ece480f5fe6d1a1fe2dac` |
| `角色卡/项目管理/memo.md` | `3e9575dbee2f29db3f7c3d1226258f1c74f4acff30534a6c34f77f4a571f2006` |
| `角色卡/任务工具/changelog.md` | `137ae8d2692c92102ccdf24807ad2aa5dbdb03bcde452aadde0f743696522cf2` |
| `角色卡/测试/changelog.md` | `8d2379c2fe4b30d49e7cc87c762edb338525dffcb8ae2e9b177ceb277f3c90de` |
| `references/governance-changelog.md` | `1374acfe108c134f2178b3378f856114578423bc9b23f414b116d22772678216` |
| `docs/scheduling/2026-10-22_five-role-rework.md`（计划自身） | `a46acfd9bfd485bc850fa6f7e4541f4946a6dd108ac01f677adfb42bdba385e3` |

### 9.2 逐项结果

| 项 | 结论 | 依据 |
| --- | --- | --- |
| K1 | 关闭 | [任务工具角色卡](../../../任务工具/role-card.md)第 22 行改为“策划负责产品方案和架构设计；项目管理仅在统筹团队计划建立时负责实现设计和技术契约，不拥有整体架构设计。必读策划确认的产品方案、架构设计与共有业务契约及验收标准，以及项目管理角色（如已建立）的实现设计、技术契约与技术评审……”。相邻第 20 行同步改为“项目管理（如按统筹团队计划建立）的相关实现架构说明与项目法案”。定向检索确认两卡已无“项目管理的技术架构/实现设计”或等价所有权断言。 |
| K2 | 关闭 | [测试角色卡](../../../测试/role-card.md)第 24 行改为“策划负责产品方案和架构设计；项目管理仅在统筹团队计划建立时负责实现设计和技术契约，不拥有整体架构设计。必读……以及项目管理角色（如已建立）的实现设计和技术契约……”，与 K1 同一区分。 |
| K3 | 关闭 | [测试角色卡](../../../测试/role-card.md)第 31 行改为“产品方案/架构设计问题交策划；实现设计/技术契约问题交已按统筹团队计划建立的项目管理（技术架构）角色，未建立该项目管理角色时不虚构，由统筹安排”，与 [test-role](../../../../references/test-role.md)第 41 行、[acceptance-role](../../../../references/acceptance-role.md)第 20 行的 R6 现行表述一致；“（技术架构）”是同一现行标签，不是所有权断言。 |
| N2 | 关闭 | [PM memo](../../../项目管理/memo.md)第 7 行改为“负责实现层架构、契约评审、项目法案及已获准的共享代码工作”；第 14 行保留第一轮 B2 已记录的现行模型表述“项目管理仅在统筹团队计划建立时负责实现设计、技术契约和实现层架构，不拥有整体架构设计”；日期行同步为 2026-10-22。 |
| N1 | 仍为残留，不阻塞（按计划本轮不修） | [references/functional-description.md](../../../../references/functional-description.md)第 5 行原文未变：“Project management owns overall architecture and role collaboration in its own docs/architecture.md.”。对全部 `boundary.md`／`boundary.yaml`（含 `references/built-in-boundary.md`／`.yaml`）定向检索该路径为 0 命中，确认仍无 Section 1 所有者；按计划第 9.6 节留待后续治理轮次确定归属后处理，不作为本轮阻塞条件。 |
| N5（本轮新记） | 非阻塞残留 | [任务工具角色卡](../../../任务工具/role-card.md)第 30 行“若实现发现需要扩大范围或改变契约，先更新本角色获准的设计/变更文件并交项目管理评审和用户确认……”未写“如已按团队计划建立”。它只描述技术契约变更的评审去向，不包含架构或整体评审权的所有权断言；[project-role](../../../../references/project-role.md)第 3、10 行规定项目管理建立后负责实现设计、技术评审与技术契约，[role-card](../../../../references/role-card.md)第 98 行对同类交接触发也写“已建立的项目管理角色”。但在未建立项目管理的项目里该句缺少接收方，建议后续条件化为“交已按团队计划建立的项目管理角色评审；未建立时由统筹安排”。本轮不据此判返工，不要求回招募。 |

### 9.3 定向测试

| 检查 | 命令 | 实际结果 |
| --- | --- | --- |
| 程序测试 | `python3 -m unittest discover -s scripts/tests -q` | `Ran 236 tests in 73.985s`，`OK`，退出码 0。日志 `/tmp/ans-five-role-acceptance-tests-round2.log`，SHA-256 `e495334b6f328a8141d06e81d3d95a8c965d869f667b911a1f8a7bc27b3087e1`。测试通过只说明脚本测试集通过，不代替文档一致性或验收判断。 |
| 空白检查 | `git diff --check HEAD` | 退出码 0，无空白错误。 |

### 9.4 定向修复范围核对

- 以第一轮报告写盘时间（2026-10-22 14:35:51）为界，之后被修改的跟踪文件恰好 6 个：`角色卡/任务工具/role-card.md`、`角色卡/测试/role-card.md`、`角色卡/项目管理/memo.md`、`角色卡/任务工具/changelog.md`、`角色卡/测试/changelog.md`、`references/governance-changelog.md`；另有统筹追加第 9 节的返工计划本身（计划不是 K1–K3 的修正对象）。`git diff HEAD` 显示两张角色卡只有 K1–K3 及相邻第 20 行修正，两份角色 changelog 只有对应 K1/K2/K3 条目；PM memo 的第二轮新增变化为第 7 行实现层限定和日期行。
- `git status -uall` 的 3 个未跟踪文件均为第一轮已知：返工计划、技能规范变更记录、本报告；没有新增未授权文件，也没有新增路径、角色、`roleId`、组别或默认写权。
- 留痕：任务工具 changelog 第 11 行记录 K1；测试 changelog 第 26 行记录 K2/K3；[治理变更记录](../../../../references/governance-changelog.md)第 25 行记录第二轮整体，并注明 N2 属项目管理自身修正、N1 仍为无所有者残留。PM memo 在自身 Section 1 内，根 changelog 由招募维护，PM 未改写根 changelog。

### 9.5 结论

**结论：通过（第二轮定向复核）。**

理由：

1. K1、K2、K3 均已按基线第 5 条和 R6 的区分关闭：两张角色卡不再把“项目管理的技术架构/实现设计”作为默认；第 31 行按“产品方案/架构设计问题交策划；实现设计/技术契约问题交已按统筹团队计划建立的项目管理；未建立时不虚构，由统筹安排”分流，且与现行角色定义一致。
2. N2 已由项目管理在自身 memo 内限定为“实现层架构”，未扩大职责；N1 仍是无 Section 1 所有者的旧模型句残留，按计划本轮不修、不阻塞；第 30 行只涉及技术契约变更的评审去向，不构成架构所有权断言，记为非阻塞残留 N5，建议后续条件化。
3. 定向测试 236 项全部通过（退出码 0），`git diff --check` 无空白错误；定向修复范围、留痕与计划第 9 节一致，没有新增未授权文件或路径。

覆盖限制：本结论只对当前冻结候选和同一版策划方案有效，且只覆盖上述定向项；不重做第一轮的全库链接、全边界覆盖、MD/YAML 全量比对等检查，第一轮已关闭项沿用第一轮证据（第 1–8 节）。候选或方案实质变化须重新核对。本报告只写验收获准路径；未修改程序、其他角色文档、角色卡、边界或任务状态，未 commit、未 push、未安装、未发布。

## 10. 最终复核（2026-10-22，第三轮全量复核）

### 10.1 验收基线与候选范围

本轮按客户确认的最终方案逐项复核 10 条基线：五个内置管理角色；默认窄写权与五份 memo；三道客户闸门；五维判断与决策表；能力描述分工；运行架构；权力矩阵；验收表与风险分档；人事改名；角色定义与共享文档归属。

- 分支：`feat/five-role-model`；已提交基线：`f76127d`（`f76127dd1043f033f462ce5874991a8530e004d7`）。
- 受验对象：当前工作区整体候选，不是 HEAD。写本节前 `git status --porcelain -uall` 为 77 条：73 个已修改跟踪文件 + 4 个未跟踪文件（`references/authority-matrix.md`、`角色卡/技能规范/docs/change/2026-10-22_change_five-role-model.md`、`docs/scheduling/2026-10-22_five-role-rework.md`、本报告）。候选快照（文件名与状态码，排序后）SHA-256：`a1c5c7f1ed19316f67b3dbcfc2d9ded24bbd8632a658aef669da805fdb4efcc8`；`git diff HEAD` 的 SHA-256：`1c52f1b456dddb236d3a053c5e8b1fa3a90a0e6d1d765fbd9c94214d7d82d6ee`。
- 写本节前本报告 SHA-256：`825665d24fed1556fe1b581507d74042db390710c189cad8cba2f68d929f2eac`。
- 关键文件 SHA-256：

| 文件 | SHA-256 |
| --- | --- |
| `SKILL.md` | `26c6b75f206349529e7569d575868fcf89e373302292511c89ee92535ebd5be6` |
| `SKILL.zh.md` | `ef8d788c71d361143e9f6c00f0d3a4fd653a25507069d024745c299eacd34483` |
| `README.md` | `80a779e66aa916a41cc3b2ba2ff0968748bac0e7c8ccf4ca3f77a6e719ce3316` |
| `references/scheduler.md` | `45b03b715426ec9f7459b39fae640abe370b8264b968b8033af7a565590147d5` |
| `references/authority-matrix.md` | `a4c2227f13fd9f00a529db5f99166466ff5507f11bc765cbad3e2713fef7cf48` |
| `references/acceptance-role.md` | `a02fa9de51edf23d503974fe527955886561a5e399affaa4323cc2f87aabd4d1` |
| `references/testing.md` | `b9022f21c726f081932ebe052cc3525cfdf27e946198458e477187b573dab8db` |
| `references/team-formation.md` | `ac3614119d72ec53fa7e87db2f55ecc372fc689bdf394f4a5e17939b0c919c17` |
| `references/communication-role.md` | `652acf1652682814383b43e93f90834670adc0b5235bae411732b8203f174811` |
| `references/planning-role.md` | `3aa78105a9cd206de0036ff829f43208720bc0c250d5ddca9374f0b3ce42d96b` |
| `references/built-in-boundary.md` | `566523988038c56eff525eed0d143bfc4e851397d30b3b89624db67dfd66d7b0` |
| `角色卡/governance-boundary.md` | `2009d5ffdfd43b22403365f857d6e48271eee27c65cc62891f15d76bf2c4ea4e` |

### 10.2 逐项 1–10 验收表

| ID | 基线标准（摘要） | 需要的证据 | 实际证据（路径/行号） | 候选版本 | 产出角色 | 结果 | 判断 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 五个内置管理角色在任意项目可用，无需项目角色卡或先招募 | 五份角色定义和入口一致列出五角色、默认窄范围、无需建卡 | `SKILL.md:105-115`；`SKILL.zh.md:16,23,25`；`README.md:85-92,100`；`references/communication-role.md:3`、`planning-role.md:3`、`team-formation.md:5`、`scheduler.md:3`、`acceptance-role.md:3` | 工作区 @ `a1c5c7…` | 技能规范、人事 | 五角色定义齐全，均写明立即可用、默认窄范围、不自动获得业务代码写权 | 通过 |
| 2 | 默认写权窄；五份 memo 路径固定 | 五份参考、`role-memo.md`、`role-card.md`、入口与 README 的路径一致 | `SKILL.md:84,107-113`；`SKILL.zh.md:25,52`；`README.md:258`；`communication-role.md:62`；`planning-role.md:89`；`scheduler.md:82`；`acceptance-role.md:67`；`team-formation.md:94`；`role-memo.md:6`；`role-card.md:23` | 同上 | 技能规范、人事 | 五条默认路径和五份 memo 均写入；项目本地覆盖有说明 | 通过 |
| 3 | 三道客户闸门；沟通唯一客户通道；默认勾选等不算同意；变更重开对应闸门 | `SKILL.md`、`SKILL.zh.md`、`README.md`、`workflow.md`、`bootstrap-workflow.md`、五份参考中的闸门与重开规则 | `SKILL.md:20-24`；`SKILL.zh.md:10`；`README.md:60`；`workflow.md:88`；`bootstrap-workflow.md:3`；`communication-role.md:9-12,38-48`；`planning-role.md:5`；`scheduler.md:3,17-19`；`team-formation.md:3`；`acceptance-role.md:3,11`；`authority-matrix.md:17,24-32`。**冲突**：`SKILL.md:18` 仍写客户请求可经 worker 角色上下文进入，`SKILL.md:24` 却写 Communication 是唯一客户通道 | 同上 | 沟通、策划、统筹、人事、验收 | 闸门机制与重开规则一致；唯一客户通道被 `SKILL.md:18` 例外破坏 | 不通过 |
| 4 | 五维判断（责任独立性、范围归属、契约影响、证据独立性、协调成本）与决策表；结果只能是五种之一；团队计划记录覆盖图、工作量、契约/证据影响、协调成本、选项、理由、边界变更清单、闸门 2 确认 | `scheduler.md` 的唯一定义；其他共享文档只链接；团队计划字段齐全 | `scheduler.md:21-46` 定义五维、决策表、团队计划字段；`README.md:60,88,100,108,119,187`、`SKILL.md:22,74,112,132,135,139,215,243`、`SKILL.zh.md:10,23,40,68`、`workflow.md:88`、`bootstrap-workflow.md:3`、`documentation.md:26` 均链接 `scheduler.md#五维判断与决策表`。**冲突**：`team-formation.md:22-41` 完整复制五维与决策表；`角色卡/统筹调度/role-card.md:27` 又复述五维和一句话规则 | 同上 | 统筹、人事 | 决策表在 `scheduler.md` 定义，但 `team-formation.md` 形成第二处完整定义 | 不通过 |
| 5 | 统筹只定要什么能力、什么边界；人事补能力描述、职责、必读、交接输入输出、执行原则，再落卡/边界/YAML/changelog；人事不得私自招人或扩权 | `scheduler.md`、`team-formation.md`、入口与 README 分工表述一致 | `scheduler.md:48-54`；`team-formation.md:55-63`；`SKILL.md:24,135`；`README.md:85,100`；`authority-matrix.md:19-20,38` | 同上 | 统筹、人事 | 分工、禁止事项和落地顺序均一致 | 通过 |
| 6 | 客户窗口只加载沟通；策划/人事/统筹/验收由沟通启动独立子代理；工作角色只由统筹调度；沟通不得直接派活/授权/启动；统筹不启动内置管理角色；验收由沟通启动，结论回沟通和统筹 | 入口、workflow、bootstrap、五份参考、权力矩阵的运行架构硬规则 | `SKILL.md:163-170,199,207`；`SKILL.zh.md:29-34`；`README.md:46-51,123`；`workflow.md:7-14`；`bootstrap-workflow.md:3,80`；`communication-role.md:16`；`planning-role.md:9`；`scheduler.md:7,107`；`team-formation.md:11`；`acceptance-role.md:7`；`authority-matrix.md:5-11`。**冲突**：`SKILL.md:18` 的 worker 入口例外 | 同上 | 沟通、统筹、验收 | 四条硬规则和验收回路齐全；第 18 行例外与“客户窗口只加载沟通”冲突 | 不通过 |
| 7 | `authority-matrix.md` 存在并链接，声明不新增权限，覆盖六类角色、三闸门、写入/派发/角色定义/任务状态/验收/备忘录权、禁止事项、变更规则 | 文件内容、链接、冲突声明 | `references/authority-matrix.md:1-60`；`SKILL.md:62,271`；`README.md:94`；`SKILL.zh.md:21`；五份参考的参见链接；`角色卡/任务工具/role-card.md:33`、`技能规范/role-card.md:39`、`测试/role-card.md:34`、`项目管理/role-card.md:40` | 同上 | 人事 | 内容覆盖六类角色和三闸门，明确“汇总视图，不新增权限”，链接齐全 | 通过 |
| 8 | 验收表为核心；统筹交变更包（候选哈希、路径、节点、证据、T0-T3）；同候选/同输入依赖/同命令可复用证据；不全量重跑，除非发布、共享抽象变化或证据不足 | `acceptance-role.md`、`scheduler.md`、`testing.md`、`documentation.md` 的表格、变更包和分档定义一致 | `acceptance-role.md:15-34`；`scheduler.md:108,113-115`；`testing.md:9-26`；`documentation.md:32`；`SKILL.md:143`；`README.md:98`；`SKILL.zh.md:92`；`角色卡/验收/role-card.md:30`；`角色卡/统筹调度/role-card.md:33`。**冲突**：`acceptance-role.md:29` 把“纯文档/治理”列为 T0（不跑代码测试），`testing.md:18` 把“governance or permission change”列入 T3（全量回归）；`testing.md:11` 与 `documentation.md:32`、`SKILL.md:143`、`README.md:98` 又都说不全量重跑除非发布/共享抽象/证据不足 | 同上 | 验收、统筹、技能规范 | 表列、变更包、复用规则一致；T0/T3 对治理变更的分档自相矛盾 | 不通过 |
| 9 | 现行文档统一用 ANS 人事 / ANS People Operations；首次可注原团队组建/招募；文件名、roleId、目录不变；历史日期化记录保留旧名并注现人事 | 现行文档扫描；历史记录区分；文件名/目录/roleId 未变 | `references/team-formation.md` 文件名、`roleId`、目录未变；主入口和五份参考已用新名；但 6 份共享参考、3 份技能规范现行文档、3 份项目管理现行文档、测试边界双格式仍有无注释旧名，见 10.3 K4/K5 | 同上 | 技能规范、人事、项目管理、测试 | 现行文档仍有未注旧名，不能算“统一用新名” | 不通过 |
| 10 | 角色不写自己的定义；角色定义类参考归人事；共享入口/格式/宣传页归技能规范 | 治理边界与技能规范边界的 Section 1；角色卡声明 | `角色卡/governance-boundary.md:7-53` 与 YAML；`角色卡/技能规范/boundary.md:55,61`；五份参考的“不写自己的角色定义”；`SKILL.md:94`；`team-formation.md:5-7`；`role-card.md:23`；`site/` 在技能规范边界内 | 同上 | 人事、技能规范 | 归属和“不写自己的定义”均一致 | 通过 |

### 10.3 阻塞项（必须返工）

#### K1（基线 3、6）：`SKILL.md` 第 18 行仍保留“客户请求可经 worker 角色上下文进入”的例外

`SKILL.md:18` 原文为：“Customer requests enter through the **ANS Communication** built-in role — the single customer interface and end-to-end workflow owner — or, for an existing accepted project assignment, through a fresh context bound directly to its authorized worker role.” 同一节 `SKILL.md:24` 又写“Communication is the only customer channel: the Scheduler and worker roles never contact the customer directly.” 这与基线第 3 条“沟通是唯一客户通道”和第 6 条“客户窗口只加载沟通”直接冲突，也与 `SKILL.zh.md:31`、`README.md:48`、`authority-matrix.md:17`、`action-policy.md:48`、`coordination.md:16` 的现行表述不一致。

**应改为**：客户请求始终经沟通进入并记录；已有正式角色任务由沟通完成必要确认后交统筹，由统筹在独立固定上下文中启动或续接 worker 角色；worker 角色不直接接触客户。删除“or ... authorized worker role”这一入口例外。

#### K2（基线 4）：五维判断与决策表在 `references/team-formation.md` 被完整复制

`references/scheduler.md:21-46` 已是五维标准、决策表和团队计划字段的唯一定义。`references/team-formation.md:22-41` 又完整列出同样的五维、同样的八行决策表和一句话规则，而不是链接；`角色卡/统筹调度/role-card.md:27` 也复述了五维名称和一句话规则。虽然当前文字与 `scheduler.md` 一致，但形成第二处定义，违反“只在 `scheduler.md` 定义，共享文档只链接”的复核要求，后续两处容易漂移。

**应改为**：`team-formation.md` 的“核对团队判断”保留“人事不重新做团队判断，只按 `scheduler.md` 的五维标准与决策表核对计划”这一职责，删除复制的五维和决策表，改为链接 `scheduler.md#五维判断与决策表`；团队计划记录字段可保留为对 `scheduler.md` 要求的引用。`角色卡/统筹调度/role-card.md:27` 同样改为链接，避免第三处复述。

#### K3（基线 8）：`references/testing.md` 的 T3 与 `references/acceptance-role.md` 的 T0 对“治理变更”分档冲突

`references/acceptance-role.md:29` 定义“T0 纯文档/治理：文档、治理、链接、锚点；链接、锚点、一致性检查，不跑代码测试”。`references/testing.md:18` 却把“governance or permission change”列入 T3，并要求“Full applicable regression”。`testing.md:11` 自己也说“Full regression is reserved for release, shared-abstraction changes or insufficient evidence”，与同文件第 18 行矛盾；`documentation.md:32`、`SKILL.md:143`、`README.md:98`、`SKILL.zh.md:92` 均采用“全量回归只在发布、共享抽象变化或证据不足时做”。

**应改为**：以基线和 `acceptance-role.md` 为准，统一 T0-T3。治理文档/链接/锚点变更应落在 T0（做链接、锚点、一致性检查，不跑代码回归）；如确需对“治理程序或权限实现”做代码检查，应在 T3 明确限定为程序/权限实现变更，而不是所有治理文档变更。同步修正 `testing.md:11` 与第 18 行，使四份文档一致。

#### K4（基线 9）：多份现行文档仍用“团队组建 / 招募 / Team Formation”且未注旧名

以下均为现行文档，不是历史日期化记录，直接违反“现行文档统一用 ANS 人事 / ANS People Operations”：

| 文件 | 行 | 现行旧名 |
| --- | --- | --- |
| `references/api-spec.md` | 9、48 | “Team Formation prepares registration”“Team Formation handles …” |
| `references/feature-point.md` | 9、11 | “再交团队组建处理”；角色列表写“招募” |
| `references/group-leadership.md` | 5 | “ANS 团队组建（招募）……招募不自行决定招聘……详见[团队组建]” |
| `references/project-rules.md` | 9 | “交团队组建建立并确认该角色及其边界” |
| `references/shared-directories.md` | 16、23 | “The built-in ANS Team Formation role…”“Team Formation grants…” |
| `references/task-operations.md` | 14、26、30、38 | “内置 ANS 团队组建”及多处“团队组建” |
| `角色卡/技能规范/docs/feature/role-authority-split.md` | 4、22、25、27、35、48、65、69、71、85、87 | 标题、正文和事件摘要中的“团队组建/招募”（第 99 行是带日期的历史条目，见 10.4） |
| `角色卡/技能规范/docs/feature/role-groups.md` | 40、42、50、64 | “团队组建” |
| `角色卡/技能规范/feature-map.md` | 8 | “团队组建、策划、统筹与独立验收” |
| `角色卡/项目管理/docs/architecture.md` | 9、11、19、33、37、55 | “招募”“ANS团队组建（招募）” |
| `角色卡/项目管理/docs/project-rules.md` | 5、41 | “ANS 团队组建（招募）”“以招募维护的角色定义为准”（第 52 行是历史表行，见 10.4） |
| `角色卡/项目管理/feature-map.md` | 3 | “由招募建立本角色” |

**应改为**：统一改为“ANS 人事 / ANS People Operations”；首次出现可按基线注“原团队组建/招募”。以下带注释的用法已合规，不需改动：`references/project-role.md:3` 与 `test-role.md:3` 的“ANS 人事（ANS People Operations，原招募）”、`references/built-in-assembly.md:3` 的“formerly Team Formation/recruitment”、`SKILL.md:119`、`SKILL.zh.md:16,23`、`README.md:85,100`、`references/team-formation.md:3`、`references/built-in-boundary.md:3`、`角色卡/技能规范/boundary.md:55`、`角色卡/governance-boundary.md:3,63`、`角色卡/统筹调度/boundary.md:17`、`角色卡/项目管理/boundary.md:29`。

#### K5（基线 9，边界双格式）：`角色卡/测试/boundary.md` 与 `boundary.yaml` 仍写“ANS Governance 唯一维护”

`角色卡/测试/boundary.md:19` 写“角色卡与边界由 ANS Governance 唯一维护”；`角色卡/测试/boundary.yaml:39` 同步副本同样写“ANS Governance”。这是现行 Section 1 权威文档，不是历史记录，且未注旧名。应改为“角色卡与边界由 ANS 人事 / ANS People Operations 唯一维护”，并在同一次治理交付中同步 Markdown 与 YAML。

### 10.4 残留项（不阻塞）

| 编号 | 事实 | 处理建议 |
| --- | --- | --- |
| N1 | `references/functional-description.md:5` 仍写“Project management owns overall architecture and role collaboration in its own docs/architecture.md.”；该文件不属于任何 Section 1。 | 后续治理轮次确定归属并改为“策划拥有 `docs/planning/` 的产品方案与架构设计；按团队计划建立的项目管理角色只维护实现层 `docs/architecture.md`”。本轮无所有者，不自行修改。 |
| N2（第二轮 N5） | `角色卡/任务工具/role-card.md:30` “交项目管理评审和用户确认”未写“如已按团队计划建立”。 | 后续条件化为“交已按团队计划建立的项目管理角色评审；未建立时由统筹安排”。不影响本轮架构所有权结论。 |
| N3 | `角色卡/governance-boundary.md:61` 及 YAML 的历史沿革仍写“项目管理负责技术架构与实现设计”，未加“已被 2026-10-22 模型取代”。 | 作为历史沿革保留；下次修改时加注，避免误读。 |
| N4 | 历史日期化记录和 memo 中的旧名：`角色卡/统筹调度/memo.md:2,4`、`角色卡/项目管理/memo.md:8`、`角色卡/验收/memo.md:3`、`角色卡/技能规范/docs/change/2026-10-22_change_five-role-model.md`、`docs/scheduling/2026-10-22_five-role-rework.md`、`references/governance-changelog.md`、各角色 `changelog.md`、`doc/` 历史记录等。 | 按基线保留旧名，建议后续治理轮次补“现人事 / now People Operations”注释；本轮不作为阻塞。 |
| N5 | 无 Section 1 所有者的 legacy 参考：`references/code-atlas.md`、`references/documentation-change.md`、`references/documentation-design.md`、`references/documentation-feature.md`、`references/documentation-fix.md`、`references/interface.md`、`references/model.md`、`references/pipeline.md`、`references/provider.md`、`references/role-atlas.md`、`references/service.md`、`references/functional-description.md`。 | 只读 legacy；后续治理轮次决定归属，不阻塞本轮。 |
| N6 | 项目管理角色在本仓库已按需建立；是否保留或停用属于统筹团队计划决定。 | 本轮不改；由统筹在后续团队计划中判断。 |
| N7 | `角色卡/招募/memo.md`、`docs/communication/memo.md` 路径已授权但文件尚未创建；本仓库策划/统筹/验收的项目本地 memo 已存在。 | 角色下次工作时按授权创建；不影响五份 memo 路径的规则。 |
| N8 | 既有 legacy 链接：`doc/feature/2026-09-20_feature_role-function-graphs.md` 等 3 处指向缺失的 `assets/role-dashboard/index.html`；`references/feature-point.md` 的 3 个示例链接位于 fenced code block；Dashboard 模板使用 `__BASE_PATH__` 占位符。 | 均为候选外或示例/模板，不计入现行文档链接缺陷。 |
| N9 | 12 个文件同时出现在通用 `references/built-in-boundary.md` 与仓库本地 `角色卡/governance-boundary.md`（`references/communication-role.md` 等）；`docs/scheduling/2026-10-22_five-role-rework.md` 同时匹配内置边界 `docs/` 条件目录。 | 内置边界明确“项目本地治理边界可覆盖”，且 `docs/` 条件目录明确排除内置管理默认目录 `docs/scheduling/`；按本地覆盖解释为单一适用所有者，不构成实际重复授权。 |

### 10.5 实际命令与结果

| 检查 | 命令／方法 | 实际结果 |
| --- | --- | --- |
| 程序测试 | `python3 -m unittest discover -s scripts/tests -q` | `Ran 236 tests in 76.063s`，`OK`，退出码 0。日志 `/tmp/ans-five-role-acceptance-tests-final.log`，SHA-256 `72f9f5bde4cbc6b6e26bef9585a061fb87a5424e7db92ec065fa4e21776be3cb`。测试通过只说明脚本测试集通过，不代替文档一致性或验收判断。 |
| 空白检查 | `git diff --check HEAD` | 退出码 0，无空白错误。 |
| 本地链接/锚点 | 对 129 个现行 `.md`/`.html` 文件解析 Markdown 行内链接和 HTML `href`，排除 fenced code block 示例、Dashboard `__BASE_PATH__` 模板、站点根绝对路径和 `doc/` legacy | 1301 个链接，0 个未解析的现行文档相对目标；`references/scheduler.md#五维判断与决策表` 锚点存在；`dashboard/README.md#role-channel` 锚点存在。3 个 `doc/feature/...` legacy 链接指向缺失旧资产，见 N8。 |
| 边界覆盖 | 解析 9 对 `boundary.md` Section 1，逐个匹配 77 个受验文件 | 77/77 有适用所有者；无未归属写入目标；12 个文件与通用内置边界名义重叠，按本地覆盖解释为单一所有者，见 N9。 |
| MD/YAML 一致 | 比较 9 对边界的条目集合、类型、路径 | 9/9 一致（技能规范 47、策划 3、统筹调度 5、项目管理 13、验收 7、任务工具 9、测试 11、治理覆盖 43、内置边界 17）。 |
| 候选快照 | `git status --porcelain -uall \| sort`；`git diff HEAD` | 77 条；快照 SHA-256 `a1c5c7f1…`；diff SHA-256 `1c52f1b4…`。 |

### 10.6 结论及理由

**结论：返工。**

理由：

1. **基线 3、6 不满足**：`SKILL.md:18` 的“existing accepted project assignment 可直接经 worker 角色上下文进入”例外，与同文件第 24 行“Communication is the only customer channel”、`SKILL.zh.md:31`、`README.md:48`、`authority-matrix.md:17`、`action-policy.md:48`、`coordination.md:16` 直接冲突；必须删除该例外，客户请求始终经沟通。
2. **基线 4 不满足**：`references/team-formation.md:22-41` 完整复制了 `scheduler.md:21-46` 的五维标准和决策表，而不是链接，形成第二处定义；违反“只在 `scheduler.md` 定义，共享文档只链接”的复核要求。
3. **基线 8 不满足**：`references/acceptance-role.md:29` 将“纯文档/治理”定为 T0（不跑代码测试），`references/testing.md:18` 却将“governance or permission change”定为 T3（全量回归），且 `testing.md:11` 与 `documentation.md:32`、`SKILL.md:143`、`README.md:98` 的“不全量重跑，除非发布/共享抽象/证据不足”矛盾；治理变更的验收档位必须先统一。
4. **基线 9 不满足**：6 份共享参考、3 份技能规范现行文档、3 份项目管理现行文档和测试边界双格式仍有未注旧名（K4、K5）；这不是“历史记录旧名”，而是现行治理文档和现行 Section 1 权限文档的残留。
5. **其余基线通过**：五角色可用性、窄写权与 memo、能力描述分工、权力矩阵、角色定义归属和共享文档归属均满足；236 项测试通过，`git diff --check` 无空白错误，现行文档链接/锚点可解析，77/77 受验文件有适用 Section 1，9/9 边界 MD/YAML 一致。返工不是因为这些项目未完成，而是上述 K1–K5 的实际偏差。

修复范围小且局部：删除 `SKILL.md` 第 18 行的一个例外分句；把 `team-formation.md` 的五维/决策表改为链接；统一 `testing.md` 的 T0-T3 定义；更新 K4/K5 列出的现行文档旧名并同步测试边界 YAML。无需新增角色、边界、路径或程序权限，也不需要重做本轮全部检查。修复后只需复核这些变更行、重新运行同一测试集、`git diff --check`、链接/锚点和边界覆盖检查；除非候选或方案实质变化，不要求全量重跑。

### 10.7 覆盖限制

本结论只对上述冻结候选和客户确认的同一版五内置管理角色方案有效。候选再变化、方案实质变更或修复超出 K1–K5 范围时，须重新核对受影响部分。本报告只写验收获准路径；未修改程序、测试、其他角色文档、角色卡、边界或任务状态，未 commit、未 push、未安装、未发布。

## 11. 最终定向复核（2026-10-22，第四轮）

### 11.1 复核范围与候选快照

本轮只复核第 10 节五个阻塞项（K1–K5）的修复，不重做第 10 节的全量检查；第 10 节已通过或未涉及的项沿用其结论。复核对象仍是当前工作区候选，分支 `feat/five-role-model`，已提交基线 `f76127d`。

- 写本节前 `git status --porcelain -uall` 为 79 条：75 个已修改跟踪文件 + 4 个未跟踪文件（`references/authority-matrix.md`、`角色卡/技能规范/docs/change/2026-10-22_change_five-role-model.md`、`docs/scheduling/2026-10-22_five-role-rework.md`、本报告）。候选快照（文件名与状态码，排序后）SHA-256：`857b0d58ae745a59eddf3e23c03a3b32651d4b99643ea4ae7f3828deb1b6bf9c`；`git diff HEAD` 的 SHA-256：`d75e35a22f428982404ab9ff963bcfe88226fa0c956c2b9f784b5d4c2d067e5c`。
- 关键修复文件 SHA-256：

| 文件 | SHA-256 |
| --- | --- |
| `SKILL.md` | `af822e79d66c49e2e75059b0fd2c6be0b99be0aa01fc5233a49a8ae89d558f1f` |
| `references/team-formation.md` | `62b092df97b75a01e88b7fcdd5a9f8411a86ac6b2b85840378c75085e583ac58` |
| `角色卡/统筹调度/role-card.md` | `e7b56971dd874d398a514779b93450349e04d01980d0d7d4ecdaad6b4b5f93fe` |
| `references/testing.md` | `8a2ea5ae10b51f43bedba271d052891a81858db9ca88f2f297508401aea4e1f7` |
| `references/acceptance-role.md` | `c520153484458b5025262a1838be9a0f7460299c778bf712390d00a48abc089c` |
| `references/scheduler.md` | `862b0afd923783c194c63a8d6c4813f7b3b2ae0a82b2d74ff8bd8e3990ca9243` |
| `references/documentation.md` | `ffeadf13ba343e862888ffdc70077d6a143ec76e70004a559fb58137a72a3015` |
| `README.md` | `a3ec1b9ca0631fbe6c5cbab4e20cfbd90289cd3cf9b72e4ed90475964e40b293` |
| `SKILL.zh.md` | `f33bc9896162f10a409d0a99c6523ccfb98aed4a2c4e23b860c17403fc01d4e8` |
| `角色卡/测试/boundary.md` | `e8b645296f3b27caf31d8148f3c13386258293272d1813fa3b26f19872115805` |
| `角色卡/测试/boundary.yaml` | `661de38392b50993e0c0e33597898a2cdd4d1f9b579f1fb3b68e3945e6b06b86` |
| `references/project-role.md` | `8184a63abc9fb1959830f1128ce433fe1622af59f9c63a0fefeea3763153c6b4` |
| `references/test-role.md` | `3f614070ce10264de739a930538f373af135c971a93762904cb12adf633fedf2` |
| `references/built-in-assembly.md` | `6042d9f63764a447ca3ebf8d6314683d1ae63d8a4daf031d99d94fb39768dccd` |

### 11.2 逐项结果

| ID | 修复要求 | 实际证据（路径/行号） | 结果 |
| --- | --- | --- | --- |
| 1 | 删除 `SKILL.md:18` “客户请求可经 worker 角色上下文进入”的例外，客户请求始终经沟通 | `SKILL.md:18` 现为“Customer requests enter through the **ANS Communication** built-in role — the single customer interface and end-to-end workflow owner.”，无 worker 入口例外；`SKILL.md:24`、`SKILL.zh.md:31`、`README.md:48`、`references/authority-matrix.md:17`、`references/action-policy.md:48`、`references/coordination.md:16` 均一致表述沟通为唯一客户通道。 | 关闭 |
| 2 | 五维标准/决策表只在 `scheduler.md` 定义，`team-formation.md` 与统筹角色卡改为链接 | `references/team-formation.md:22` 现为“按统筹使用的五维判断与决策表（`scheduler.md#五维判断与决策表`）核对团队计划”，不再复制；`角色卡/统筹调度/role-card.md:27` 同样链接 `../../references/scheduler.md#五维判断与决策表`；`references/scheduler.md:21` 的 `### 五维判断与决策表` 锚点存在；对现行文档检索“责任独立性”，仅 `references/scheduler.md:25` 一处定义。 | 关闭 |
| 3 | `references/testing.md` 作为 T0–T3 唯一定义，其他文档统一引用，无冲突 | `references/testing.md:9-26` 定义 T0 纯文档（不涉及治理/权限变更）、T1 局部实现、T2 跨角色/契约/shared、T3 发布/共享抽象/治理或权限变更；`references/acceptance-role.md:25` 以“以 testing.md 的唯一定义为准”引用；`references/scheduler.md:115`、`references/documentation.md:32`、`SKILL.md:143`、`README.md:98`、`SKILL.zh.md:92`、`角色卡/验收/role-card.md:30` 均引用同一来源；`references/acceptance-role.md` 已移除重复的 T0–T3 表。 | 关闭（附 11.4 的 T3 范围说明） |
| 4 | 清理现行文档旧名；历史记录可保留旧名 | 现行非历史文档扫描未发现未注旧名；`references/project-role.md:3`、`references/test-role.md:3` 已用“ANS 人事（ANS People Operations，原招募）”，`references/built-in-assembly.md:3` 已用“ANS People Operations (formerly Team Formation/recruitment)”；共享参考、技能规范现行文档和项目管理现行文档已改为“人事/ANS 人事”；剩余旧名均位于历史日期记录或 memo，并多带“现人事/原团队组建/招募”注释。 | 关闭 |
| 5 | 测试边界双格式改“ANS 人事（ANS People Operations）”；调度只启动工作角色，内置管理角色由沟通启动 | `角色卡/测试/boundary.md:19` 与 `boundary.yaml:39` 均为“角色卡与边界由 ANS 人事（ANS People Operations）唯一维护”；`references/scheduler.md:107` 明确“调度只授权、预留和启动工作角色；策划、人事、统筹、验收由沟通启动独立子代理，调度不启动内置管理角色”，与 `references/authority-matrix.md:20` 一致。 | 关闭 |

### 11.3 实际命令与结果

| 检查 | 命令／方法 | 实际结果 |
| --- | --- | --- |
| 程序测试 | `python3 -m unittest discover -s scripts/tests -q` | `Ran 236 tests in 75.427s`，`OK`，退出码 0。日志 `/tmp/ans-five-role-acceptance-tests-final-targeted.log`，SHA-256 `e180ee6da69b4cec49a480644fb21a3b5372f2e4fa1afee6bea6eabbeb88b238`。测试通过只说明脚本测试集通过，不代替文档一致性或验收判断。 |
| 空白检查 | `git diff --check HEAD` | 退出码 0，无空白错误。 |
| 本地链接/锚点 | 对 133 个现行 `.md`/`.html` 文件解析 Markdown 行内链接和 HTML `href`，排除 fenced code block 示例、Dashboard `__BASE_PATH__` 模板、站点根绝对路径和 `doc/` legacy | 1322 个链接，0 个未解析；`references/scheduler.md#五维判断与决策表`、`references/testing.md#risk-based-verification-and-change-packages` 锚点均存在。 |
| 边界覆盖 | 解析 9 对 `boundary.md` Section 1，逐个匹配 79 个受验文件 | 79/79 有适用所有者；无未归属写入目标；13 个文件与通用内置边界名义重叠，按本地覆盖解释为单一所有者（同第 10 节 N9）。 |
| MD/YAML 一致 | 比较 9 对边界的条目集合、类型、路径 | 9/9 一致（技能规范 47、策划 3、统筹调度 5、项目管理 13、验收 7、任务工具 9、测试 11、治理覆盖 43、内置边界 17）。 |
| 候选快照 | `git status --porcelain -uall \| sort`；`git diff HEAD` | 79 条；快照 SHA-256 `857b0d58…`；diff SHA-256 `d75e35a2…`。 |

### 11.4 残留项（不阻塞）

- **T3 范围说明**：新单一分档把“治理或权限变更”纳入 T3 全量回归，比原基线第 8 条列举的“发布、共享抽象变化或证据不足”更严格。该口径已写入 `references/testing.md:15-23` 和治理变更记录顶部条目，并在 acceptance-role、scheduler、documentation、SKILL、README、SKILL.zh 统一引用；文档间已无冲突。若客户认为该扩展需要单独确认，可在放行前知悉；本轮不据此判返工，因为它是收紧而非放宽检查。
- 历史记录/memo 旧名：`角色卡/统筹调度/memo.md:4,6`、`角色卡/项目管理/memo.md:8`、`角色卡/验收/memo.md:4`、`角色卡/governance-boundary.md:63,67`、`角色卡/技能规范/boundary.md:61`、`角色卡/技能规范/docs/feature/role-authority-split.md:22,99`、`角色卡/项目管理/docs/project-rules.md:52` 等。按基线保留旧名，建议后续治理轮次补“现人事”注释。
- N1：`references/functional-description.md:5` 旧模型句，仍无 Section 1 所有者。
- N2（原第二轮 N5）：`角色卡/任务工具/role-card.md:30` 的评审去向未条件化，建议后续改为“交已按团队计划建立的项目管理角色评审；未建立时由统筹安排”。
- N3：`角色卡/governance-boundary.md:61` 历史沿革仍写“项目管理负责技术架构与实现设计”，建议后续加注“已被 2026-10-22 模型取代”。
- 无 Section 1 所有者的 legacy 参考：`references/code-atlas.md`、`references/documentation-change.md`、`references/documentation-design.md`、`references/documentation-feature.md`、`references/documentation-fix.md`、`references/interface.md`、`references/model.md`、`references/pipeline.md`、`references/provider.md`、`references/role-atlas.md`、`references/service.md`、`references/functional-description.md`。
- 项目管理角色在本仓库已按需建立；是否保留或停用属于统筹团队计划决定。
- `角色卡/招募/memo.md`、`docs/communication/memo.md` 路径已授权但文件尚未创建；角色下次工作时按授权创建。
- 既有 legacy 链接、示例和模板（同第 10 节 N8）；通用内置边界与本地治理边界的名义重叠（同第 10 节 N9）。
- 治理变更记录顶部新增“Final-acceptance rework: single judgment source and unified risk tiers”条目；原“Acceptance table and risk-tiered evidence”条目已同步新分档口径。建议后续严格保持时间点差异说明，避免历史条目被读成当时就采用当前口径（不阻塞）。

### 11.5 结论

**结论：通过（最终定向复核）。**

理由：

1. 第 10 节五个阻塞项均按实际文件/行号核对关闭：唯一客户通道例外已删除；五维/决策表已收敛到 `scheduler.md` 单一来源；T0–T3 已收敛到 `testing.md` 单一来源且各文档无冲突；现行文档旧名已清理，剩余旧名均在历史记录或 memo；测试边界双格式已改为 ANS 人事/People Operations，调度启动措辞与权力矩阵一致。
2. 程序测试 236 项全部通过（75.427s，退出码 0），`git diff --check` 无空白错误；133 个现行文档、1322 个链接 0 未解析；`scheduler.md#五维判断与决策表` 和 `testing.md#risk-based-verification-and-change-packages` 锚点存在；79/79 受验文件有适用 Section 1；9/9 边界 MD/YAML 一致。
3. 残留项均为历史记录旧名、无主 legacy 参考、既有 legacy 链接/模板或需统筹团队计划决定的角色存废，不构成本轮阻塞。T3 范围说明是较原基线示例更严格的口径，已记录在治理变更记录并统一引用；如客户要求单独确认，属于放行前知悉事项，不需要重做本轮修复。

覆盖限制：本轮只复核上述五项，不重做第 10 节全量检查；第 10 节的全量结论仍是其他项的依据。候选再变化、方案实质变更或修复超出这五项范围时，须重新核对受影响部分。本报告只写验收获准路径；未修改程序、测试、其他角色文档、角色卡、边界或任务状态，未 commit、未 push、未安装、未发布。
