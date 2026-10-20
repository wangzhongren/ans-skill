---
id: workflow-fixes-validation-change
type: change
title: 工作文档与实际执行环境修复的独立测试记录
created: "2026-10-20"
updated: "2026-10-20"
timezone: Asia/Shanghai
status: tested
related: [workflow-fixes-validation-t1, workflow-fixes-d1, task-authority]
events:
  - date: "2026-10-20"
    kind: changed
    summary: 客户确认后新增15个独立CLI方法并准备94份字节复制载荷；首轮原失败保留，正在复测
  - date: "2026-10-20"
    kind: changed
    summary: 源独立CLI40项及完整发现236项通过；保留文案断言失败和沙箱端口错误，冻结96份根内准备输入及manifest
  - date: "2026-10-20"
    kind: changed
    summary: 只读核对隔离test本人八份真实原日志及60方法、同候选和固定方法报告；当前待独立验收最终结论
  - date: "2026-10-20"
    kind: changed
    summary: 引用隔离独立验收本人最终通过及不同PATH只读结果；源QA实读revision19两节点有效，旧188文件及旧93兼容保全完成
---

# 工作文档与实际执行环境修复的独立测试记录

固定源【测试 / qa】依据客户“确认，按方案完成修复和验证”的实施授权、[D1-final-1](../../../项目管理/docs/design/2026-10-20_design_workflow-fixes.md)、[C1](../../../验收/docs/acceptance/2026-10-20_workflow-fixes-criteria.md)和[QA-T1](../design/2026-10-20_design_workflow-fixes-validation.md)实施。本角色只修改原独立测试文件及本报告，并按独立复制例外准备清单载荷；不兼副本Provider/test/验收，不改生产程序或治理内容。

**源侧实际结果：独立CLI40项和完整发现236项全部通过，同一工具/测试候选前后未变。** 隔离Provider和test本人完成真实文档节点及八项正式检查，其中六组库存回归实际60方法通过；独立acceptance本人已最终verify通过，源QA只读确认revision19、两节点当前有效、taskComplete=true。旧188文件保全无变化，旧任务在原观察环境仍revision93有效。初始文案断言失败与沙箱端口错误均保留。本报告提供测试和保全事实，源修复整体最终验收由源独立验收判断。

## 候选及实际改动

基线为源`main d95d0068d219c2a8870d585364af2b34999bec3c`，工作区包含各原owner已获准改动。工具owner交付的稳定候选：

| 文件 | SHA-256 |
| --- | --- |
| scripts/task_ops.py | `2919757a34d8c725c1f3fb1bafd0444003d40824e431e99cc4bbf4e44e0a4236` |
| scripts/coordination_store.py（本轮未改） | `09aee0153d26f0510e77eaaa284a48549a3bfc8d96fdc23ce4a53df4b6af7fd4` |
| scripts/tests/test_role_authority_flow.py（QA最终候选） | `18a8e78cb8de38a0f14daa77fa8a54a38703daa15a52f83d66079e89ebb9862a` |
| scripts/tests/test_task_ops.py（工具owner候选，QA只读） | `9b1d1cb014afe8bf922cd9af57439fd33582695cf6a675ebb29cd7d0f1220235` |

本角色修改[scripts/tests/test_role_authority_flow.py](../../../../scripts/tests/test_role_authority_flow.py)：原25方法保留，新增15方法和独立fixture准备/只读预检helper，总40方法。实际AST比较确认原25方法体及断言与d95d006完全相同。仍通过真实子进程CLI操作，不导入生产operate或开发测试helper。

新覆盖包括：无task预检前后完整文件树相同；必要core/API漏权与内容未创建的区别；全角色登记/绑定、roleId与自定义中英文实际根不同；合法精确文档本人写入后完整CLI流程；未选入writeFiles的重叠及状态许可；标准和自定义治理文件、跨角色、目录、非规范路径及symlink拒绝；不同查询者PATH的status/verify/依赖派发/完成有效；v2私密快照权限、absent键、未跟踪变量不采集及公共结果不泄露原值；快照丢失/改动不回退；readSet资源/配置、实际执行文件目标/内容/途中变化失效；快照写入失败不能生成有效通过；真正d95d006工具产生的hash-only证据继续旧判定且不补快照。

自动化fixture中的scheduler/worker/acceptance凭证及批准来源明确为fixture，仅证明CLI门禁。真实独立角色工作和副本验收仍另取原证据。

## 实际运行与首轮失败

证据目录为`/private/tmp/ans-workflow-fixes-source-qa-20261020/`（0700），原测试日志0600；私密快照不打印、不写入本报告。实际环境为macOS-26.6.2-arm64-arm-64bit-Mach-O、Python3.14.7。调用解释器`/opt/homebrew/opt/python@3.14/bin/python3.14`解析至`/opt/homebrew/Cellar/python@3.14/3.14.7/Frameworks/Python.framework/Versions/3.14/bin/python3.14`，文件SHA-256 `87d4df53fd91304be5bac391fb204643c36b7df2023c04a0953bcbc7d4fdf634`。命令在源仓库cwd执行，显式ANS_QA_LOG_DIR及PYTHONDONTWRITEBYTECODE=1；候选/原输出摘要见各summary.json。

| 检查 | 实际命令 | 结果 | 原始证据 |
| --- | --- | --- | --- |
| 新测试静态语法/方法清点 | ast.parse本测试文件，不执行测试 | 可解析；40方法。这不是动态测试通过 | 2026-10-20 QA实际命令输出 |
| 首轮独立CLI | `python3 -m unittest discover -s scripts/tests -p test_role_authority_flow.py -v` | 实际40方法，44.521秒，退出1：39通过、1失败 | [首轮原日志](/private/tmp/ans-workflow-fixes-source-qa-20261020/independent-cli-first.log)、[原摘要](/private/tmp/ans-workflow-fixes-source-qa-20261020/independent-cli-first-summary.json) |
| 修正后独立CLI | 同上 | 40方法全部通过，48.358秒，退出0；三个工具/QA输入摘要未变 | [复测原日志](/private/tmp/ans-workflow-fixes-source-qa-20261020/independent-cli-final.log)、[复测摘要](/private/tmp/ans-workflow-fixes-source-qa-20261020/independent-cli-final-summary.json) |
| 完整发现首轮（沙箱） | `python3 -m unittest discover -s scripts/tests -v` | 实际236方法，60.704秒，退出1：226通过、10项本机HTTP端口无法运行 | [沙箱原日志](/private/tmp/ans-workflow-fixes-source-qa-20261020/full-suite-final.log)、[沙箱摘要](/private/tmp/ans-workflow-fixes-source-qa-20261020/full-suite-final-summary.json) |
| 完整发现复测（允许本机端口） | 同一完整发现命令、同一候选 | 236方法全部通过，71.216秒，退出0；四源码/测试摘要未变 | [最终完整原日志](/private/tmp/ans-workflow-fixes-source-qa-20261020/full-suite-loopback-final.log)、[最终完整摘要](/private/tmp/ans-workflow-fixes-source-qa-20261020/full-suite-loopback-final-summary.json) |

唯一首轮失败来自新增`test_role_documents_still_require_exact_task_scope_and_registration`的错误文案断言。无roleDefinitions时，工具实际退出2且保持任务记录不变，消息为`Configured write file is absent from boundary Section 1: role-cards/developer/docs/design/new.md`，用例却限定含governance。修正后仍要求退出2、任务字节不变、同一精确路径及boundary/governance拒绝类别；未放松权限或删除断言。首轮失败日志和项目保留，未改生产代码。同时补入根定点指出的未选`.ans/unselected.md`及`docs/scheduling/unselected.md`实际预检负例。

完整发现首轮的10项ERROR均为既有HTTP回归绑定`127.0.0.1:0`时被沙箱拒绝，PermissionError Errno1；原日志逐项保留。按已确认完整回归范围通过require_escalated允许本机临时端口后，未改代码或skip断言，重新运行同一完整组并全部通过。40项独立CLI包含在236项完整发现中，不累加称276项。最终CLI原日志SHA-256为`6ba7aede20425af866d72ec0c499197dd94ee2d95a30579aa006cc0248d1149a`；最终完整日志SHA-256为`4a961f66cacd4fe89947ca64ba5c4407593962b337623f44d825e899cea8c5ea`。完整发现包含原Dashboard/云端/同步/角色通道、工具开发69项及既有timer等回归，不把这些称库存业务回归。

## 隔离载荷复制和治理差额

唯一新验证根为`ans-full-trial-2026-10-19-bqf0vjof/validation/workflow-fixes-2026-10-20/`。按已接受的[QA边界复制例外](../../boundary.md)准备，不作为task_ops跨根权限，不放宽safe。

1. 初始复制94文件：20原交付文件、九角色各7份输入、旧五份冻结合同、四份API、final-candidate及原配置。原配置仅放baseline-inputs/original-project.json。94份复制均与原件逐字节相同，20文件同时匹配旧final-candidate摘要。未复制旧任务/runtime/私密环境/凭证，没有生成新config。
2. 初始[copy-manifest](../../../../../ans-full-trial-2026-10-19-bqf0vjof/validation/workflow-fixes-2026-10-20/baseline-inputs/copy-manifest.md)原版本摘要为`6fb6bcdb5f427d9bbf4dc3752607810f60ac0e9d5e42ce6c2b13b2b2e7ce5b9d`，记录94行原件/副本双摘要，之后保留这张历史表。
3. 根团队组建接受副本治理后，QA只读其[差额收据](/private/tmp/ans-workflow-fixes-20261020-pfkr9dbm/governance-delta.json)并逐项核实：仅副本test的boundary.md、boundary.yaml、changelog.md三份为获准治理差额（增加三fixture精确路径）；其他91份输入仍等于原件。QA未编辑治理内容。manifest增加第二执行基线，记录三份原/新摘要及归属；此时暂态摘要`a34126c23bc836c996654911c7052c88b5a78476ec39cffef25b8acae43fde37`，源工具尚未加入，未宣称已冻结最终manifest。
4. 稳定源工具按上表摘要复制为validation-tools/task_ops.py和coordination_store.py，源字节=副本字节。最终manifest已加入两工具表并冻结，SHA-256为`60fe4b772d938baadec96cf057805190a9972be71ccfd907931fb7f7cc273beb`。共96份准备输入+manifest；不嵌入manifest自摘要，后续readSet绑定它本身。其`Accepted input digests`二列表为94条接受后输入，`Stable source-tool copies`四列表为2条工具；历史初始表和三条治理差额不是重复输入。
5. 三fixture、Provider文档、隔离test方法报告、标准、plan/config由各实际隔离角色维护。QA未代写这些产物、未改副本治理、未init任务；已把冻结manifest格式/精确数量交统筹供配置检查复用。准备清单不自动包含后续新文件，实际任务仍须精确展开全部read/write。

## 隔离角色本人执行与源QA只读核对

实际新任务为`workflow-fixes-isolated-20261020`，唯一正式[任务记录](../../../../../ans-full-trial-2026-10-19-bqf0vjof/validation/workflow-fixes-2026-10-20/docs/scheduling/workflow-fixes-isolated-20261020.md)。源QA本次恢复只调用普通只读status、读取原任务事件及原输出，没有持worker/验收凭证，没有重跑源236或库存60。

- `document` / provider-json本人ack、写唯一说明、run-check document-content、report complete，再由独立acceptance本人按阶段标准verify。源QA实读revision18时该节点status=verified、currentAcceptanceValid=true，候选`4cf0e21a600ed2141da258242a7632eb096a557bdd8cc0a04bb4a1f64acf2dd9`；document-content原日志SHA-256 `54e706d41dfdc8d9a25e2df2c3e6dd3ccfcd5e031e237c018468fdf61b3e96c1`，退出0、v2、候选及环境未变。阶段通过只放行后续独立test。
- `document-check` / test本人ack后先固定[唯一方法报告](../../../../../ans-full-trial-2026-10-19-bqf0vjof/validation/workflow-fixes-2026-10-20/角色卡/test/docs/change/2026-10-20_change_workflow-fixes-validation.md)，SHA-256 `6ef8e3fd65a41a6faea8913d33ae9b03c8d73b013aaf3489be41b485aa311d41`；随后八次正式run-check，最后本人report complete，reportId=`inventory-check-20261020-document-check-1-complete-1`。源QA实读revision18时status=awaiting-verification，尚未把它写成最终pass。
- 八项均为同候选`df0dd19736ee1578dde6951d37e6398329bcbb839edeb12ef394902df1bc6ef0`，全部exitCode=0、environmentVersion=2、candidateUnchanged=true、environmentUnchanged=true，日志字节摘要均与checkEvidence一致。方法报告在正式检查后没有回写，当前摘要仍相同。源两工具、副本两工具及最终manifest保持上文冻结摘要。

下列结果是**隔离test本人实际运行、源QA读取其原日志核对**，不是源QA冒称亲自执行。

| 正式check | 实际方法数 / 输出 | 原日志 |
| --- | --- | --- |
| regression-model | 7，OK | [model](../../../../../ans-full-trial-2026-10-19-bqf0vjof/validation/workflow-fixes-2026-10-20/.ans/runtime/workflow-fixes-isolated-20261020/evidence/document-check-1-regression-model-2bfb4b12.log) |
| regression-provider | 7，OK | [provider](../../../../../ans-full-trial-2026-10-19-bqf0vjof/validation/workflow-fixes-2026-10-20/.ans/runtime/workflow-fixes-isolated-20261020/evidence/document-check-1-regression-provider-8b6e56dc.log) |
| regression-service | 10，OK | [service](../../../../../ans-full-trial-2026-10-19-bqf0vjof/validation/workflow-fixes-2026-10-20/.ans/runtime/workflow-fixes-isolated-20261020/evidence/document-check-1-regression-service-5e37c777.log) |
| regression-cli | 21，OK | [CLI](../../../../../ans-full-trial-2026-10-19-bqf0vjof/validation/workflow-fixes-2026-10-20/.ans/runtime/workflow-fixes-isolated-20261020/evidence/document-check-1-regression-cli-980b1cec.log) |
| regression-assembly | 6，OK | [assembly](../../../../../ans-full-trial-2026-10-19-bqf0vjof/validation/workflow-fixes-2026-10-20/.ans/runtime/workflow-fixes-isolated-20261020/evidence/document-check-1-regression-assembly-ab717dec.log) |
| unit-integration | 9，OK | [integration](../../../../../ans-full-trial-2026-10-19-bqf0vjof/validation/workflow-fixes-2026-10-20/.ans/runtime/workflow-fixes-isolated-20261020/evidence/document-check-1-unit-integration-13d0f19a.log) |
| document-manifest | 根内96准备输入/manifest、20载荷、旧五合同、四API、两工具、九定义、精确写入、三fixture及固定方法报告断言成功 | [manifest](../../../../../ans-full-trial-2026-10-19-bqf0vjof/validation/workflow-fixes-2026-10-20/.ans/runtime/workflow-fixes-isolated-20261020/evidence/document-check-1-document-manifest-eeacccce.log) |
| fixture-executable | `WORKFLOW_CHECK_PROBE_OK_v1`加LF | [fixture](../../../../../ans-full-trial-2026-10-19-bqf0vjof/validation/workflow-fixes-2026-10-20/.ans/runtime/workflow-fixes-isolated-20261020/evidence/document-check-1-fixture-executable-4f2cef87.log) |

六组合计60方法，不重复累计开发回归、历史77次进程调用或本轮额外两个断言为库存方法数。原事件的ack/check/report producer分别为provider-json/document-1和test/document-check-1；verify事件producer为独立acceptance，统筹只派发/消费结果。源QA的[只读证据观察摘要](/private/tmp/ans-workflow-fixes-source-qa-20261020/isolated-evidence-observation.json)记录逐日志完整摘要及revision18状态，不含私密快照值。

**最终独立结论已实读。** 固定隔离acceptance本人真实提交document-check的verify，任务到revision19，两必需节点均verified/currentAcceptanceValid=true、taskComplete=true。其[独立结果报告](../../../../../ans-full-trial-2026-10-19-bqf0vjof/validation/workflow-fixes-2026-10-20/角色卡/acceptance/docs/change/2026-10-20_change_workflow-fixes-result.md) SHA-256为`7f3b5481fccaec841de1a46a336cc5167858428f1d16cc3334b1c26e6bff7477`，逐项引用真实C1判断、九份原检查与原失败历史；这些是其本人结论，不是源QA代验收。

该独立角色在两个不同普通PATH下只读status，均保持revision19、两节点有效及taskComplete=true；任务文件前后SHA-256均为`ed04991f6a3e753b8d32feb3d6ad74adc4483e8e22568c41118a26b031b2dcf2`，没有新增check或回填原环境。源QA随后仅作一次普通只读status再次确认同一revision19及两节点有效，前后任务SHA相同，checkHistory仍为Provider1+test8共9，见[最终只读状态摘要](/private/tmp/ans-workflow-fixes-source-qa-20261020/isolated-final-status-summary.json)。没有重跑任何源236、库存60、程序或检查。根随后还以普通当前环境、不恢复旧观察环境，直接用新源工具消费新隔离任务status，实际同为revision19、两节点有效、taskComplete=true，Provider1+test8检查保持，任务Markdown字节不变；这是第三实际角色的普通状态消费佐证，未另跑检查。

## 旧库存保全与限制

读取根事前保全文件`/private/tmp/ans-workflow-fixes-20261020-pfkr9dbm/baseline.json`，在本轮源CLI运行前及完整回归/准备收尾后两次实际重算188份旧文件摘要与文件集合：变化0、验证根外新增0、删除0。旧任务SHA-256仍为`5628337d3414bd031ab2721be69eff3df1a98895bb59337b526220b399e1b346`，见[源QA收尾保全结果](/private/tmp/ans-workflow-fixes-source-qa-20261020/original-preservation-after-source.json)。这是源回归/复制准备阶段的收尾比较，副本正式检查完成后的比较另见下文。未对旧任务派发、run-check、report或verify，也未追认旧hash-only。

隔离test正式检查完成后，源QA在任务外再次执行父根保全比较，旧188文件摘要/集合变化0，唯一新根外新增0、删除0，见[最终外部保全摘要](/private/tmp/ans-workflow-fixes-source-qa-20261020/original-preservation-after-isolated.json)。按D1 7.3，用当前源工具`2919757a…a4236`对旧`inventory-full-trial`作只读status，仅从既有私密observed-check-environment.json overlay values并移除absentKeys，未输出原值或复制旧环境到新根。实际返回revision93、六节点currentAcceptanceValid=true、taskComplete=true；调用前后旧task SHA-256均为上述`5628337d…1b346`，见[旧任务只读兼容结果](/private/tmp/ans-workflow-fixes-source-qa-20261020/legacy-status-final-summary.json)。这证明当前工具在旧实际观察环境保留legacy判定，不是给旧证据补快照或追认新版结果。

根还独立只读核得相同的旧93/188保全结果、四批准输入未变及工具副本等源，见[根独立保全收据](/private/tmp/ans-workflow-fixes-20261020-pfkr9dbm/preservation-final-root.json)。旧环境兼容与字节保全证据不冒充新版不同PATH证明；后者来自源真实CLI负/正例及上述隔离独立角色的普通查询。源规范owner最后的批准路径内路由文字小修未改工具/测试、四批准快照或根内plan/C1，本次只补实际证据，没有追加测试范围或改冻结输入。

已知限制：工作文档预检不是新架构扫描器；原Provider/Service层结构由原授权回归、既有库存两AST方法及合同核对证明实际范围，不宣称新增缺三目录的通用机器检查。源CLI自动化fixture不代真实角色协作；源完整发现不代副本库存60项；测试通过不代独立验收。安装、public、push、发布均未执行。
