# 工作流缺口修复：独立验收结果

日期：2026-10-20；作者：源仓库固定独立【验收 / acceptance】上下文。结论：**通过；C1 的 WF-01 至 WF-06 全部满足。**

角色交接现在有真实只读预检，已获准的本角色精确工作文档可以进入受限任务，新检查按原执行环境核对有效性。当前候选完成源独立回归、库存隔离两节点真实流程与旧库存最终保全；不同查询者 PATH 未使同一有效结果误失效。实际程序、声明配置、输入或证据变化的失效保护仍在，旧 hash-only 证据没有补造或追认。

本结论依据客户真实确认“确认，按方案完成修复和验证”，绑定 P1、D1-final-1、C1、QA-T1-draft-1 和 D1 第6／7节范围。本人读取当前源码差异、实际角色边界、原开发／固定测试日志、隔离独立验收与最终保全记录后独立判断，没有代跑测试、改标准、操作隔离凭证或改任务状态。源项目没有另建任务；本报告是源独立成果判断，不冒充隔离项目的工具 verify。

## 标准、方案及当前候选

源基线 HEAD 为 `d95d0068d219c2a8870d585364af2b34999bec3c`；当前为工作区候选，没有虚构新提交号。治理、策划、PM、工具、规范和测试的各自改动按原所有者和有效 Section 1 分开核对，没有将既有工作区输入计为本验收角色产物。

| 批准输入／独立证据 | 版本或本次实读 SHA-256 |
| --- | --- |
| [P1](../../../策划/docs/design/2026-10-20_design_workflow-friction-product.md) | P1；`a14d8a82b0a0b1462fc0a85eb5b9394cb30441eff9f3565f16321482213ba25c` |
| [D1](../../../项目管理/docs/design/2026-10-20_design_workflow-fixes.md) | D1-final-1；`eeae25a2ee4fe0891ccd8972b24591cb633c8e05414deef5cf8b23c9cddcdc87` |
| [本轮标准](2026-10-20_workflow-fixes-criteria.md) | C1；`69119468244f97eb7e399cfc779f03f5f23850609860e326d28ae3fde112b438` |
| [固定测试设计](../../../测试/docs/design/2026-10-20_design_workflow-fixes-validation.md) | QA-T1-draft-1；`c048526701b3ecbb596247533cbdc9a3b12cb9d4382a0f97d8544df1ee160c0c` |
| [源QA最终原报告](../../../测试/docs/change/2026-10-20_change_workflow-fixes-validation.md) | `93902a1c3322ae1fcdd60f90a7441903f9217baf39e42943473c5a55764257df` |
| [隔离项目独立验收结果](../../../../../ans-full-trial-2026-10-19-bqf0vjof/validation/workflow-fixes-2026-10-20/角色卡/acceptance/docs/change/2026-10-20_change_workflow-fixes-result.md) | `7f3b5481fccaec841de1a46a336cc5167858428f1d16cc3334b1c26e6bff7477` |

源QA报告最后仅补真实独立验收、普通状态消费和根保全事实；程序、测试、四批准输入与根内候选没有改变。引用最终实际报告，不回改隔离报告当时读到的历史摘要，也不建立互相更新摘要的循环。

源程序／测试候选逐文件实读如下；两工具副本与对应源字节一致：

| 路径 | SHA-256 |
| --- | --- |
| `scripts/task_ops.py` | `2919757a34d8c725c1f3fb1bafd0444003d40824e431e99cc4bbf4e44e0a4236` |
| `scripts/coordination_store.py`（未改） | `09aee0153d26f0510e77eaaa284a48549a3bfc8d96fdc23ce4a53df4b6af7fd4` |
| `scripts/tests/test_task_ops.py` | `9b1d1cb014afe8bf922cd9af57439fd33582695cf6a675ebb29cd7d0f1220235` |
| `scripts/tests/test_role_authority_flow.py` | `18a8e78cb8de38a0f14daa77fa8a54a38703daa15a52f83d66079e89ebb9862a` |

规范与当前功能说明同样按实际交付版本核对。最后的“治理提供登记／权限，已接受统筹准备配置，再预检后开展其余工作”措辞澄清符合原批准职责和当前入口，没有改变程序、测试或冻结的执行输入，不要求重跑程序套件。

| 规范／所有者文档路径 | SHA-256 |
| --- | --- |
| `SKILL.md` | `5553fd16c10d11b323793e0ca29a71073cbf5f9cef38a6422903f0d4248afa0a` |
| `SKILL.zh.md` | `72905da6d5728009e43dd51f7c2a39dd9157ec01b97b3711ae55a4258a863713` |
| `references/bootstrap-workflow.md` | `442f5fb8719de9332a18a8c878ad8a1577a0029e60e16107e2e09bd8261543ce` |
| `references/role-card.md` | `0329efb39096634328006cfc0c7781b1f4756edff0a516ab52748dfaaf761781` |
| `references/module-boundary.md` | `4f9093caf672840951af8d39012ebf50a51f35c01218141662d2d4a0a2a74752` |
| `references/task-operations.md` | `b9c47d1d30a5af470a758478a05702dda7b3778aba6b7873932bf848cb447f9b` |
| `references/team-formation.md` | `f5889406678c4e880068f4839b6424a07fc0eacc435db9a9df07c99df1ed370c` |
| `references/api-spec.md` | `a91af5963764929d07ead28a25830347c16707a36470adb82fbc72c8f47a1d04` |
| `references/scheduler.md` | `368826797532bc1c9e20e870773a7285534a8155bc3adc72e725c6d119d148c6` |
| `角色卡/任务工具/docs/feature/task-authority.md` | `5a14f29cf28c59f5075ef8a780672c2ba259eecf3bf791fad557ca2cf3fe4fe0` |
| `角色卡/任务工具/docs/fix/2026-10-20_fix_workflow-gaps.md` | `9b0eff81c42703417ab5b68a3af74d33028179c540d6d5fd85091442f89b3932` |
| `角色卡/技能规范/docs/feature/role-authority-split.md` | `fc00090eab5ec41db8b5d4c43d85f8113484243012bcf6698e7432f868ad4500` |
| `角色卡/技能规范/docs/fix/2026-10-20_fix_workflow-gaps.md` | `2badb3d2c31dd5cdcbbbc78df756c61783a539f1ba4d3952597e8bb2e200d0c0` |

## WF-01 至 WF-06 的独立判断

| 标准 | 结论 | 当前实现与实际证据 |
| --- | --- | --- |
| WF-01 初始化／交接检漏 | 通过 | `preflight-role` 在 Store 前分支；共用解析只取实际 Section 1 路径列，不将用途文字当授权。完整登记的 core、API适用声明及当前 docs 漏权具体返回；权限与内容存在性分开。源CLI原断言／输出证明无task预检前后树不变、init缺权不建任务；既有宽根、重叠、穿越／symlink保护回归通过。规范将真实预检接入配置准备与交接路由，库存两项有界AST本轮重跑，没有冒称新通用架构扫描器。 |
| WF-02 精确自身文档与保护 | 通过 | 从登记 card／boundary 的共同父目录定角色根，有限根工作文件及自身有界docs与Section 1／writeFiles／writeSet取交集；完整保护集合及目录相交检查先于文件入选。源真实CLI覆盖roleId不同目录合法正例、自定义治理路径、非执行角色／验收治理、MD/YAML/changelog、跨角色、状态、目录、非规范与symlink拒绝。真实Provider和test各只有一份自有工作文档写集合，没有借目录扩权。 |
| WF-03 执行环境与查询者分离 | 通过 | 当前 `run-check` 一次捕获实际env并固定解析后的真实程序执行；新证据v2只引用工具生成私密最少快照。源CLI普通不同PATH的status／verify／依赖消费通过；隔离真实跨角色验收后两个不同PATH普通status仍为revision19、两节点有效、taskComplete=true，任务字节及九次check历史不变。九份实际快照摘要匹配，文件0600、父目录0700，没有公开环境原值。 |
| WF-04 真实变化失效／legacy | 通过 | 已读源码的版本分流、快照形状／摘要、程序路径／内容、声明配置、候选、日志与祖先门禁，以及源原CLI负例断言／日志。v2缺坏快照与未知版本不回退；真实执行对象、readSet资源／配置、源码、日志／报告、执行中变化与失败缺证不放行。只有无版本字段走旧判定。active补证和verified须新任务的既有状态机保持，没有新增通用report绑定。真实d95d006生成旧证据的fixture及原库存93只读兼容均未补造快照。 |
| WF-05 库存隔离真实流程及保全 | 通过 | 字节复制B落实，初始94输入与原件一致；test三治理差额单独接受，第二基线94输入加两工具为96，manifest冻结。独立Provider／test本人ack、check、report及隔离acceptance本人verify形成19事件；test报告先固定后八项正式检查，六组60方法与两辅助检查均同候选退出0。外部最终保全核旧188文件集合／字节变化0、新根外增删0，旧任务93及失败历史保留；未以根内manifest冒称父根实时保全。 |
| WF-06 版本、职责与原始证据 | 通过 | 程序／开发测试／独立CLI各在原owner精确范围；规范九文件及两owner当前说明与实码一致。源69／40／236日志、两任务候选与九原日志摘要、独立verify、最终源QA及根保全可互核。开发、源QA、隔离Provider／test／验收和源验收是不同固定角色；fixture凭证未冒充真实协作，本人未持隔离秘密。真实失败保留，没有删断言或改旧证据使通过。 |

本次判断采用 C1 既定阶段语义：Provider 的阶段通过只放行独立测试。直到 `document-check` 实际检查、隔离独立验收及源外部保全齐备，才给本源成果全部通过；没有用早先Provider pass或单个taskComplete替代完整目标。

## 原始执行证据与真实失败

[开发原修复报告](../../../任务工具/docs/fix/2026-10-20_fix_workflow-gaps.md)记录开发69项；[源QA最终原报告](../../../测试/docs/change/2026-10-20_change_workflow-fixes-validation.md)记录独立CLI40和完整236。本人核当前四输入摘要与两份最终summary一致、`inputsUnchanged=true`，原日志退出0；69和40都包含于236，不相加，也不与库存60混称同一套测试。

| 原检查 | 实际结果 | 原始日志与摘要 |
| --- | --- | --- |
| 开发 `test_task_ops.py` | 69项，7.978秒，OK | [原日志](/tmp/ans-workflow-task-unit-final-20261020.log)；`8384c09b2455f34833084c32a7a4603ebcf84357e48c5a64683d9e273957bd89` |
| 独立 `test_role_authority_flow.py` | 40项，48.358秒，OK | [原日志](/private/tmp/ans-workflow-fixes-source-qa-20261020/independent-cli-final.log)；`6ba7aede20425af866d72ec0c499197dd94ee2d95a30579aa006cc0248d1149a` |
| 完整 `scripts/tests` | 236项，71.216秒，OK | [原日志](/private/tmp/ans-workflow-fixes-source-qa-20261020/full-suite-loopback-final.log)；`4a961f66cacd4fe89947ca64ba5c4407593962b337623f44d825e899cea8c5ea` |

上述运行环境为macOS arm64、Python3.14.7。原25个独立CLI方法体及断言与基线AST相同；新增15个方法覆盖T01–T11。开发首轮格式迁移预期和第二轮精确文档fixture错误、QA首轮拒绝文案断言错误、完整发现首轮10个本机HTTP沙箱权限ERROR都留有原日志。QA文案修正仍要求非法路径拒绝且任务字节不变；允许本机临时端口后同一候选完整236重跑通过，没有skip或删除旧安全断言。

## 隔离项目的最终事实

唯一新根为 `ans-full-trial-2026-10-19-bqf0vjof/validation/workflow-fixes-2026-10-20/`。[任务原记录](../../../../../ans-full-trial-2026-10-19-bqf0vjof/validation/workflow-fixes-2026-10-20/docs/scheduling/workflow-fixes-isolated-20261020.md) SHA-256为 `ed04991f6a3e753b8d32feb3d6ad74adc4483e8e22568c41118a26b031b2dcf2`。实读19事件：accept-plan为2，Provider ack/check/report后独立verify为7，test ack/八check/report后独立verify为19。两个节点均verified且inactive，逐项WF-01—WF-06均由acceptance给pass。

| 节点 | attempt／当前候选 | 正式检查 |
| --- | --- | --- |
| document／provider-json | document-1；`4cf0e21a600ed2141da258242a7632eb096a557bdd8cc0a04bb4a1f64acf2dd9` | 1项document-content |
| document-check／test | document-check-1；`df0dd19736ee1578dde6951d37e6398329bcbb839edeb12ef394902df1bc6ef0` | regression-model7、provider7、service10、cli21、assembly6、unit-integration9，加document-manifest及fixture-executable |

本人读取九原日志、逐条核实producer／attempt、exitCode=0、environmentVersion=2、候选相符、candidateUnchanged／environmentUnchanged=true、日志与快照字节摘要相符。六组Ran数为7/7/10/21/6/9，合计60；两个辅助检查不是额外库存方法。八份test原日志的完整路径／摘要由[隔离独立结果](../../../../../ans-full-trial-2026-10-19-bqf0vjof/validation/workflow-fixes-2026-10-20/角色卡/acceptance/docs/change/2026-10-20_change_workflow-fixes-result.md)逐项列明，源QA同样已读取。原业务调用均在副本root，未导入父库存源码。

test方法报告SHA-256 `6ef8e3fd65a41a6faea8913d33ae9b03c8d73b013aaf3489be41b485aa311d41`，八正式检查后未回写。readSet为103／104，后者覆盖前者读写并集；两源工具、根内本轮批准计划／标准、原20文件、实际夹具和manifest都被精确绑定。manifest SHA-256 `60fe4b772d938baadec96cf057805190a9972be71ccfd907931fb7f7cc273beb`，复制基线与治理补权后执行基线没有混用。

不同PATH查询的当前有效性来自隔离acceptance本人、sourceQA及根的真实普通status消费，不是仅从Markdown“提交时任务完成”推断。[源QA最终状态摘要](/private/tmp/ans-workflow-fixes-source-qa-20261020/isolated-final-status-summary.json)与隔离独立报告记录revision19、两节点currentAcceptanceValid=true、taskComplete=true；任务文件前后同上述摘要，checkHistory仍Provider1＋test8，没有为查询重新run-check或回填执行环境。

## 旧库存保全、限制及后续

[源QA最终外部保全](/private/tmp/ans-workflow-fixes-source-qa-20261020/original-preservation-after-isolated.json)和[根独立保全收据](/private/tmp/ans-workflow-fixes-20261020-pfkr9dbm/preservation-final-root.json)均证明旧188文件集合及字节变化0、唯一新根外新增0／删除0。覆盖旧批准输入、原20交付、角色输入、旧任务、runtime日志／失败历史与原私密observed快照；没有覆盖或清理历史。根内manifest检查只证明根内载荷，外部保全由任务外只读比较提供。

[旧任务只读兼容记录](/private/tmp/ans-workflow-fixes-source-qa-20261020/legacy-status-final-summary.json)表明新源工具在既有真实跟踪环境中读取旧inventory-full-trial仍为revision93、六节点有效、taskComplete=true；旧任务前后SHA-256同为 `5628337d3414bd031ab2721be69eff3df1a98895bb59337b526220b399e1b346`。这证明legacy兼容，不能拿它冒充v2不同普通PATH的新证据；旧证据无快照补造或重新签认。

没有未解决的C1必需项。完成范围仍是已批准三项修复及受限验证：预检不自动发现未登记角色或理解职责，不是Provider／Service通用结构扫描器；未声明环境／外部动态依赖不在自动覆盖内；不承诺OS用户级隔离、跨机器证据复用或快照恢复。程序／配置／相关输入／证据今后变化仍须按原规则复核。

没有push、install、public镜像更新、发布、旧任务迁移或额外硬化。本验收通过不授权这些操作。所有者后续仅同步链接／状态等元数据时，保留当前程序、测试与冻结执行证据；若实质输入改变，再按影响范围取得新证据。
