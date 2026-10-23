# 2026-10-23 验收并行取证实施：独立验收结果（B2）

- 文件：B2（独立验收结果）
- 版本：1
- 日期：2026-10-23
- 作者：验收主上下文（由沟通启动；唯一判断和唯一 B2）
- 状态：本轮独立验收结果；总体结论 **证据不足**
- 验收基线：客户在闸门 1 确认的策划方案 P2.2，SHA-256 `9df07dc0e2e024d8e2412d5a5bb354a655ae0d1bad101db12dc37efefaf2e6f6`
- 验收对象：统筹 N4 冻结候选（分支 `feat/parallel-acceptance-evidence`；HEAD `06e8a09739db0365871791576b76300599e3e043`；22 条工作区快照，快照 SHA-256 `7dbccaf8154c63371a5069d2c021898aca3bfc8619a97d9c4e2a2267273e6a90`）
- 关联依据：[B1](2026-10-23_parallel-acceptance-evidence-criteria.md)、[G1](../../../../docs/communication/2026-10-23_communication_parallel-acceptance-evidence.md)、[G2](../../../../docs/communication/2026-10-23_communication_parallel-acceptance-evidence-walkthrough.md)、[N4](../../../../docs/scheduling/2026-10-23_parallel-acceptance-evidence.md)、[A3](../../../../references/acceptance-parallel-evidence.md)、[P2.2](../../../策划/docs/design/2026-10-23_design_parallel-acceptance-evidence.md)、[D2](../../../策划/docs/design/2026-10-23_review_parallel-acceptance-evidence.md)
- 性质：本文件是本轮唯一 B2；不是客户确认、不是实施授权、不是发布许可，不授权 commit/push/合并/部署。

## 1. 结论摘要

**总体结论：证据不足。**

- 22 个适用行中，21 行为 `pass`（C1–C12、B-01–B-09），1 行为 `insufficient evidence`（C13），没有 `fail`。
- C13（T3 全量适用回归）在本机 Windows 环境执行了现有 `scripts/tests` 套件：`Ran 196 tests in 41.285s`，`FAILED (failures=13, errors=37, skipped=1)`，退出码 1。失败/错误包含 symlink 权限（WinError 1314）、GBK/UTF-8 解码、缺失历史提交 `6a7d4fe`、POSIX 文件模式差异、Windows 下 shell 脚本执行差异等环境/平台原因；候选未修改代码或测试，测试目录 diff 为空。没有干净的全量回归，按 C13 记 `insufficient evidence`，不降档、不判 `pass`，也不把环境失败改写成候选 `fail`。
- 本轮未引用上一轮 T3-01 客户例外，也未复用上一轮 T3 证据作为本轮通过依据。
- 其余 21 行的证据覆盖当前冻结候选；若后续仅在兼容环境补做 C13，且候选未变，其他行的证据可按“同一候选、同一证据”规则复用，只重新判定 C13 和总体结论。

## 2. 候选、快照与关键哈希

### 2.1 候选前后核对

| 时点 | 条目 | 快照 SHA-256 | `git diff HEAD` SHA-256 | 说明 |
| --- | --- | --- | --- | --- |
| 分发前（验收主上下文入口核对） | 22 条（16 M + 6 ??） | `7dbccaf8…6a90` | `1538dccc…1ff2` | 与 N4 §16.1 完全一致 |
| 证据收集后（G2 已写、B2 未写） | 23 条（22 + G2） | 全部 23 条 `b35f2054…b70d`；排除 G2 后 `7dbccaf8…6a90` | `1538dccc…1ff2` | G2 是沟通走查材料，不是候选 |
| 写入 B2 后（本文件已写） | 24 条（22 + G2 + B2） | 排除 G2/B2 后 `7dbccaf8…6a90` | `1538dccc…1ff2` | B2 是冻结后唯一新增验收输出，不属于候选 |

- 分支与 HEAD 在三次核对中均未变化。
- E1 运行前后、E2 开工/收工的工作区状态文件内容逐字节相同（SHA-256 均为 `7dbccaf8…6a90`）；T3 运行未改变候选条目。
- 候选关键文件哈希在分发前、证据收集后、写 B2 后均与 N4 §16.2 一致；`references/authority-matrix.md` 哈希 `762f2790…01ef`，`git diff HEAD -- references/authority-matrix.md` 为空。
- B2 不是冻结候选的一部分；B2 写入后，候选仍以 22 条快照和 N4 冻结为准。

### 2.2 关键证据文件与哈希

| 文件 | SHA-256 | 用途 |
| --- | --- | --- |
| P2.2 | `9df07dc0e2e024d8e2412d5a5bb354a655ae0d1bad101db12dc37efefaf2e6f6` | 验收基线 |
| D2 | `2567da9d120d787048678ad77c1c624df76a246e54d02ed0d379e1511a557512` | 复核背景，不是基线 |
| A3 | `295d083de0c3a89eb0070542d3626e7b0474b87e5fd185616c9b3a807e03c27a` | 并行取证单一来源 |
| B1 | `c4146041257469448be69a461e34bab562920d3591347f7ecab496e8c4c1ab6c` | 本轮验收标准 |
| `SKILL.md` | `cc8f548f18f385b29a5689e29b67edba0accfd494eac4ca51d925471d6b772b8` | 技能入口 |
| `SKILL.zh.md` | `8a35445d7b87a0980e2ab1229ea062220cde6461ea0c6b0bff634118415b0c0c` | 中文技能入口 |
| `references/acceptance-role.md` | `7bf21811cd293b5f01c780f8dd7cce5149805a84684c3de4e082a644b679b84e` | 验收角色定义 |
| `references/communication-role.md` | `472bc479fbf4fee9cbf29cf090eebf1f3100471fe851cb8e36404bf001f8595f` | 沟通角色定义 |
| `references/scheduler.md` | `53644c48e08364a985a41a3ebf04cd783965f1d642a031ce3798c14c559e1fb8` | 调度角色定义 |
| `references/documentation.md` | `b0c603ada1ad455d2e17f165b454675b562406b88c2ddf95e57d22fe1b6e3e87` | 文档规则 |
| `references/evidence.md` | `ba17b24635fc1b853c55a6504bdf1cace78e797cbe96c61104696dd1972c4c6f` | 证据规则 |
| `references/authority-matrix.md` | `762f27907209019d77546ab031b35b98492bd3dcea3b4ddde29d82ae054b01ef` | 权力矩阵；未修改 |
| `角色卡/验收/role-card.md` | `67385521cc77b3de38759eb22648eaf998d3ef152c487adf22ec691e4ba8809d` | 验收角色卡 |
| `角色卡/governance-boundary.md` / `.yaml` | `bb6e2d55…f19466` / `270c5bf1…313f1f` | 治理边界 |
| `角色卡/验收/boundary.md` / `.yaml` | `08156994…86e278` / `119083e5…02a10c9d` | 验收边界 |
| `references/built-in-boundary.md` / `.yaml` | `73c14abe…c328cb` / `729ca07f…72de2a` | 内置人事边界 |
| `references/governance-changelog.md` | `a5b5ea0c222752f934cf0075d7df6b29e278fe46c87a3d26758f05c4b7215d2e` | 治理变更记录 |
| `角色卡/验收/changelog.md` | `ffba7a1ee3809bf64de6ae09cc5b40a15bda331b2f1a08dceb50a87f8db5f994` | 验收变更记录 |
| G1 | `2b7948be76a0d5116d2b5ea4e68cbda203cbfb216d476ad6a6162be503855a81` | 闸门 0/1/2 与实施授权记录 |
| G2 | `cea8f79dc94c9a953959c9a56242e6775d5531ed263da6b19370cf1ba8716289` | C9 走查材料 |
| N4（PL1） | `c6cb97026dac914088056a6078c96d0837e9c2fcf3504269beb457f49234eb36` | 团队计划与冻结记录（§16 追加后） |
| E1 实际运行日志 | `8f3b03927d7138d0d5fd0586907ab3e8aedc3752db4e860954819b7208dece1c` | `C:\Users\51054\AppData\Local\Temp\tmp.0jXZZJoiZJ\E1-t3-python.log` |
| E1 python3 尝试日志 | `05640271fe4631f6d0759c164bafa972719c8f54c62b6470c21487ef84e74f11` | 同目录 `E1-t3-python3.log` |
| E1 状态/差异 | `7dbccaf8…6a90` / `1538dccc…1ff2` | `E1-status-before.txt` / `E1-status-after.txt` / `E1-diff.patch` |
| E2 状态/差异 | `7dbccaf8…6a90` / `1538dccc…1ff2` | `C:\Users\51054\AppData\Local\Temp\tmp.RnToHPRxpD\status.txt` / `status_final.txt` / `diff_head.patch` / `diff_head_final.patch` |
| E2 清单/链接/边界/校验 | `7b18eb2d…5af0`（MANIFEST）；`9faae5fd…8b3c`（link_check）；`a2734ce4…8ba3`（owner_map）；`3b58bd06…ceb2`（boundary_compare）；`8c04bbee…954c`（git_checks）；`3077ef47…ae3b`（notes_norm）；`bcaade04…e099`（md_yaml_rawdiff） | 系统临时目录 `tmp.RnToHPRxpD` |
| 主上下文 B-07/B-08 日志 | `fd6159e3f66cc7c93c1b69679a69bbd89f99de844da7d02c2405bb15cc30e43a` | `/tmp/ans-acceptance-main-b07-b08-2026-10-23.log` |

## 3. 取证方式、C9 走查与工具只读核对

### 3.1 取证方式

- **并行取证**，启用 2 个只读取证子上下文：E1（T3 全量适用回归）和 E2（机械静态证据）。E1、E2 是同一验收角色（`acceptance`）的只读取证上下文编号，不是角色、不是子验收，不产生第二个 B2。
- 依据：本轮为 T3；B1 适用行 22 条（≥约 12 条）；存在长时执行、机械静态、语义条款、记录/历史等多个独立证据族；单上下文预计超过 20 分钟；E1/E2 读集和命令可分离。符合 A3 第 6.2 节并行条件和团队计划建议的 E1 + E2 配置。
- E1 先启动（长测试先行），E2 同批启动；主上下文在等待期间完成语义条款、记录/历史和判断类行。
- 未启用 E3/E4：当前可用的 Explore agent 是只读搜索代理，读摘录、不做完整审阅；语义条款（C1–C4、C12、B-04、B-05）和记录/历史（C5–C10、B-07、B-08、B-09）由主上下文顺序完成，避免浅层证据和重复复核。该安排仍满足 C9 的“至少 2 个只读取证子上下文”。

### 3.2 C9 走查记录

- 启动者：沟通（ANS Communication）。
- 子上下文数量与编号：2 个，E1、E2；未启动 E3/E4；未启动工作角色或其他管理角色。
- 任务书与回报：任务书由验收主上下文编写，沟通原样转交；E1/E2 回报经沟通原样转交主上下文，不增删、不摘要、不判断、不形成结论；两份回报末尾均有“只提供证据、不含验收结论”声明。
- 沟通材料：G2 `docs/communication/2026-10-23_communication_parallel-acceptance-evidence-walkthrough.md`，SHA-256 `cea8f79d…6289`；明确“不是客户确认、不是验收基线、不是第二个结论”。
- 唯一结论：本 B2 是唯一 B2；没有第二个验收结论、没有并行判决。
- B-07 演练：按 C9 方式一（部分失败/模拟启动失败），E2 任务书把 B-07 标为演练项，沟通不启动该演练分组，E2 不执行 B-07，主上下文在合并阶段按同一 B1 原文顺序补做；G2 第 6 节和本 B2 §6 记录。未伪造失败、未降低标准。
- 工具只读缺口：见 §3.3；已记录并披露。

### 3.3 工具只读能力核对（C5/C9）

- 使用的子上下文类型：Explore agent；工具集不含 `Edit`、`Write`、`NotebookEdit`、`Agent`，含 `Read`、`Grep`、`Glob`、`Bash`。
- 子上下文没有 `acceptanceToken`：仓库无 `.ans/project.json`，本轮不启用 task_ops；Explore 没有验收接口、任务状态写权、B2 写权或启动其他上下文的能力。
- 形式化缺口：当前工具没有 `writeFiles`/`writeSet` 形式的授权参数，`Bash` 仍是残余写通道，因此不是硬只读沙箱。
- 补偿控制：任务书限定只读路径和精确命令；日志/辅助脚本只放系统临时目录；子上下文必须回报实际命令；主上下文分发前和合并后核对 `git status`、HEAD 和关键文件哈希；任何仓库文件变化都会使相关证据失效并触发回退。
- 实际结果：E1、E2 都成功启动并完成；E1/E2 开工与收工快照逐字节相同；除 G2（沟通材料）和 B2（本文件）外，未发现子上下文写入仓库；候选 22 条条目未变。
- 判断：C5/C9 按实质只读授权判 `pass`；形式化 `writeFiles`/`writeSet` 缺口作为工具限制记录，不把它说成硬只读沙箱。若后续要求字面级硬隔离，应按 C5/C10 回退单上下文，并在 B2/G2 记录“并行不可用/工具缺口”。

## 4. 分配摘要

| 行 ID | 主责 | 说明 |
| --- | --- | --- |
| C1–C4 | 主上下文 | 语义条款；E2 提供文件范围/边界/哈希支持 |
| C5–C10 | 主上下文 | 工具、候选、分配、模式、C9、回退等判断/记录 |
| C11 | E2 | 机械静态；含 B-06 链接/锚点结果 |
| C12 | 主上下文 | 五角色、闸门、唯一判断语义核对 |
| C13 | E1 | T3 全量适用回归 |
| B-01、B-02、B-03、B-06 | E2 | 写集、唯一所有者、MD/YAML、链接/锚点 |
| B-04、B-05 | 主上下文 | 单一来源、措辞一致语义核对 |
| B-07 | 主上下文 | 演练项，沟通不启动，主上下文顺序补做 |
| B-08、B-09 | 主上下文 | 记录一致、候选快照；E2 提供 diff/哈希支持 |

完整性核对：22/22 行都有且只有一个主责；无遗漏、无双重主责；E1 主责 1 行、E2 主责 5 行、主上下文主责 16 行。支持证据不替代主责。

## 5. 主复核措施

1. **候选快照**：分发前记录分支、HEAD、`git status` 22 条及 SHA-256、`git diff HEAD` SHA-256；证据收集后和写 B2 后再次记录；排除 G2/B2 后候选条目仍为 22 条、哈希仍为 `7dbccaf8…6a90`，`git diff HEAD` 仍为 `1538dccc…1ff2`。
2. **E1 原始证据**：打开并复算 E1 日志 SHA-256（`8f3b0392…ce1c`、`05640271…4f11`）；核对日志中 `Ran 196 tests in 41.285s`、`FAILED (failures=13, errors=37, skipped=1)`、`exit=1`；核对 `git diff HEAD -- scripts/tests` 与 `git status -- scripts/tests` 为空；核对运行前后状态文件 SHA-256 与候选一致。
3. **E2 原始证据**：打开并复算 E2 状态、diff、链接、边界、所有者、哈希等文件；核对 19 个变更/新增 `.md` 中的 328 条内联链接、0 缺失路径、0 缺失锚点、0 外部 scheme、0 site 根路由；核对三对边界 Section 1 字段差异 0；核对 `git diff HEAD -- scripts test dashboard site` 和 `authority-matrix` diff 均为 0 字节。
4. **B-07 主上下文补做**：执行 `git diff --check HEAD`（退出码 0）；对 6 个未跟踪候选文件检查尾随空白、制表符和结尾换行（均 0 / 0 / 有结尾换行）；日志 `/tmp/ans-acceptance-main-b07-b08-2026-10-23.log` SHA-256 `fd6159e3…e43a`。
5. **B-08 记录核对**：逐条对照治理 changelog、验收 changelog 与 `git status`/`git diff HEAD`/实际文件；changelog 提到的 A1–A3、A5–A14、S1–S4、B1 路径均存在且状态符合（M 或 ??）；`authority-matrix` 不在变更清单且 diff 为空；未发现“未发生却写成已发生”的修改或补造授权。
6. **语义行**：主上下文逐份读取 acceptance-role、role-card、SKILL.md、SKILL.zh.md、communication-role、scheduler、documentation、evidence、authority-matrix、A3；按关键句行号核对；全库检索“验收可启动子代理”“验收新增启动权”“并行判决”“第二验收”“多个验收结论”“第六个角色”等，命中均为否定性约束、B1/团队计划检索项或历史记录，未发现肯定性相反现行表述。
7. **抽样复跑**：对 E2 的链接检查方法做抽样核对（SKILL.md 的 `references/scheduler.md#五维判断与决策表`、`#role-binding-and-handoff` 等锚点；A3 新参考标题可生成锚点）；对关键文件哈希复算；不要求主上下文重跑 E1 全量回归。

## 6. 冲突、失效与演练

- **B-07 定义观察**：E2 指出任务书把 B-07 标为演练项，而 B1/团队计划把 B-07 定义为空白/格式检查。两者不矛盾：B-07 的 B1 标准就是“空白/格式”；任务书只是把它选为 C9 演练分组，并要求 E2 不执行、主上下文补做。主上下文按 B1 原文执行了 B-07，未把它当成已由 E2 完成。
- **G1/PL1 哈希与 mtime 观察**：G1 当前哈希 `2b7948be…`、PL1 当前 `c6cb9702…`，与 B1 §1.2 记录的部分历史哈希不同；G1/PL1 mtime 晚于 B1。按 B1 §1.2 的“来源文件后续追加按对应章节内容核对”处理；闸门 0/1/2 内容完整，N4 记录的 G1 哈希与当前一致，PL1 §16 追加导致自身哈希变化。未发现候选内容冲突，未使任何验收证据失效。
- **未跟踪文件的版本历史限制**：A3、B1、G1、PL1、P2.2、D2 无 git 历史，无法用 `git diff` 证明其未改；用哈希、mtime、changelog 和候选冻结记录交叉核对。该限制不改变当前快照与 N4 一致的结论。
- **候选变化**：未发生。E1/E2 前后快照相同；主上下文分发前、证据收集后、写 B2 后候选条目和关键哈希一致。没有证据因候选变化而失效。
- **冲突处理**：没有两个分组对同一行给出互相矛盾的观察；没有投票、平均或多数处理。B-07 观察按“读决定性来源（B1 原文）+ 主上下文补做”处理，未记 `insufficient evidence`。
- **演练记录**：演练方式一（部分失败→主上下文补做）；事先标注在 E2 任务书；沟通未启动 B-07；E2 未执行；主上下文补做并保留同一证据字段；未降低标准。G2 第 6 节记录了同一路径。

## 7. 限制与未检查事项

- **C13 环境限制**：只运行 `scripts/tests`；未运行仓库根 `test/` 和其他 T3 发布/共享抽象专项检查；`skipped=1` 的具体测试未捕获；失败根因未诊断，只保留原始 traceback；`python3` 是 Windows 应用执行别名存根，实际使用 `python` 3.14.7；Windows 无 symlink 特权、无 POSIX 0o600/0o700 语义、locale cp936、缺失历史提交 `6a7d4fe`、Windows 下 `#!/bin/sh` 脚本执行差异。
- **工具限制**：Explore 无 Edit/Write/Agent，但 Bash 是残余写通道；无形式化 `writeFiles`/`writeSet`；按 §3.3 补偿控制使用并行，不把它说成硬只读沙箱。
- **链接检查范围**：B-06 只覆盖 19 个变更/新增 `.md` 的内联链接/图片；未覆盖引用式链接、自动链接、未变更文档指向本轮文件的链接；锚点 slug 为 GitHub 规则近似，未用独立 Markdown 渲染器复核；`site` 根路由分支无样本；路径存在性不等于语义正确。
- **边界/顺序**：B-02 的 mtime 只能反映最后修改时间，不能严格区分创建/修改先后；changelog 为决定性记录。治理 changelog mtime 早于 A3 最后写盘，属于“记录先写、文件后编辑”的可能情况，未发现内容矛盾。
- **B-08**：未跟踪文件无 git 历史；未安装技能副本、外部站点、发布渠道不在本仓库证据范围内；changelog 的事实内容按 diff、路径、哈希和记录交叉核对，未做独立时间机器验证。
- **未检查**：未检查其他角色工作草稿、未读取其他子上下文结果（除 E1/E2 回报）、未使用 acceptanceToken、未调用验收接口、未写任务状态、未 commit/push。
- **旧例外**：未引用上一轮 T3-01 客户例外，未复用上一轮 T3 证据。

## 8. 验收表

说明：E1、E2 是同一验收角色的只读取证上下文编号，不是角色、不是子验收；本表“产出角色”中“E1/E2”仅表示证据收集上下文，判断和唯一结论仍由验收主上下文作出。C13 的候选版本与本表所有行相同：N4 冻结候选（分支 `feat/parallel-acceptance-evidence`，HEAD `06e8a09…`，快照 `7dbccaf8…6a90`）。

| ID | 方案条目/标准（摘要） | 需要的证据 | 实际证据路径/哈希 | 候选版本 | 产出角色 | 结果 | 验收判断 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| C1 | 验收角色定义和角色卡写明沟通启动唯一验收主上下文和全部只读取证子上下文；主上下文只合并/判断、不启动；子上下文只读、只交证据、不写 B2、不给结论；最多 4 个 | acceptance-role、role-card 相关段落及互链 | `references/acceptance-role.md` 第 7 行（SHA-256 `7bf218…b84e`）；`角色卡/验收/role-card.md` 第 35 行（`673855…809d`）；两处均链接 A3；B-06 链接 0 缺失 | `7dbccaf8…6a90` | 人事（文档）；验收主上下文复核 | 启动者、主上下文职责、子上下文限制、上限齐全；无相反表述 | `pass` |
| C2 | 存在 A3 单一来源，含分组原则、最多 4 个、任务书/回报格式、沟通交接、合并复核、冲突、阈值、回退、复用；其他文档只摘要/链接；A3 由人事维护；内置边界决定已记录 | A3 章节结构；其他文档链接段落；built-in boundary 条目；治理 changelog | A3（`295d08…c27a`）第 1–9 节覆盖全部要求；A3 第 3 行声明人事唯一维护；`references/built-in-boundary.md` 第 11 行含 A3 精确路径；`references/governance-changelog.md` 第 7–9 行 N1a/N1b 记录 | `7dbccaf8…6a90` | 人事（文档）；验收主上下文复核 | 单一来源结构完整；内置边界决定已记录；其他文档只摘要/链接 | `pass` |
| C3 | 权力矩阵保持原文（验收“无；由沟通启动”，无新增启动权）；acceptance-role、SKILL.md、SKILL.zh.md 精确写明启动模型；communication-role 写明原样转交、不摘要成结论、对客户只引用 B2；全库无相反现行表述 | authority-matrix 未变及原文；四份文档改写点；全库检索 | `references/authority-matrix.md`（`762f27…01ef`）第 21 行“无；由沟通启动”，diff 为空；acceptance-role 第 7 行；SKILL.md 第 166/197/207 行；SKILL.zh.md 第 32 行；communication-role 第 16/22/39/66 行；全库检索无肯定性相反表述 | `7dbccaf8…6a90` | 人事、技能规范（文档）；验收主上下文复核 | 矩阵原文未变；启动/判断/转交措辞一致；未发现相反现行表述 | `pass` |
| C4 | B1/B2 结构不变：B1 四种判断值和证据列不变；B2 三种总体结论不变；B2 增加取证方式、子上下文、候选前后核对、主复核、冲突/失效、限制；“产出角色”注明 E1/E2 是上下文编号；只有主上下文写 B2 | B1 表头/判定值；documentation/acceptance-role 来源记录要求；本轮 B2 表头与来源记录 | B1 第 129/211 行 8 列；B1 第 80–105 行四种判断值/三种结论；`references/documentation.md` 第 34 行；`references/acceptance-role.md` 第 54 行；本 B2 §3–§9 | `7dbccaf8…6a90` | 人事、技能规范、验收 | B1/B2 结构与判断口径不变；B2 来源记录齐全；唯一 B2 由主上下文写 | `pass` |
| C5 | 子上下文无 Section 1 写路径、无 acceptanceToken、不能提交验收结论；工具可签发独立只读任务授权；不能签发时回退并记录；证据在临时目录；除主上下文写 B2 外取证不产生仓库变更 | 任务书/授权说明；工具核对；G2；前后 `git status` | 本 B2 §3.3；G2 §3；E1/E2 任务书；E2 `git_checks.txt`（`8c04bb…954c`）；候选前后快照 `7dbccaf8…6a90`；Explore 无 Edit/Write/Agent、无 token；形式化 `writeFiles`/`writeSet` 缺口记录为限制 | `7dbccaf8…6a90` | 验收主上下文；沟通（G2） | 实际只读执行可核对；无 token；无仓库写入；形式化只读授权缺口已披露 | `pass` |
| C6 | 候选冻结约束：变更包候选哈希/版本即冻结依据；每份回报记录候选标识；主上下文分发前/合并后各核对；候选变化按 A3 5.2 统一失效 | 规则文本；两次快照/HEAD/哈希；N4 候选标识 | 本 B2 §2.1；E1/E2 回报候选标识；E1/E2 状态文件；N4 §16；A3 第 151–156 行 | `7dbccaf8…6a90` | 验收主上下文；统筹（冻结） | 分发前/合并后一致；每份回报带候选；无失效证据 | `pass` |
| C7 | 分配矩阵覆盖全部适用行且每行恰一个主责；冲突按重跑/读决定性来源，未解决记 insufficient；不投票/平均/多数 | 规则文本；本轮分配矩阵；冲突记录 | 本 B2 §4（22/22，一主责）；A3 第 51–57 行；§6 冲突记录（B-07 定义观察按 B1 原文+补做处理） | `7dbccaf8…6a90` | 验收主上下文 | 矩阵完整；无多重主责；无投票/平均 | `pass` |
| C8 | 阈值：单上下文默认条件和并行条件、最多 4 个、协调成本规则写明；B2 记录本次模式和理由；小任务实际单上下文 | 规则文本；B2 取证方式记录 | A3 第 190–221 行；本 B2 §3.1（并行、2 个、T3/22 行/多证据族/预计 >20 分钟/净收益） | `7dbccaf8…6a90` | 验收主上下文 | 阈值规则落地；本轮模式与理由已记录 | `pass` |
| C9 | 用沟通启动的至少 2 个只读取证子上下文做真实验收；记录启动者、数量/编号、任务书/回报转交、回退路径；演练冲突或部分失败/回退；单一 B2 含分配/合并/主复核；G2 不是客户确认；工具缺口记录 | G2、B2、沟通记录、演练记录、前后 `git status` | G2（`cea8f7…6289`）§1/§2/§6；本 B2 §3.2/§6；E1/E2 回报；B-07 补做日志 `fd6159…e43a` | `7dbccaf8…6a90` | 验收主上下文；沟通（启动/转交/G2） | 2 个子上下文；启动/转交/演练/唯一 B2 齐全；G2 性质声明完整 | `pass` |
| C10 | 回退规则：无法启动子上下文时顺序单上下文，记录“并行不可用”原因和缺口，标准不放宽 | 规则文本；B2/G2 回退记录 | A3 第 223–231 行；G2 §3；本 B2 §3.3/§6（B-07 部分失败→主上下文补做） | `7dbccaf8…6a90` | 验收主上下文；沟通 | 回退规则落地；演练路径记录；未降标准 | `pass` |
| C11 | 不引入代码/测试改动；如仓库有文档链接检查则通过；变更文档链接/锚点可解析；`git diff --check HEAD` 退出码 0 | 文件清单、`git status`、diff、链接检查 | E2 `git_checks.txt`：`scripts/`、`test/`、`dashboard/`、`site/` diff 0 字节；`git diff --check HEAD` 退出码 0；B-06 328 链接/0 缺失/0 坏锚点；`scripts/` 无专用链接检查脚本，C11 链接子项 `not applicable` 有依据；B-07 主上下文补做未跟踪文件空白检查通过 | `7dbccaf8…6a90` | 验收主上下文（B-07）；E2（其余） | 无代码/测试改动；链接/锚点通过；空白/格式通过；专用检查子项不适用有依据 | `pass` |
| C12 | 五个内置管理角色不变；三道客户闸门和权力矩阵不变；验收唯一判断和唯一 B2 不变；无“并行判决/多个验收结论/验收新增启动权”现行表述 | 角色定义、矩阵原文、技能入口、全库检索 | SKILL.md 第 105–113 行五角色表；authority-matrix 第 17–21 行五角色、第 28–30 行三闸门（`762f27…01ef`，diff 空）；A3 第 11 行唯一判断/唯一 B2；全库检索无肯定性相反表述 | `7dbccaf8…6a90` | 人事、技能规范、验收 | 五角色/三闸门/矩阵不变；唯一判断/唯一 B2 不变；无相反现行表述 | `pass` |
| C13 | T3 全量适用回归：仓库根运行 `scripts/tests`，记录命令/环境/时间/退出码/日志哈希/测试数/候选；不改测试；环境不可用记 insufficient，不降档；不引用上一轮例外 | 回归日志与哈希、环境、候选、测试目录 diff | E1 实际运行：`python -m unittest discover -s scripts/tests -q`（`python3` 为 Store 别名存根，退出 49）；`Ran 196 tests in 41.285s`；`FAILED (failures=13, errors=37, skipped=1)`；退出码 1；日志 `8f3b0392…ce1c`；`git diff HEAD -- scripts/tests` 和 `git status -- scripts/tests` 为空；环境：Windows 11/Git Bash、Python 3.14.7、cp936、无 symlink 特权、缺 `6a7d4fe`、POSIX mode 差异 | `7dbccaf8…6a90` | 验收角色（E1 只读取证上下文，主上下文复核）；统筹环境协调 | 套件整体运行一次；196 项；13 FAIL/37 ERROR/1 skipped；退出码 1；环境/平台原因；无干净全量回归 | `insufficient evidence` |
| B-01 | 所有变更/新增文件在团队计划写集内；受保护路径、A4、P2.2/D2、上一轮记录未被修改；没有覆盖无关用户改动 | `git status`、`git diff HEAD`、变更清单 | E2 `status.txt` 22 条=16 M+6 ??，与 N4 一致；22 条全部映射 A1–A3/A5–A14/S1–S4/B1/G1/PL1 或 P2.2/D2；`scripts/test/dashboard/site` diff 0；构建配置 0；`2026-10-22` 路径 0；A4 diff 0；P2.2/D2 哈希 `9df07d…`/`2567da…` | `7dbccaf8…6a90` | 验收角色（E2 只读取证上下文，主上下文复核） | 无计划外条目；受保护路径未改；无上一轮记录混入 | `pass` |
| B-02 | 每个变更/新增文件恰一个 Section 1 所有者；A3 先入治理/内置边界，B1/B2 先入验收边界；不得先写后补；无目录级扩权 | 各 boundary MD/YAML；changelog；创建/修改顺序 | E2 `owner_map.txt`（`a2734c…8ba3`）：22 条均有精确/默认/条件目录授权；治理 45/45、内置 10/10、验收 11/11；同一边界无重复路径；A3/B1/B2 精确单文件；治理 changelog 第 7–9 行、验收 changelog 第 39–45 行记录“先边界/路径、后文件/流程”；mtime 支持（`mtimes.txt`），以 changelog 为决定性记录 | `7dbccaf8…6a90` | 验收角色（E2 只读取证上下文，主上下文复核） | 所有者唯一；A3/B1/B2 精确路径；记录顺序符合；无目录级扩权 | `pass` |
| B-03 | 治理边界、验收边界、内置边界三对 MD/YAML 的条目集合、类型、路径、用途一致 | 逐项解析/比对 | E2 `boundary_compare.txt`（`3b58bd…ceb2`）：治理 45/45、内置 10/10、验收 11/11；SECTION1_FIELD_DIFFS=0；`notes_norm.txt`（`3077ef…ae3b`）0 未匹配 | `7dbccaf8…6a90` | 验收角色（E2 只读取证上下文，主上下文复核） | 三对 Section 1 语义一致；notes 规范化后一致 | `pass` |
| B-04 | 分组、上限、任务书/回报字段、合并、冲突、阈值、回退、复用规则只在 A3 完整定义；其他操作性文档只摘要/链接，无完整清单复制；P2.2 是设计来源，不作为第二套操作规则 | A3 章节；其他文档检索 | A3 第 1–9 节完整；acceptance-role、communication-role、scheduler、documentation、evidence、SKILL.md、SKILL.zh.md、role-card 均只摘要并链接 A3（行号见 §5 第 6 项）；未发现完整字段表/分组表复制 | `7dbccaf8…6a90` | 验收主上下文（文档产出：人事、技能规范） | A3 单一来源；其他文档无完整复制；P2.2 作为设计来源不构成操作性第二套规则 | `pass` |
| B-05 | 所有相关文档一致写明启动者、主上下文职责、子上下文限制、最多 4 个、E1/E2 是上下文编号、不新增验收启动权、不并行判决、矩阵不变；无相反现行表述 | 逐句核对；全库检索 | acceptance-role 第 7 行、role-card 第 35 行、SKILL.md 第 166/197/207 行、SKILL.zh.md 第 32 行、communication-role 第 16/22/39/66 行、scheduler 第 7/115 行、documentation 第 34 行、evidence 第 27 行、A3 第 5/10–12/177–188 行；全库检索命中均为否定性约束/历史记录，无肯定性相反现行表述 | `7dbccaf8…6a90` | 验收主上下文（文档产出：人事、技能规范） | 关键措辞一致；E1/E2 上下文编号说明齐全；无相反现行表述 | `pass` |
| B-06 | 变更文档本地链接/锚点可解析；新参考锚点可被引用 | 变更 `.md` 链接/锚点解析 | E2 `link_check.txt`（`9faae5…8b3c`）：19 个文件、328 链接、外部 0、缺失路径 0、缺失锚点 0、site 根路由 0、24 个锚点链接全部命中；A3 28 个标题可生成锚点 | `7dbccaf8…6a90` | 验收角色（E2 只读取证上下文，主上下文复核） | 19 个变更/新增 .md 内联链接/锚点全部解析；未见断链 | `pass` |
| B-07 | `git diff --check HEAD` 退出码 0；新增未跟踪文件另行检查或说明未覆盖 | 命令输出/退出码；未跟踪文件空白检查 | 主上下文补做日志 `fd6159e3…e43a`：`git diff --check HEAD` 退出码 0；A3、B1、G1、PL1、P2.2、D2 六个未跟踪候选文件尾随空白 0、制表符 0、均有结尾换行；G2（非候选）也无空白问题 | `7dbccaf8…6a90` | 验收主上下文（演练补做） | 已跟踪 diff 空白检查 0；未跟踪候选文件逐一检查通过 | `pass` |
| B-08 | governance-changelog、验收 changelog 与实际 diff 一致；未发生却写成已发生/补造历史授权；A4“未修改”有实际证据 | changelog 与 diff 逐条对照；A4 diff 为空 | 治理 changelog 第 3–9 行 N1a/N1b、验收 changelog 第 39–45 行路径/流程条目；提到的 A1–A3/A5–A14/S1–S4/B1 路径均存在且状态 M/??；authority-matrix 不在 status、diff 0 字节、哈希 `762f27…01ef`；G1 闸门 2/实施授权原文支撑记录；无未发生修改/补造授权 | `7dbccaf8…6a90` | 验收主上下文（记录产出：人事） | changelog 与实际 diff 一致；A4 未改有证据；未发现补造 | `pass` |
| B-09 | 写报告前记录 `git status`、分支、HEAD、关键文件哈希；报告只对冻结候选负责；B2 不属于候选；T3 运行不改变候选 | N4 冻结与验收前后快照对照；关键哈希；B2 清单 | 本 B2 §2.1：分发前 22 条 `7dbccaf8…`；证据后 23 条（排除 G2 后 22 条 `7dbccaf8…`）；写 B2 后 24 条（排除 G2/B2 后 22 条 `7dbccaf8…`）；diff 始终 `1538dccc…`；关键哈希同 N4；E1/E2 前后状态相同 | `7dbccaf8…6a90` | 验收主上下文；统筹（冻结） | 候选前后一致；B2/G2 不属候选；T3 未改变候选条目 | `pass` |

## 9. C13 专项说明与总体结论

### 9.1 C13 证据事实

- 命令：优先 `python3 -m unittest discover -s scripts/tests -q`；因 `python3` 是 Windows 应用执行别名存根（`Python was not found`，退出 49），按 B1 C13 预案改用 `python -m unittest discover -s scripts/tests -q`，Python 3.14.7（`C:\Users\51054\AppData\Local\Programs\Python\Python314\python`）。
- 工作目录：`C:\Users\51054\Desktop\work\ans-skill`；时间：2026-10-23T18:37:31+0800 至 18:38:14+0800；`Ran 196 tests in 41.285s`；`FAILED (failures=13, errors=37, skipped=1)`；退出码 1；无 `OK`。
- 日志：`E1-t3-python3.log` SHA-256 `05640271…4f11`；`E1-t3-python.log` SHA-256 `8f3b0392…ce1c`；原始日志保留在系统临时目录，本 B2 记录路径和哈希。
- 失败/错误类别（原始 traceback）：`OSError [WinError 1314]` 12 次；`UnicodeDecodeError 'gbk'` 15 次、`'utf-8'` 3 次；`IndexError` 4 次；`CalledProcessError` 2 次（含 `git show 6a7d4fe:scripts/task_ops.py` exit 128）；`JSONDecodeError` 2 次；`coordination_store.Rejected` 1 次；`AssertionError` 13 次；`ValueError` 2 次。可见原因包括无 symlink 特权、cp936 解码、缺失历史提交、Windows 下 POSIX 模式/脚本执行差异。
- 测试目录：`git diff HEAD -- scripts/tests` 与 `git status --porcelain -uall -- scripts/tests` 均为空；候选未修改测试。
- 结论：这不是一个干净的全量回归；失败/错误没有显示为候选文档变更导致的缺陷，也没有可判 `pass` 的完整证据。按 C13 和 `references/testing.md` 的 T3 规则记 `insufficient evidence`，不降档、不猜测、不引用上一轮客户例外。

### 9.2 总体结论

- 没有 `fail`；C13 为 `insufficient evidence`；其余 21 行为 `pass`。
- 按 B1 §2.2，没有 `fail` 但有 `insufficient evidence` 时，总体结论只能是 **证据不足**。
- 本结论只对 N4 冻结候选（22 条，快照 `7dbccaf8…6a90`）和客户闸门 1 确认的 P2.2 版本有效；B2/G2 不属于冻结候选。
- 统筹不得按通过放行。后续可在兼容环境（Linux/WSL/CI，或具备 symlink 权限、POSIX 模式、完整历史提交的环境）对同一冻结候选重跑同一 `scripts/tests` 命令，记录同一候选、环境、命令、退出码、日志和哈希；若候选未变，其他 21 行证据可复用，只重新判定 C13 和总体结论。
- 若候选、P2.2 或相关规则发生实质变化，按 P2.2 7.2 / A3 5.2 的统一失效口径处理，不引用本 B2 中已失效的部分。

## 10. 性质声明

- 本文件是唯一 B2，由验收主上下文写；没有第二个 B2、没有并行判决、没有多个验收结论。
- 本文件不是客户确认、不是实施授权、不是验收基线；G2、D2、子上下文回报、实施者自述和工具成功都不是客户确认或验收通过。
- 本文件不授权 commit、push、合并、发布、部署或修改其他文件。
- 本文件不引用上一轮 T3-01 客户例外，不把上一轮 T3 证据作为本轮通过依据。
