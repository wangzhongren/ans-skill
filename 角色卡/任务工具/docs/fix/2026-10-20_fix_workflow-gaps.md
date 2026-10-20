---
id: task-tools-workflow-gaps-fix
type: fix
title: 角色工作文档与检查环境的任务工具修复
created: "2026-10-20"
updated: "2026-10-20"
timezone: Asia/Shanghai
status: implemented-unverified
related: [task-authority, workflow-friction-product-p1]
events:
  - date: "2026-10-20"
    kind: created
    summary: 任务工具 owner 只读核对实码，形成方案评估；没有实施或测试
  - date: "2026-10-20"
    kind: implemented
    summary: 客户确认P1及D1-final-1后实现三项工具修复；开发69项通过，待固定测试和独立验收
---

# 角色工作文档与检查环境的任务工具修复

当前状态：客户已确认 P1、D1-final-1、C1及QA-T1-draft-1，并明确“按方案完成修复和验证”。固定 `task-tools` 已完成本角色程序、开发单测和当前功能说明；69项开发测试通过，等待本轮独立固定测试与验收。实际实施、候选及日志见文末。以下首轮和成文评估保留当时事实，不代表当前仍停留在只读方案阶段。

本文最初是固定角色 `task-tools` 的独立方案评估，供项目管理完成技术设计和实质评审。首轮仅修改本文件，没有修改程序、测试或现有功能说明，没有初始化任务、运行测试、安装或发布。源码基线为 `main d95d006`；本轮其他角色已有自己的未提交文档改动，本文不将其计为本角色成果。

用户要解决三个实际问题：角色交接前能发现工作文档缺权；本角色已获准的精确工作文档可以进入任务；查询者无关的 PATH 写法变化不会推翻实际执行对象相同的检查结果。产品目标见[策划 P1](../../../策划/docs/design/2026-10-20_design_workflow-friction-product.md)，当前功能见[任务工具权限与证据](../feature/task-authority.md)。本文形成时，项目管理 D1 尚未落盘；以下评估针对统筹转交的 PM 最小契约提议，不冒称已评审 D1 正文。

随后已实际读取[PM D1 全文](../../../项目管理/docs/design/2026-10-20_design_workflow-fixes.md)，补充核对与当前 owner 结论见文末；前述未成文状态仅说明首轮评估的时间点。

## 实际触发点

1. `scripts/task_ops.py` 的 `roles_valid()` 只承认 `owned_code_directory()` 识别的 common/test 子树，且对目录和精确 writeFiles 均拒绝 `role-cards/` 与 `角色卡/` 前缀。因此即使 Section 1 精确授予自身 feature-map 或 docs 文件，也不能进入执行配置。
2. `environment()` 从当前进程继承环境，并把 PATH 原文纳入变量摘要；`evidence_valid()` 以本次查询进程环境重算，再与运行检查时的整份 environment 相等比较。两个查询终端即使解析到同一可执行文件及内容，也会因 PATH 原文不同被判环境改变。
3. 现有 `operate()` 在任何分支之前进入 `Store.locked()`。该函数创建 `.ans/runtime/<task>/`、运行目录忽略文件和锁。把新预检仅加在这个锁内，不能声称无任务写入的只读检查。CLI 当前也一律要求 `--task`。
4. `coordination_store.safe()` 已拒绝绝对路径、穿越、任意路径段 symlink 与越出项目根；新角色文档校验应复用它，不另建弱化版本。

## 对最小配置契约的建议

建议采用既有审核配置中的可选 `roleDefinitions`，复用 `scripts/task_ops.py` 新增 `preflight-role`，不另建脚本或权限 JSON。仅从当前 `roles` 推导全角色保护集合更短，却漏掉未作为本次执行者登记的统筹、验收及其他角色，不能满足完整预检和跨角色保护。

`roleDefinitions` 是按 roleId 登记的角色定义映射，值仅包含实际 card、boundary 和适用工作文档清单。roles 中的执行者以及 acceptanceAuthority 的 card/boundary 必须与对应登记一致；统筹等非执行角色也在登记内。角色根只能取 card 与 boundary 的共同父目录，不能把 roleId 当目录名拼接。本项目实际 `task-tools` 与中文目录名不同，正好说明这种推导会出错。

建议把工作文档清单定为**精确项目相对文件路径**：它表达这个角色实际需要维护哪些伴随文档，供交接预检逐项检查 Section 1 覆盖；它自身不授予写权。适用清单不必要求文件已存在，交接检查应能指出“准备创建但未获权”的文件。角色无关的 api-spec 等不强制补齐。目录授权仍只来自 Section 1，任务 writeFiles/writeSet 仍只接受精确文件，不需要再在登记里发明目录通配、第二份授权表或文档存在性门槛。

角色文档的可执行范围应同时满足：确属自身根目录约定的工作文件，或自身 `docs/` 子树；Section 1 精确条目或自身 docs 有界目录确实覆盖；审核配置 writeFiles 精确列出；计划节点 writeSet 包含该文件。根工作文件的有限集合需由 D1 明列，例如 feature-map.md、memo.md、functional-description.md、api-spec.md；不开放整个角色根。登记中的适用文档清单用于发现缺项，不把未在此清单出现但已获 Section 1 的未来 dated docs 文件判为越权。

新任务申请这类角色文档写权时，必须提供完整登记。无此字段的旧配置继续使用原执行范围判断，保持原有拒绝角色目录的语义；不能修改旧批准配置来让旧任务自动扩权。新增字段后配置摘要变化，仍按现有规则需要新的审核配置和任务，不能追改原 configHash。

## 必须在放行前完成的路径判断

应先校验完整登记并建保护集合，再校验任何角色的 writeFiles，不能边遍历边只保护已经见过的角色。

- 所有登记角色的实际 card、boundary、边界同名 YAML，以及根 changelog.md 均受保护，包括非执行角色和验收角色。根 changelog 的治理维护与角色 docs/change 工作记录应明确区分。本轮不顺带改变治理归属。
- 任意两个角色根相同或祖先／后代交叠，先拒绝登记；card/boundary 必须同父且规范、真实存在。不能让一个角色的 docs 子树包住另一角色的治理文件。
- 工作文档或 docs 目录与已登记治理文件／治理保留目录、`.ans/`、`docs/scheduling/` 相交时拒绝。检查路径组件边界，不能只做无斜线的字符串前缀比较。
- 复用现有 safe 和规范项目相对路径要求拒绝穿越、别名、symlink；目录不能伪装成精确 writeFiles。未来未创建的文件也须核对其现存祖先没有 symlink。
- 现有 `claim_scope()` 的跨角色目录／文件重叠检查继续使用；docs 目录新增支持不能扩大 common/test 或其他源码目录规则。

这些是用户本次要求的实现必要条件，并非附加通用安全改造。工具仍不能防止有权任意改配置、源码和哈希的同 OS 操作者。

## 交接预检应怎样接入

`preflight-role` 应在 Store 构造／加锁前走独立只读分支，不要求 task ID、任务凭证或已有任务；不执行 checks，不创建 runtime、日志或任务记录。可以复用登记／Section 1／路径保护的校验函数，避免预检说可写、init 又拒绝的两套规则。结果至少标明角色、缺权具体路径和原因，退出 0 或拒绝退出 2。

预检只说明当前定义满足所声明适用文档的覆盖，不是客户授权、派发、验收或工具能理解职责的证明。“交接前自动”还需要技能规范把调用放到实际建立／交接路由中；单独存在命令而无人调用不满足用户目标。init 在申请角色文档范围时应复用同一校验，避免绕过交接路由仍执行缺权任务。

## 环境有效性约束与旧证据

环境具体数据形状和运行资源选择由 PM D1 定案，本角色不抢写第二套环境设计。但实码决定了以下约束：

- 只从变量摘要里删 PATH 不能完整实现“运行事实与查询者环境分开”，也可能误放行通过 PATH 再找子程序的检查。应区分运行检查时固定的事实和查询时能重新验证的实际资源；无法判断相关性时明确判当前无效。
- 相同实际可执行路径及内容的无关 PATH 写法差异应保持有效；实际程序内容、相关运行资源、批准配置、源码/readSet、日志改变仍须失效。不能以宽松整体比较替代这些现有门禁。
- 现有 environment 已把显式 check.env 明文放入 declaredEnvironment，status 只按 token/credential 键名脱敏，并不保护任意环境变量。新运行资源固定机制不得把整个 os.environ、私密 PATH 或秘密值写入受 Git 跟踪的任务／配置／报告；应利用本地被忽略的运行资料，只在可跟踪记录中保存必要非敏感事实及校验摘要。私密数据不足时拒绝或明确无效，不静默退回查询者环境。
- 旧 variablesHash 是整体摘要，不能从它补造原变量或执行事实，也不能重写旧 evidence/environment/configHash 追认通过。旧格式核对保留原语义；本轮新行为的证明使用新隔离任务。

原库存 stateRevision 93 与 taskComplete=true 由统筹提供的私密跟踪环境复核结论引用，本文没有重新核验或修改它。原批准文件、任务、日志及 20 个源码和测试文件均保留。

## 独立验证根的最小可行判断

若 PM 采用 `validation/workflow-fixes-2026-10-20/` 为受限新验证项目根，不能让 argv 偷读父库存源码、同时宣称候选已覆盖它：safe/readSet 不允许越根，放松 safe 也不在本次范围。把原库存 20 文件与必要角色输入按相对布局字节一致复制进新根，将检查脚本、fixture、必要角色与源码输入列入 readSet，并运行既有库存 60 项，是符合受限根的较小方案；复制不是新增库存业务实现。

另一个合法方案是在原库存根建新 taskId 和独立受限新配置，不改旧配置、旧任务和旧输入，但需要另行确认该根的准确写权，且更容易混入旧状态。当前受限根意图下建议前者，最终由 PM 明确选定。不能用新外部依赖系统替代合理的只读复制。这里只评估可行性，没有执行复制或测试。

## D1 必须明确的事项

1. 全角色登记的完整性按什么项目范围核对：至少覆盖 roles、acceptanceAuthority、统筹及全部实际项目角色。不能递归把 test/game-engine 等隔离样例误当本项目角色；也不能仅自称“完整”而忽略已知另一角色。建议由 Team Formation 交接实际角色清单与审核配置相互核对，说明工具可检查的覆盖条件和无法自动发现未声明角色的边界。
2. 适用清单是否采纳精确文件且仅用于预检，以及根工作文件有限集合。目录覆盖来自 Section 1，避免出现“清单授予权限”或“所有角色强制相同资料”的歧义。
3. 预检输入与无任务 CLI 形式、实际交接自动调用位置，以及 init 的同源复核；不能只写一个需人工记住的命令。
4. 新旧环境证据如何分流、哪些实际资源重新校验、私密运行资料如何留本地，以及受限验证根选用哪一种方案。缺资料的错误必须可解释，不能补造旧 hash。

上述事项明确后，推荐继续原 PM 单配置最小方向。当前没有提出额外选装，没有实施，没有运行单测或真实 CLI，也没有给出 QA 或验收结论。

## D1 成文后的针对性 owner 结论

已真实阅读 D1 第3、4、5及7节和其余全文。**任务工具 owner 支持 D1 技术方向，完成下面两处语义小修后可按现有文件范围实现。** 这是实现可行性意见，不是 QA、验收通过或客户实施授权。

第3/4节已明确精确适用清单仅作预检、同父目录解析角色根、全角色先建保护集合、目录相交检查、旧配置原语义及先于 Store 的只读入口，覆盖首轮意见。全角色完整性由实际项目交接核对而非递归发现测试样例的界限也已说清。apiSpec/Reason 的适用判断交原规范 owner，工具只按明确枚举和具体清单校验，不自行理解自然语言职责。此方向可在 task_ops 内复用辅助函数完成，无需新增源模块或改变 safe/Store。

第5节捕获一次实际环境、私密最少快照、固定实际程序执行、status/verify/依赖共享复核以及旧证据原样保留的方向可行。它保留“跟踪环境和相关 readSet 之外仍有隐藏依赖”的原限制，不把查询者 PATH 当运行环境，也没有承诺跨机器自动复用。第7节已选定字节复制、两个源工具候选入 readSet 和原60项回归，符合隔离根约束；准备输入和真实固定角色授权由统筹继续核对，本角色没有执行复制。

两处小修应由 PM 写清，避免实现者在边界情形自行猜测：

1. **v2 不得因快照缺失退回旧比较。** 第5.2节已经要求 v2 缺失／变化时无效，但第5.3节“无 environmentVersion 或无可验证快照的旧证据”易被写成一个宽泛 OR。建议明确：无版本字段才走原 legacy 路径；environmentVersion=2 时快照缺失、损坏或形状不符直接无效；未识别版本也拒绝。这样不会把损坏的新证据以恰好匹配查询者环境的方式放行，不需要迁移旧任务。
2. **切换实际环境的复测须服从现有状态机。** 第5.2节的新 run-check／报告／verify 流程只适用于仍活动且被允许补证的 assignment。现有 verify(pass) 会设 active=false，dispatch 也拒绝 verified，所以已通过节点不能在原批次直接再跑；应明确使用新审核任务，不为本修复新增“重开 verified”接口。另外，现有 latestReport 只绑定 candidate 和 attempt，不绑定 environment/evidence；若 D1 保留“换环境不得沿用旧 report”的硬要求，实施必须显式使该旧报告失效，否则代码仅换 checkEvidence 后仍可能接受它。较小的契约是保留现有完成报告的候选／批次条件，同时要求新检查证据经独立 verify，绝不沿用旧 acceptance。请 PM 在 D1 二择其一写明，而非新增一般性的报告绑定改造。

除这两处具体语义外，本次未发现必须增加新配置体系、额外脚本或扩展安全路径能力的理由。现有 source 四程序文件未改；本回合仅补本文，没有实施、没有运行测试、没有初始化任务。

## 已批准修复的实际实施与开发验证

客户确认后，本角色只修改 `scripts/task_ops.py`、`scripts/tests/test_task_ops.py`、本记录和[当前功能说明](../feature/task-authority.md)。没有修改 coordination_store、QA测试、规范、他角色文档、旧库存、已安装技能或public；没有建立生产任务、复制库存、安装、发布或push。单测中的临时项目和fixture身份仅证明工具行为，不冒充真实角色交付或独立验收。

实际入口与行为如下：

| 用户动作 | 实际结果 |
| --- | --- |
| `--root <项目> preflight-role --request -`，只给configPath | 无task/凭证；先于Store分支，逐角色返回documents的path/exists/permissionGranted及issues，整体permissionsComplete；通过0、缺项/冲突2，不运行checks或创建任务/runtime/锁/日志。 |
| 使用roleDefinitions的新配置init | 同源校验实际Section1、core/API声明、全部登记根与保护集合；失败不写任务记录。清单不授予权限，未来dated文档仍可按已批准自身docs目录精确选择。 |
| 本角色工作文件进入writeFiles/writeSet | 根限feature-map/memo/functional-description/适用api-spec，自身docs限精确Markdown；目录只做覆盖判定。治理/他角色/重叠/穿越/symlink拒绝。 |
| 运行新检查 | environmentVersion=2、environmentSnapshot={path,sha256}；捕获一次合并env，固定canonical实际可执行文件运行；私密最少快照目录0700、文件0600。 |
| 另一个终端查询／验收／依赖消费 | 使用原快照同源重核；无关查询PATH/LANG等变化不替换运行事实，程序/配置/readSet/日志/快照真实变化仍无效。无版本字段保留legacy语义，v2异常与未知版本绝不回退。 |

登记字段为 `roleDefinitions.<roleId>.{card,boundary,requiredWorkDocuments,apiSpec,apiSpecReason}`。有限core、API适用规则及实际根解析按D1-final-1；全角色登记是否涵盖项目全部实际角色仍由治理交接核对，工具不扫描发现未登记角色。预检逐项核对所有实际Section1，而不是只查当前writeFiles。

实现时核对真实库存输入发现：assembly边界中 `.gitignore` 的用途文字包含反引号 `.ans/runtime/`，旧解析抓整行会误认权限。共用解析器现只取“可操作路径”列，避免假冲突，也避免用途文字扩大授权。统筹既有 `.ans/project.json`、`.ans/runtime/` 和 `docs/scheduling/` 管理范围允许登记及所有权核对；非统筹在Section1声明这些范围即预检拒绝，统筹普通节点writeFiles也仍拒绝状态范围。宽 `src/`、`common/`、`test/` 及没有尾斜线的现存目录不产生虚假预检通过；原common/test有界规则继续有效。

v2快照内部仅有 `environmentVersion`、`trackedKeys`、`values`、`absentKeys`，不采集未跟踪变量。工具生成路径为 `.ans/runtime/check-environments/<task>/<attempt>-<check>-<16hex>.json`，任务只记录引用和摘要。environment公开字段为platform/python/selectedExecutable/executable/executableHash/trackedKeys/variablesHash/declaredEnvironmentHash，不含明文declaredEnvironment。复核会核对快照形状、值/absent集合、批准声明、实际程序解析目标和字节；合法可执行链接按实际目标核对，项目readSet仍按safe拒绝symlink。

生产候选已冻结交固定测试；若独立QA发现同范围问题，按实际返工更新候选并重取受影响证据。Python实际版本 **3.14.7**，开发命令：

```text
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s scripts/tests -p test_task_ops.py -v
```

最终结果：**69项，7.978秒，退出0，无跳过**。原输出：[最终开发日志](/tmp/ans-workflow-task-unit-final-20261020.log)。保留原49项方法并新增20项；原生产者测试按批准语义断言v2查询者变化仍有效，同时新增显式legacy fixture保留旧环境变化使结果无效的原语义。覆盖完整登记、无Store及文件树不变的真实CLI预检、文档真实生命周期、未选择的边界冲突、自定义治理文件、scheduler例外、精确范围、实际执行对象与单次捕获、快照隐私/权限、真实资源/声明配置变化及旧格式分流。它们不等于独立固定QA或库存60项回归。

真实失败历史没有清理：首轮原49项有2个格式迁移预期失败，日志 `/tmp/ans-workflow-task-unit-initial-20261020.log`，分别是旧断言要求查询者NODE_OPTIONS使v2失效，以及缺日志时先报快照错误。前者按新契约调整并增加legacy原语义测试，后者保留原“日志不可用”优先错误；没有放松日志存在/摘要校验。第二轮67项有1个新fixture错误：沿用旧helper报src/a.py，精确文档范围将其真实拒绝；修正fixture实际changedPaths，不放宽门禁。日志 `/tmp/ans-workflow-task-unit-round2-20261020.log`。第三轮67项10.541秒退出0，日志 `/tmp/ans-workflow-task-unit-round3-20261020.log`；最终再加入2项必要治理/资源场景，得到上述69项结果。

`git diff --check -- scripts/task_ops.py scripts/tests/test_task_ops.py` 退出0。冻结逐文件 SHA-256：

| 文件 | SHA-256 |
| --- | --- |
| scripts/task_ops.py | `2919757a34d8c725c1f3fb1bafd0444003d40824e431e99cc4bbf4e44e0a4236` |
| scripts/coordination_store.py（原样只读） | `09aee0153d26f0510e77eaaa284a48549a3bfc8d96fdc23ce4a53df4b6af7fd4` |
| scripts/tests/test_task_ops.py | `9b1d1cb014afe8bf922cd9af57439fd33582695cf6a675ebb29cd7d0f1220235` |

当前开发交接已完成，独立源QA、库存隔离根真实两节点及原60项回归、旧库存保全和最终独立验收由各原角色继续。本角色没有执行这些项目，也不以开发通过宣称整体修复完成。未声明环境/外部依赖仍在现有模型之外；快照丢失要求重新取得合法测试证据，不能猜原值恢复。
