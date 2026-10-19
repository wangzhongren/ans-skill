---
id: role-authority-split-validation
type: change
title: 角色分权 CLI 的独立流程与回归验证
created: "2026-10-19"
updated: "2026-10-19"
timezone: Asia/Shanghai
status: verified
related: [role-authority-split-design]
events:
  - date: "2026-10-19"
    kind: created
    summary: 固定测试按已授权方案准备独立真实 CLI 场景，尚未报告执行成功
  - date: "2026-10-19"
    kind: verified
    summary: 独立25个CLI场景和完整201测试通过，保留一轮过窄文案断言失败及修正证据，完成隔离timer、Dashboard与9组边界静态核对
  - date: "2026-10-19"
    kind: verified
    summary: 终验通过后仅复核6份文档状态与引用，保持原196输入集合刷新清单，未重跑程序回归
---

# 角色分权 CLI 的独立验证

本记录由固定【测试】上下文维护。依据[分权方案](../../../项目管理/docs/design/2026-10-19_design_role-authority-split.md)、[独立验收标准](../../../验收/docs/acceptance/2026-10-19_role-authority-split-criteria.md)及[项目法案](../../../项目管理/docs/project-rules.md)。受测功能由[任务工具](../../../任务工具/feature-map.md)与[技能规范](../../../技能规范/docs/feature/role-authority-split.md)维护；测试导航见[本角色导航](../../feature-map.md)。

已确认范围包含独立测试文件 `scripts/tests/test_role_authority_flow.py`，通过 Python 子进程调用 `scripts/task_ops.py --root <临时项目> --task <id> <command> --request -`；不复用开发者 `operate()` helper。临时凭证仅用于夹具，不用于真实仓库任务。

实际完成 C1–C8/A1–A12 对应的下列验证。最终独立 CLI 文件包含 25 个测试方法，完整发现 201 个方法全部通过，无跳过。这是固定测试的事实报告，供验收角色独立判断，不是客户验收结论；未发布、未安装。

原开发四文件候选为 `c8af7641c83888807ad38939ecfaf0621735b062cf21467e7436f92ffcd7ce8b`，来源 `/tmp/ans-task-candidate-20261019.json`。最终 QA 另取产品、治理和测试输入摘要，排除验收结果、统筹后续文档和本报告，防止自循环。独立验收结论由验收角色作出。

## 环境、版本和输入

- 实测日期为 2026-10-19；macOS 26.6.2 arm64，Python 3.14.7，解释器 `/opt/homebrew/opt/python@3.14/bin/python3.14`；`/usr/local/bin/node --version` 为 `v24.14.0`。Ruby 2.6.10、Psych 3.1.0 用于下述有限替代静态检查。未安装依赖。
- Git HEAD 为 `6a7d4fe125919736c89bcd095baa26d2c9a7d146`；本轮受测修改在工作树中，不能仅用 HEAD 当作候选身份。开发四文件哈希实读与上述 `c8af7641…` 清单逐项相同。
- 201 回归与首次终验使用的非循环输入清单，已逐字节保留为 [final-candidate-before-metadata.json](/tmp/ans-independent-qa-20261019/final-candidate-before-metadata.json)，196 文件，集合摘要 `5f88ad3c8b3ec50d71ad9e9cea21ee93d8ac12699716abe0032fcdf6942358ca`。算法为各相对路径到文件 SHA-256 的映射，按键排序，以 UTF-8 JSON、`ensure_ascii=False`、紧凑分隔符编码，再作 SHA-256。终验后状态/引用收尾的新清单见文末补记。
- 该集合包括产品入口、references、CLI/测试源码、Dashboard、只读 game-engine 源码、当前真实角色卡/MD/YAML边界与有关当前导航、PM 当前方案/架构/法案，以及验收标准；明确排除本 QA 报告、日志、清单本身、验收 result/nav/memo、统筹后续 docs/nav/memo、其他日期版变更历史和本地缓存/私有环境。报告写完后复核同一输入集合；不通过把报告自身摘要写进输入来形成循环。
- 验收标准 v2 SHA-256：`f793e05065c9d15320994cc8afb48baa7629b6bedfdcb8a0a014da66c16b3f6e`；方案最终 SHA-256：`dc6cadf91ebfd84294288171e78194ad93fcf7dbb83e46118dcd2d88b64815d4`。v2 只把 C8 补为策划→PM 技术评审→客户授权→统筹，C1–C7 未改。
- 独立测试文件最终 SHA-256：`b0b542742ef738be380e3365e12a36ede17ed6b823e8905a7cec3a636b196fcf`。各临时项目在自己的目录建立 `.ans/project.json`、角色卡、边界、需求、设计、标准、检查脚本和产物；三阶段为 developer→builder→tester，验收为独立角色。`check.py` 被列入 readSet，验收凭证只在测试进程内和 stdin 请求中使用，持久任务记录仅含摘要；逐命令轨迹将 token/credential 字段脱敏。

## 真实运行与保留的中间结果

以下命令均从仓库根目录执行。测试发现命令前设置 `ANS_QA_LOG_DIR=/tmp/ans-independent-qa-20261019 PYTHONDONTWRITEBYTECODE=1`；`ANS_QA_LOG_DIR` 只让本测试保留隔离夹具与脱敏轨迹。CLI 子进程真实 argv、输入与退出码见对应目录的 `cli-transcript.jsonl`，批准检查的原始日志保存在各夹具 `.ans/runtime/<task>/evidence/`。

| 执行 | 原命令/输入 | 真实结果 | 原日志 |
| --- | --- | --- | --- |
| 首轮独立 CLI | `python3 -m unittest discover -s scripts/tests -p test_role_authority_flow.py -v` | exit 0；20 方法，27.217 秒 | [cli-first.log](/tmp/ans-independent-qa-20261019/cli-first.log) |
| 第二轮独立 CLI | 同上 | exit 0；23 方法，28.501 秒 | [cli-second.log](/tmp/ans-independent-qa-20261019/cli-second.log) |
| 第一轮完整发现 | `python3 -m unittest discover -s scripts/tests -v` | exit 0；199 方法，52.219 秒 | [full-suite.log](/tmp/ans-independent-qa-20261019/full-suite.log) |
| 新增 Git/Dashboard 窄跑 | `python3 -m unittest discover -s scripts/tests -p test_role_authority_flow.py -k dashboard_reads_real -k git_actual_cli -v` | exit 1；2 方法，1 失败，2.952 秒，原因见下文 | [cli-git-dashboard.log](/tmp/ans-independent-qa-20261019/cli-git-dashboard.log) |
| 文案断言修正后窄跑 | 同上一条命令 | exit 0；2 方法，2.630 秒 | [cli-git-dashboard-corrected.log](/tmp/ans-independent-qa-20261019/cli-git-dashboard-corrected.log) |
| 最终完整发现 | `python3 -m unittest discover -s scripts/tests -v` | exit 0；201 方法，53.608 秒，无跳过 | [full-suite-final.log](/tmp/ans-independent-qa-20261019/full-suite-final.log) |
| 隔离 timer | `python3 scripts/validate_task_flow.py --source test/game-engine --output /tmp/ans-independent-qa-20261019/timer-replay --node /usr/local/bin/node` | exit 0；原 mainloop/assembly 检查各 exit 1，修复后 owner/integration 各 exit 0，24 个事件 | [timer.log](/tmp/ans-independent-qa-20261019/timer.log)、[原任务记录](/tmp/ans-independent-qa-20261019/timer-replay/docs/scheduling/timer-pause-resume.md) |

首轮之前的聊天把预估方法数误说为 22；实际初始文件和首轮发现均为 20，没有少跑或删除失败用例。第二轮新增三个方法：标准变化必须新任务、独立测试 readSet 覆盖、unaffected pass 必须由新 accept-plan 的 carriedAcceptances 复核；并在原方法补了 worker token 不能执行 scheduler 命令和实际环境 variablesHash 断言。第二轮没有夹具或产品失败。

为使既有 Git 与 Dashboard 保证也有固定测试自己的真实入口证据，随后新增两方法。Git 窄跑中真实 Git 合并已产生冲突、`status` 已 exit 2 拒读、任务字节不变，但测试还要求错误文字含 `merge conflicts`，实际解析路径返回 `Invalid task event`。仅将这条过窄文案断言改为实际解析错误，保留 Git 非零、CLI 拒绝和拒绝前后字节相同三项行为断言；没有删例、降低权限门禁或修改产品实现。失败夹具保存在 `/tmp/ans-independent-qa-20261019/ans-independent-qa-rub94zf8/`，修正后两方法及最终全套均通过。

最终 201 方法的模块计数见 [full-suite-final-counts.json](/tmp/ans-independent-qa-20261019/full-suite-final-counts.json)：独立 CLI 25、任务工具开发回归 49、`test_dashboard` 14、云端 Dashboard 13、本地 Key 配置 7、versioned sync 20，其余 73。开发者的 49 单测是本上下文实际重跑的回归输入，未被当作独立 CLI 25 方法的替代。最终独立原始项目、真正旧脚本和命令轨迹保存在 [ans-independent-qa-jwqgwlpq](/tmp/ans-independent-qa-20261019/ans-independent-qa-jwqgwlpq)。

## 标准与实际观察

| 标准与方案编号 | 本测试实际核对的结果 | 主要独立方法/附加证据 |
| --- | --- | --- |
| C1；A1/A2/A9 | 缺 acceptanceAuthority、同秘密、请求覆盖身份均 exit 2；init 只返回 schedulerToken，没有验收秘密；scheduler/worker/项目Key/伪造roleId和scope不能 accept-plan/verify；验收凭证不能 dispatch/revise/recover；旧 coordinatorToken 不作别名；无 close/mint/reset 命令；新旧与历史摘要脱敏 | `test_init_*`、`test_credentials_*`、`test_legacy_json_*`、真实任务记录 |
| C2；A3/A8 | 未预检拒绝派发；不能少列必需节点/测试节点/客户来源；同预检重复返回 duplicate 且文档不变；标准改变不能重新接受成同任务；需求/设计修订及删依赖使预检过期；unaffected 不能自行恢复通过，须新预检显式携带复核 | `test_accept_plan_*`、`test_criteria_change_*`、`test_independent_test_readset_*`、两种 revision 方法和 `test_unaffected_*` |
| C3；A4/A5 | 开发→构建→固定测试的真实检查/报告/验收通过后才完成；complete 仍 active/awaiting-verification；pass 释放写预约；missing-evidence 保留预约、阻下游，可同 attempt 补证；needs-work blocked 且保留预约，同 attempt run-check/complete/pass 均拒绝，须 stop 和具体 retryReason 新批次；stop 不完成任务 | `test_real_developer_builder_test_flow_*`、`test_missing_evidence_*`、`test_needs_work_*` |
| C4；A6/A7 | 缺产物、真实 exit 7、真实超时 exit 124、检查修改候选、完成后源码/harness变化、日志丢失/篡改、标准/角色/验收卡/配置变化、stale stateRevision 均拒 pass；失败历史保留；实际 producer/argv/候选/时间/环境/日志摘要可核对；开发检查与外部成功日志不能充当 tester 检查 | `test_failure_history_*`、`test_candidate_output_*`、`test_stale_state_*`、`test_external_logs_*` |
| C4/C5；A6/A8/A10 | `check.env` 覆盖相对 PATH 后，真实命令在项目 cwd 执行；强制 PYTHONDONTWRITEBYTECODE=1 与 variablesHash 一致；解析出的 executable/hash 为实际 probe；二进制改动即使候选不变也失效。祖先日志删掉而直接依赖候选不变，拒下游派发和 pass、当前 taskComplete=false、历史 pass 保留；仍能正式写 missing-evidence/needs-work 负面结论而不放行 | `test_environment_snapshot_*`、两个 `test_ancestor_*`、换机器日志缺失方法 |
| C6；A9 | 真正旧基线六命令全部 exit 2 且拒绝前后 Markdown 字节相同；v2 全历史无 coordinatorTokenHash/tokenHash 别名；真正旧工具建出的 v1 Markdown 可新工具读并兼容 CRLF，但所有写操作拒绝、不释放 active；旧 JSON 可只读且递归脱敏，init 不覆盖；plan.json/state.json 末级外链均拒绝 | `test_real_baseline_*`、`test_old_v1_*`、`test_legacy_json_*`；旧 JSON 范围限制见下文 |
| C7；A10/A11 | 独立真实锁竞争拒写；注入 os.replace 失败时保留原完整文档；recover 只读且不代验收；重复报告幂等/冲突重复拒写，旧批次迟报 exit 3 保留为未采纳；真实 Git 跨任务合并可读、同任务冲突拒读；换副本缺本地日志不能沿用通过；可读区篡改拒 recover；事件 producer 分属 scheduler/acceptance/developer/builder/tester | `test_lock_atomic_*`、`test_git_actual_cli_*`、`test_git_copy_*`、生命周期/旧批次用例；独立 Dashboard 读自己的真实 CLI 三节点记录，issues=[]、全部 verified、记录字节不变 |
| C8；A12 | 本上下文始终固定测试，仅写边界内独占测试与自己的报告/导航/memo；职责来源实际读到规划、PM技术架构、统筹、开发、测试、验收及团队组建各自卡/规则；group 分类且平级，7 项目角色卡均无 groupDuty/组长/组员；新策划产品流程→PM技术评审→客户授权→统筹路线在中英文入口、README、策划规则与实际卡中一致 | 最终静态读取；[9组边界与frontmatter原结果](/tmp/ans-independent-qa-20261019/static-boundaries.json)、[链接原结果](/tmp/ans-independent-qa-20261019/links.json)。其他上下文是否始终守身份需验收核对原交付，不能由程序测试推断 |

## 真正旧工具取得与拒写

测试 `setUpClass` 实际执行以下命令，两个命令均 exit 0；临时文件直接来自 Git blob，未用新程序模拟旧行为，也未在产品目录留下旧入口：

```text
git show 6a7d4fe:scripts/task_ops.py
git show 6a7d4fe:scripts/coordination_store.py
```

旧 `task_ops.py` SHA-256：`90c8644f202913144a5f83e01b7276f14f67240f55519b5c6435775cd21f1017`；旧 `coordination_store.py`：`c7228255969f1c9710cf57abe739d761de91765c4a021ac13543bcc538c63431`。最终取得命令及摘要见 [baseline-manifest.json](/tmp/ans-independent-qa-20261019/ans-independent-qa-jwqgwlpq/baseline-manifest.json)。

用这些脚本真实执行 v2 的 dispatch/verify/ack/run-check/report/stop，各 exit 2、各次记录字节不变；本次首先在旧渲染校验处拒绝，原报错为 `Task record was edited outside task_ops or has merge conflicts`。这不证明旧脚本已经走到认证查询；另外独立断言 v2 的当前和历史机器记录没有 coordinatorTokenHash/tokenHash，避免仅依赖渲染差异。旧脚本对自己的 v1 仍可创建/派发/ack，故本矩阵没有用“无法运行旧程序”假充拒写。

## Dashboard、静态检查与限制

Dashboard 独立部署检查使用 [dashboard_smoke.py](/tmp/ans-independent-qa-20261019/dashboard_smoke.py)，只复制 `dashboard/` 到临时父目录，未复制 `scripts/`、清除 PYTHONPATH。先通过 stdin 为临时 CloudStore 建测试管理员，然后真实运行 `python3 -u -m dashboard.server --cloud-state <隔离state> --port 0 --insecure-local-preview`，仅监听 127.0.0.1；GET `/login` 返回 HTTP 200/777 bytes。启动检查 exit 0；结束主动 terminate，serverStopExit=-15 是清理结果。实际 argv/cwd/URL/响应见 [dashboard-startup-escalated.log](/tmp/ans-independent-qa-20261019/dashboard-startup-escalated.log)。第一次沙箱内执行 exit 1，底层 bind 报 Errno 1 Operation not permitted，原日志 [dashboard-startup.log](/tmp/ans-independent-qa-20261019/dashboard-startup.log) 保留；必要的回环权限升级自动获准后实测通过，不将沙箱限制当产品故障。完整 HTTP 回归使用相同本机测试授权，没有云端发布或新增角色 Key。

静态候选在规范/策划/治理最终冻结后取证：

- `ruby /tmp/ans-independent-qa-20261019/static_boundaries.rb .` exit 0。实际枚举 7 项目角色、仓库 governance 覆盖、内置 built-in-boundary 共 **9 组** MD/YAML，逐行 type/path/purpose 相同、source 正确、YAML notes 在对应 Markdown 中可定位；解析 24 份已有 frontmatter 无语法错误。game-engine 历史 8 张角色卡没有本轮 YAML，不混计为这9组。
- `python3 /tmp/ans-independent-qa-20261019/check_links.py` exit 0。清单中 89 份 Markdown 的589个实际相对目标存在，代码围栏无未闭合；外部网址、标题锚点和代码围栏样例未验证，不声称全网链接或所有锚点成功。
- `rg -n 'groupDuty|组长|组员' 角色卡/*/role-card.md` exit 1、无匹配，表示这7张当前卡未发现该文本；另外阅读了入口与策划/PM/统筹规则，不能单凭关键词扫描证明职责正确。
- `git diff --check` exit 0；仅检查工作树差异空白，不证明行为正确。本上下文实际写入仅为独占测试、本报告及自身 feature-map/memo；其他角色改动保持只读。
- 官方 `python3 /Users/wangzhongren/.codex/skills/.system/skill-creator/scripts/quick_validate.py .` 实际 exit 1，原因是 `ModuleNotFoundError: No module named 'yaml'`，见 [quick-validate.log](/tmp/ans-independent-qa-20261019/quick-validate.log)。Ruby/Psych 只替代 YAML 语法及表格/notes一致性核对，**没有运行或替代官方全部技能策略检查**；此项是环境不可用，既不称产品失败，也不称官方验证通过。

这些结果只针对上述实际候选、环境和已列输入。timer 使用实际 Timer/GameLoop/Engine 与确定性时钟/RAF、场景渲染桩；未测试浏览器初始化、GUI交互、TypeScript 编译、网络部署或任意隐藏机器环境。旧 JSON 路径仅证明读取 plan/state、脱敏、只读与路径安全，不声称其旧 events.jsonl 具有 Markdown 哈希链/渲染一致性校验。原子替换失败通过子进程对 os.replace 故障注入，未模拟真实断电。没有墙钟 TTL、外部客户身份认证或同 OS 恶意操作者防护；未启用真实任务凭证。验证完成后没有继续扩大覆盖或无理由重复全套，必要验收判断交固定验收角色。

## 终验通过后的状态与引用收尾

原独立验收已在[正式结果](../../../验收/docs/acceptance/2026-10-19_role-authority-split-result.md)判 C1–C8 pass。随后 PM 和任务工具在各自边界内收尾当前状态与 QA/验收链接。本固定测试仅执行只读轻量复核及本报告补记；没有修改产品/测试、增覆盖或重新运行 201 回归、timer、Dashboard。原日志和前述测试数量、时间、限制保持历史事实。

仍严格使用同一 **196 个路径**、同一摘要算法，实际检测到以下 **6 个输入**变化，其余 **190 个输入**哈希逐项相同：

| 变动输入 | 当前内容核对 |
| --- | --- |
| `角色卡/任务工具/docs/feature/task-authority.md` | 当前状态为 verified，引用固定测试与独立验收结果；原独立凭证、预检、三结论、证据与历史限制说明保留 |
| `角色卡/任务工具/feature-map.md` | 导航补实际 QA/验收结果，仍说明开发单测不等于固定测试/验收 |
| `角色卡/任务工具/memo.md` | 续接线索引用201回归/25真实CLI与标准v2 pass，保留旧JSON、环境、真实凭证和职责限制 |
| `角色卡/项目管理/docs/architecture.md` | 把待验证状态收尾为实际 QA/验收引用，不把引用写成 PM 自己执行测试；角色路线和现有技术范围保留 |
| `角色卡/项目管理/feature-map.md` | 本轮方案入口补已交付原报告与通过结果 |
| `角色卡/项目管理/memo.md` | 记录当前通过事实及仍由测试/验收处理清单引用，不新增PM实施或验收职责 |

六文件的旧/新 SHA-256 完整映射见 [metadata-changes-before-refresh.json](/tmp/ans-independent-qa-20261019/metadata-changes-before-refresh.json)。旧清单保存的是哈希，不是这六份旧文件的全文；因此此处**不能声称已逐句重建旧新 diff**。可直接核对的证据是精确六文件集合、其余190输入不变、当前语义/链接与原受验行为一致，以及各原固定 owner 报告其修改限状态/引用。任务工具日期版 change 报告也仅引用真实原结果，已只读核对，但它原本不在196输入集合中，继续排除。

四源码逐项仍等于 `/tmp/ans-task-candidate-20261019.json` 中原值，四文件聚合仍为 `c8af7641c83888807ad38939ecfaf0621735b062cf21467e7436f92ffcd7ce8b`；独立测试及其他测试源码、criteria、方案、契约/指南、实际角色卡与MD/YAML边界均无输入哈希变化。测试结果依然指向原执行候选；本次只是元数据收尾检查，不把旧测试冒称重新运行。

轻量复核结果：`check_links.py` exit 0，仍为89份 Markdown，当前 **601** 个相对目标存在、无未闭合围栏（首次589结果另存 `links-before-metadata.json`）；`static_boundaries.rb .` exit 0，9组边界表格/notes及24份 frontmatter 解析通过；对上述六文件及被排除 change 的 `git diff --check -- <七路径>` exit 0。这是当前文件/链接与必要空白检查，不是逐句旧新差异证明，也未验证外部网址或标题锚点。原结果分别见 [link-summary-metadata.json](/tmp/ans-independent-qa-20261019/link-summary-metadata.json)、[static-boundaries-metadata.json](/tmp/ans-independent-qa-20261019/static-boundaries-metadata.json)、[diff-check-metadata.log](/tmp/ans-independent-qa-20261019/diff-check-metadata.log)。

- 保留旧候选摘要：`5f88ad3c8b3ec50d71ad9e9cea21ee93d8ac12699716abe0032fcdf6942358ca`；[旧清单副本](/tmp/ans-independent-qa-20261019/final-candidate-before-metadata.json) 文件 SHA-256 为 `483b744b31f1770a0dcbf24a3c4cb977ac6168cfa9e5cd6ef03f66106313d7f1`。
- 最新元数据候选摘要：`e2c3fb2bfde40d246c1bd011af45a552b69a205b66fefc20c9c4468e82c31712`；[最新同集合清单](/tmp/ans-independent-qa-20261019/final-candidate.json)文件 SHA-256 为 `5cde407f71794678d98afe1df8cac350b6d072b31d4e7c6a887235b38c152944`。
- 本 QA 报告/日志/清单本身、验收 result/nav/memo、统筹后续记录继续排除，故本补记与验收随后补引用不造成摘要自循环。最新清单供原验收只读补充引用；未重新作客户验收决定。
