# 角色职责拆分：独立验收结果

2026-10-19；固定独立【验收】上下文。结论：**通过（pass）**。当前候选满足标准 v2 的 C1–C8；没有需返工或补证的必需项。本结论来自实际差异、当前产物和原始证据核对，不是统筹转述或开发者自验收，也不代表发布、安装或真实项目任务已经启用。

## 本次判断对应哪个版本

- [标准 v2](2026-10-19_role-authority-split-criteria.md)，SHA-256 `f793e05065c9d15320994cc8afb48baa7629b6bedfdcb8a0a014da66c16b3f6e`；[方案](../../../项目管理/docs/design/2026-10-19_design_role-authority-split.md)，SHA-256 `dc6cadf91ebfd84294288171e78194ad93fcf7dbb83e46118dcd2d88b64815d4`。v1→v2 的用户新增策划决定与旧/新方案摘要仍保留在标准中，C1–C7 未改。
- Git 基线 `6a7d4fe125919736c89bcd095baa26d2c9a7d146`；受验对象是工作树实际修改，不能用 HEAD 代替候选。开发四文件集合摘要 `c8af7641c83888807ad38939ecfaf0621735b062cf21467e7436f92ffcd7ce8b`。
- [首次终验输入清单（原件归档）](/tmp/ans-independent-qa-20261019/final-candidate-before-metadata.json)：196 文件，集合摘要 `5f88ad3c8b3ec50d71ad9e9cea21ee93d8ac12699716abe0032fcdf6942358ca`；清单文件自身 SHA-256 `483b744b31f1770a0dcbf24a3c4cb977ac6168cfa9e5cd6ef03f66106313d7f1`。首次验收独立重算全部文件及规范 JSON 映射摘要，与清单一致，未发现变更。终验后的当前说明收尾及新清单见文末补记，原清单只改为指向逐字保留的归档路径。
- 清单覆盖产品入口/规范、程序和测试、Dashboard、相关只读 game-engine 输入、实际角色治理及当前说明、PM 方案/架构/法案和标准 v2；排除 QA 报告/日志/清单本身、验收结果/导航/memo、统筹后续说明和日期版历史等，避免自循环。算法和逐文件摘要见清单；新程序、规则或相关输入变化会使受影响判断需要重新核对。

## 核对的原证据

[开发原报告](../../../任务工具/docs/change/2026-10-19_change_task-authority.md)记录其49项单测与隔离 timer；验收读取了[开发单测原日志](/tmp/ans-task-unit-final-20261019.log)、[四文件原摘要](/tmp/ans-task-candidate-20261019.json)，没有把开发自测当成独立 QA。

[固定测试正式原报告](../../../测试/docs/change/2026-10-19_change_role-authority-split-validation.md)首次终验版本 SHA-256 为 `4259af8b880d229e25b6fc38307508b3c429649551a32ef2ac2ee66e60a16ff8`（追加收尾补记后的版本见文末）。本验收实读其报告、独占 CLI 测试源码、最终逐命令轨迹及下面的原始结果：

| 证据 | 实际观察与用途 |
| --- | --- |
| [最终全套日志](/tmp/ans-independent-qa-20261019/full-suite-final.log)、[计数](/tmp/ans-independent-qa-20261019/full-suite-final-counts.json) | 固定测试真实发现201项，53.608秒，exit 0、无跳过；其中独立 CLI 25、开发回归49。CLI 由独立测试子进程直接调用真实入口，不用开发 helper。 |
| [最终 CLI 夹具与轨迹](/tmp/ans-independent-qa-20261019/ans-independent-qa-jwqgwlpq)、[真正旧基线清单](/tmp/ans-independent-qa-20261019/ans-independent-qa-jwqgwlpq/baseline-manifest.json) | 负面请求的退出码、拒写前后字节、实际身份生产者、检查日志均可定位。验收另以 git show 复核两份旧脚本及临时文件摘要。 |
| [独立 timer 汇总](/tmp/ans-independent-qa-20261019/timer-replay/docs/validation-summary.json) | 原检查各exit 1，修复后开发/集成各exit 0，24事件；迟报、过早派发和工作者自验收均实际拒绝，全部节点当前有效通过。 |
| [Dashboard 独立启动](/tmp/ans-independent-qa-20261019/dashboard-startup-escalated.log) | 仅复制 dashboard/、无 scripts/；管理员创建exit 0，真实云端模式启动，GET /login 为 HTTP 200。主动停止为清理动作；本机沙箱首次 bind 失败原日志保留。 |
| [边界/语法原结果](/tmp/ans-independent-qa-20261019/static-boundaries.json)、[链接原结果](/tmp/ans-independent-qa-20261019/links.json) | 9对 MD/YAML 范围/notes一致，24份frontmatter语法可解析；89份Markdown的589个相对目标存在。验收另读实际边界、入口、策划/PM/统筹规则，核对职责语义与文件归属。 |

原测试环境为 macOS 26.6.2 arm64、Python 3.14.7、Node v24.14.0；具体命令、cwd、输入、退出码和环境由原报告及日志记录。这里仅执行了只读差异/来源/摘要核对，没有代跑完整 QA、timer 或 Dashboard。

## C1–C8 逐项结论

| 标准 | 结论 | 独立判断依据 |
| --- | --- | --- |
| C1 凭证分开 | pass | [task_ops](../../../../scripts/task_ops.py) 的 authority_valid、credential 与 init/命令路由分别约束验收身份、摘要和秘密，不生成验收明文、拒同秘密/覆盖，调度和工作者无验收入口，状态递归脱敏。独立 init/credentials/legacy 用例实测身份互用、伪造roleId/scope及项目Key均拒绝；真实秘密来源属于可信操作端，未用角色名冒充客户认证。 |
| C2 前期门禁 | pass | accepted_plan 固定实际标准/计划/角色/文档，dispatch 先核对；accept-plan 要求全部必需节点和独立测试覆盖。独立用例实际拒绝未预检/缺节点/缺来源，验证修订和删依赖后过期，以及非影响结果须新预检明确复核才能沿用。 |
| C3 三种结论 | pass | report/verify/stop/dispatch 与独立生命周期、missing-evidence、needs-work 用例一致：complete不释放，pass才verified；缺证同批次补证，返工须停止与retryReason新批次，旧批次反馈不被采纳。完整三阶段走完才taskComplete，调度没有close接口。 |
| C4 当前真实证据 | pass | run-check 无shell运行配置argv，认证assignment提供生产者，记录真实环境、时间、候选、退出码和日志；evidence_valid及验收逐项引用绑定当前报告。真实失败7、超时124、改候选/脚本/日志/角色/规则、stale stateRevision均拒pass；开发日志和外部成功文件不能冒充tester检查，失败历史保留。 |
| C5 祖先和环境失效 | pass | valid_pass 递归核对前置验收、检查与日志，verify/dispatch/status共用；candidate覆盖节点、依赖和测试覆盖的write/read集合。祖先日志删掉、直接依赖候选不变时，原轨迹仍拒下游派发/pass且当前完成false，历史pass保留，并可写负面结论。相对PATH/cwd/合并env与实际进程一致，二进制变更失效；修订传递失效与新预检复核均有独立证据。 |
| C6 新旧隔离 | pass | Store对正常v1沿用原渲染核对，旧JSON只读加载且末级外链也检查；新工具拒绝旧任务写入，不释放旧active。v2当前及历史没有旧认证字段/别名。验收核对的真旧6a7d4fe脚本六命令均exit 2，原测试逐次断言字节不变；旧脚本还实际创建/派发/ack自己的v1，排除“旧程序不能运行”的假证明。 |
| C7 记录与回归 | pass | [Store](../../../../scripts/coordination_store.py)继续锁内验证和原子单写，可读区与机器事件同源，提交派生完成并注明生产者。独立锁竞争/原子故障/重复迟报/recover/换副本缺日志，以及实际Git跨任务合并和同任务冲突均有原证据。Dashboard读取自己的真实CLI记录无issues且不改字节；全套与独立目录启动满足TASK-01/DEPLOY-01，未改云端Key模型。 |
| C8 实际职责与策划路由 | pass | 本轮原PM给技术方案；统筹交接记录协调与逐角色反馈；任务工具交自身实现/单测，固定测试写独占测试和原报告，本上下文独立定义标准并核对成果。7张项目角色卡与团队组建治理覆盖独立，范围无本轮业务/报告重叠；9对边界一致。策划自己的导航/memo、规划规则及中英文入口已落地，后续需求按策划产品方案→PM技术设计/评审→客户授权→统筹实施；本轮历史方案没有改归策划。group仅分类，旧组长页仅保留历史说明，不再授予组长/组员派发权，满足DOC-01。 |

## 保留的失败与判断限制

固定测试首轮实际20项、第二轮新增后23项、第一轮完整199项；后加Git/Dashboard两项，曾有一项错误文案断言失败。原失败中真实Git冲突、CLI exit 2、记录字节不变均已成立；修正只对齐实际 `Invalid task event` 文案，保留拒读/不改写契约，随后2/2及最终201项通过。[原失败日志](/tmp/ans-independent-qa-20261019/cli-git-dashboard.log)仍在，未用最终成功隐藏它。

[官方quick_validate原日志](/tmp/ans-independent-qa-20261019/quick-validate.log)为exit 1，缺PyYAML。Ruby/Psych替代仅证明YAML语法和MD/YAML表格/notes一致，不代表官方技能策略检查通过；链接检查也不覆盖外站和全部锚点。标准要求的实际边界、文档、行为和回归已有对应证据，因此该已披露环境限制不构成本次必需项缺证。

timer不是浏览器初始化、GUI或TypeScript编译证据；旧JSON的plan/state读取不证明旧events.jsonl有Markdown哈希链校验；原子故障注入不代表真实断电试验。结论不认证客户本人，不证明同OS操作者无法改配置，也不自动发现未声明依赖；没有新增TTL、组模型、云端角色Key或身份服务。

本次验收只写自己的报告/导航/memo，未修改程序、标准、他人报告或任务状态，未生成或交付真实项目验收秘密。后续仅更新当前说明中的完成状态/结果链接，由原所有者修改后核对精确文档差异与新清单；若源码、检查、配置或契约发生变化，应重取实际影响范围的证据，不能直接沿用本结论。

## 终验后纯状态/链接收尾复核

2026-10-19，原项目管理仅收尾自己的架构/导航/memo，任务工具仅收尾自己的功能说明/导航/memo及日期版变更记录，引用已经发生的 QA 与验收事实。本验收已只读这些当前内容，原行为说明、开发历史及限制保留，没有新增技术要求或权限。

固定测试使用原来同一196路径集合，确认仅上述6个当前说明输入变化，其余190个输入逐项不变；全部程序、开发与独立测试源码、标准v2、方案、法案、契约和角色边界均未变。任务工具日期版 change 原本排除于集合，仍排除；四源码聚合继续为 `c8af7641c83888807ad38939ecfaf0621735b062cf21467e7436f92ffcd7ce8b`。精确旧/新文件摘要见[六输入变更清单](/tmp/ans-independent-qa-20261019/metadata-changes-before-refresh.json)，核对汇总见[轻量复核原记录](/tmp/ans-independent-qa-20261019/metadata-refresh-summary.json)。旧清单只存哈希，没有六份旧文档全文；不声称已重建逐句旧新diff。本判断结合精确变化集合、其余输入未变、当前语义/链接和原固定所有者的收尾交付。

- 当前[同集合最终清单](/tmp/ans-independent-qa-20261019/final-candidate.json)集合摘要：`e2c3fb2bfde40d246c1bd011af45a552b69a205b66fefc20c9c4468e82c31712`；清单文件 SHA-256：`5cde407f71794678d98afe1df8cac350b6d072b31d4e7c6a887235b38c152944`。
- 固定测试报告补记后的当前 SHA-256：`25eff1aaedfa050312619588c4fbbc6e839034fef6174db5eb96679c8853dd45`。报告记录当前89份Markdown/601个相对目标、9对边界/24份frontmatter及限定7路径空白检查均exit 0；检查范围限制继续适用。
- 首次 `5f88ad…` 候选、原清单 `483b744b…` 和首次QA报告 `4259af…` 来源在上文保留，未静默覆盖。QA报告/日志/清单、本验收result/nav/memo和统筹后续说明继续排除，补引用不形成摘要自循环。

这是纯文档状态与来源更新，未重新运行201项或其他程序测试，不把旧执行结果写成新运行。原201项/25独立CLI证据和C1–C8判断继续适用，**维持通过（pass）**；没有新增返工项、必需缺证项或待客户决定事项。
