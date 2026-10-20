# 统一任务操作：调度与验收分权

使用 [task_ops.py](../scripts/task_ops.py) 维护任务记录，不手工改状态 JSON 或 Markdown 机器块。程序核对角色范围、依赖、版本确认、反馈身份和实际检查证据，通过一个加锁存储统一写记录。它不会创建代理、执行操作系统权限隔离或独立认证客户身份。

既有分权字段对应[分权设计](../角色卡/项目管理/docs/design/2026-10-19_design_role-authority-split.md)；本轮角色文档与环境v2按客户已确认的[D1-final-1](../角色卡/项目管理/docs/design/2026-10-20_design_workflow-fixes.md)同步。新增CLI字段已按任务工具owner交付接口核对，独立测试与验收仍待各原报告，不将文档接口核对当作执行通过。配置和计划仍使用 `schemaVersion: 1`，新任务状态使用 `schemaVersion: 2`。接口已实现不等于整体验证通过：开发单测、真实 CLI 与独立验收分别以各所有者原报告为准。

## 谁持有什么权限

| 持有者 | 允许做什么 | 不得到什么 |
| --- | --- | --- |
| 统筹／可信操作端 | 建计划、逐角色授权和范围预留、派发、记录修订、核对恢复 | 独立验收凭证、直接设通过或关闭任务的权限 |
| 指定执行者 | 确认自己的版本、运行配置允许的真实检查、报告和确认停止 | 其他执行者、调度或验收权限 |
| 独立验收 | 实施前核对客户标准和计划，交付时判通过、返工或证据不足 | 派发实现、扩权、修改业务代码或别人的报告 |
| 内置 ANS 团队组建 | 按授权维护招聘、角色卡与文件边界 | 日常任务派发或交付验收 |

统筹直接安排每个具体 `roleId`，并接收它的原始反馈。`group` 只分类；不设组长、组内职责或组内派发。所有请求仍经同一个单写工具序列提交，验收决定独立不表示第二个人手工改任务文件。

客户／可信端审核一份项目执行配置（通常 `.ans/project.json`），固定实际内容摘要。AI 自己计算摘要不是客户批准；配置须说明真实角色卡、边界、精确写入文件、允许操作、检查命令与自动派发权限。任务写入集合只能缩小已确认边界。配置中目录归属和计划中精确文件是两件事：获准目录可长出任务必要文件，但执行前仍须列入已审核配置和当前任务。

独立验收秘密由可信本地端在统筹上下文之外产生，明文只直接交验收上下文，配置只放摘要及批准验收身份和标准路径。初始化不能产生、返回或覆盖验收秘密，不能让两种凭证相同。明文不进入仓库、报告、共享记录或云端项目 Key；丢失或更换须重新走可信配置与授权建任务，不能让统筹重置它。工具检查秘密与固定输入，不把角色名、摘要或自述当客户身份认证。

## 角色文档登记与交接预检

现有配置 `schemaVersion: 1` 可增加 `roleDefinitions`，不新建配置文件。每个实际roleId登记 `card`、`boundary`、`requiredWorkDocuments`、`apiSpec`、`apiSpecReason`。card/boundary是存在、可读、无符号链接的精确项目相对路径，必须同父；该父目录才是角色根，不能从roleId拼目录。重复或相互嵌套的角色根拒绝。roles执行者和acceptanceAuthority的card/boundary必须与登记一致，schedulerRoleId也须已登记。

登记涵盖本项目全部实际角色，包括不作为执行者的统筹、策划、PM和验收。团队组建准备实际清单，原owner核对适用性，统筹与验收核对完整性；工具只能验证提供的登记，不能证明不存在未登记角色，也不递归把隔离样例当项目角色。

`requiredWorkDocuments` 是职责需要的精确工作文件，仅用于预检许可，不授权、不接受目录通配，也不限制已获边界覆盖的未来日期文档。最低列实际角色根下feature-map.md、memo.md、functional-description.md；有真实对外代码/shared能力或装配接口时 `apiSpec: "required"` 并加入根api-spec.md，否则可声明 `"not-applicable"`。两种取值都须非空、可核对的apiSpecReason，不能凭角色名判断或临时漏填。纯协作角色写真实职责、交接和文档位置，无系统功能/代码就明说，不虚构代码层。

团队组建只准备完整登记内容与角色权限定义，已接受的统筹在其自身边界内写候选执行配置。新项目先接受统筹定义，独立固定统筹上下文仅做配置准备，随后运行只读预检；齐全后再交接/派发其余实际工作。已有项目由原统筹准备配置。此顺序不授权团队组建写配置，不新增审批，也不以配置准备代替客户配置审核或派发门禁。候选配置具备后，运行真实只读入口：

```sh
python3 /path/to/skill/scripts/task_ops.py --root /path/to/project preflight-role --request -
```

标准输入只传 `{"configPath":".ans/project.json"}`，替换成实际候选配置路径。不要求 `--task`、凭证或审批动作；此分支在Store构造/加锁之前执行，不创建任务、runtime、忽略文件、锁或日志，不运行checks，也不修改文档或边界。响应有 `status`、`permissionsComplete`、逐角色 `roles`（含documents和issues）以及全局 `issues`；指出角色、实际路径、缺权/重叠/保护问题及文档存在情况。成功退出0，缺项或冲突退出2。文件尚不存在可报告 `exists=false`，不能把许可齐全说成内容已完成。

预检读取全部登记角色真实Section 1，既查requiredWorkDocuments归本人且获许可，也查未选入当前writeFiles的权限重叠。失败交团队组建处理所需授权差额并重查；适用性不清返回职责定义owner。成功不等于客户批准、派发或验收。新配置启用roleDefinitions时，init复用同源检查，失败不创建任务记录；后续定义改变仍按现有哈希门禁失效。

无roleDefinitions的旧配置保持原执行范围语义；申请新增角色文档能力，须完整登记、新审核配置和新任务，不能改旧批准内容或configHash自动扩权。此规则与旧JSON任务状态的只读兼容是两件事。

### 哪些工作文件可以进入执行范围

角色文档必须同时处于以下交集：**自身有限根工作文件或自身有界docs内精确Markdown ∩ 实际Section 1 ∩ 审核配置精确writeFiles ∩ 当前节点精确writeSet**。根文件限feature-map、memo、functional-description及适用api-spec；不开放任意根文件或整个角色根。Section 1可授自身docs/或明确docs子树，配置/节点仍只能选择本轮精确文件，目录不能进入writeFiles/writeSet。代码文件及common/test原限制保持。

先构造全部角色保护集合，再判断许可：全部实际card/boundary、同名boundary YAML、根changelog，包含自定义治理路径；docs内治理命名也不作普通工作文件。`.ans/`与`docs/scheduling/`及子路径继续拒绝普通执行写入，其他角色资料受保护。目录授权也检查是否包含保护文件、包含或进入其他角色根、与其他角色文件/目录相交；路径按组件判断，docs/a不覆盖docs/ab。同角色文件在自己的目录许可内可去重。

完整登记中的统筹合法管理范围（如.ans/runtime和docs/scheduling）可以参与规范所有权核对，不因此成为普通执行writeFiles；统筹状态仍由Store路由统一写入，不能借文档许可直接改机器记录。治理覆盖资料也不属于允许的普通工作文件。

复用safe和规范相对路径检查，拒绝绝对路径、点段、反斜线、穿越、符号链接；未创建文件也核对现存父目录。保持全部Section 1权限的不重叠检查、批准配置与节点子集校验、授权/ack/changedPaths/候选/readSet/报告门禁。工具不提供OS沙箱，也不自动扫描所有架构缺陷。

## 配置与实际命令

在原执行配置中新增独立验收身份。下面只是配置片段，实际项目还须提供 `roles`、`designFiles` 和所需策略；替换全部示例路径与摘要：

```json
{
  "schemaVersion": 1,
  "schedulerRoleId": "scheduler",
  "acceptanceAuthority": {
    "roleId": "acceptance",
    "card": "role-cards/acceptance/role-card.md",
    "boundary": "role-cards/acceptance/boundary.md",
    "cardSha256": "<实际角色卡 SHA-256>",
    "boundarySha256": "<实际边界 SHA-256>",
    "credentialHash": "<可信端独立产生的验收秘密的 SHA-256>",
    "criteriaFiles": ["docs/criteria.md"]
  }
}
```

验收 `roleId` 不能等于 `schedulerRoleId`（省略时默认为 `scheduler`），也不能放在执行者 `roles` 中。摘要必须是实际文件摘要，`credentialHash` 为 64 位小写十六进制。独立测试执行者在 `roles.<roleId>` 标 `purpose: "independent-test"`；它仍有自己的 `card`、`boundary`、精确 `writeFiles`、`operations`、`autoDispatch` 和 `checks`，不能仅凭角色名称冒充测试身份。检查可配置 `argv`、1–300 秒的 `timeoutSeconds`（默认 60）以及字符串映射 `env`。

计划节点需有 `nodeId`、`roleId`、`operation`、精确 `writeSet`、非空 `checks`，可有 `stage`、`readSet`、`requiredOutputs`（默认等于写集合）和 `dependsOn`。`requirement`、`design` 各含真实 `path` 与非空 `version`；工具计算文档与角色定义摘要。`design.path` 必须在配置 `designFiles` 内。所有计划节点都属于本任务必需节点，没有取消必需节点就算完成的接口。

统一入口接受私密标准输入 JSON；不要把真实凭证明文写入聊天、命令历史或公开日志。下例只展示调用形式，需由可信调用端提供相应请求：

```sh
python3 /path/to/skill/scripts/task_ops.py --root /path/to/project --task repair-export init --request -
python3 /path/to/skill/scripts/task_ops.py --root /path/to/project --task repair-export status
```

| 命令 | 实际请求与结果 |
| --- | --- |
| `preflight-role` | 无任务只读命令，请求仅configPath；返回status/permissionsComplete/roles及issues；不授予写权 |
| `init` | `configPath`（默认 `.ans/project.json`）、`approvedConfigSha256`、完整 `plan`；可带至少 32 字符 `schedulerToken`，否则生成；返回 `schedulerToken`。拒绝请求中的 `coordinatorToken`、`acceptanceToken`、`acceptanceAuthority`、`credentialHash`，不返回验收秘密 |
| `accept-plan` | `acceptanceToken`、当前整数 `stateRevision`、`planRevision`、`criteria`、`customerApproval`、`requiredNodes`、`independentTests`；记录计划预检 |
| `dispatch` | `schedulerToken`、`nodeId`、`workerId`；非自动派发还须 `consent` 或 `consentPath` 及 `approvedConsentSha256`；失败/阻塞重试须 `retryReason`；返回一次性工作 `assignment` |
| `ack` | 工作 assignment 中的 `nodeId`、`attemptId`、`workerId`、`token`、`revisions`；确认实际分配版本 |
| `run-check` | 上述已确认 assignment 加 `checkId`；实际执行批准命令，返回检查 `evidence` |
| `report` | 上述 assignment 加 `reportId`、`kind`（`progress/issue/complete`）、`summary`，涉及改动时带 `changedPaths`；重复相同报告去重，旧批次/越界反馈拒绝并留历史 |
| `stop` | 自己的 `nodeId/attemptId/workerId/token` 和确认停止的 `summary`；暂停旧版时不要求新版本 acknowledgment，不杀进程 |
| `revise` | `schedulerToken`、`document`（默认 `design`，也可 `requirement`）、`version`、`affected`、`reason`；可有 `dependencies` 与部分修订的 `unaffectedReason`，对应修订须已在配置允许，文档内容必须实际改变 |
| `verify` | 仅 `acceptanceToken`、当前整数 `stateRevision`、`nodeId`、`attemptId`、`candidate`、`criteriaVersion`、`criteriaSha256`、`verdict`、`summary`、`criteriaResults` |
| `status` | 无请求；返回脱敏状态和当前有效性，不接受它替代客户授权 |
| `recover` | 仅新版 `schedulerToken`；验证并返回已有状态，不重置权限或代验收 |

非自动派发的同意回执必须匹配该次 `taskId/nodeId/roleId/workerId/operation/writeSet/planRevision/attemptNumber`，不能把一次同意跨批次重放。返回的 assignment 只交指定角色：除上述认证字段，还包含 `taskId`、`roleId`、`writeSet`、`card` 和 `boundary`。调度凭证与执行者凭证都不能调用验收命令。

`accept-plan` 请求例子（假设计划正好有 `repair` 与 `integration` 两个节点）：

```json
{
  "acceptanceToken": "<由可信端仅交验收的私密值>",
  "stateRevision": 1,
  "planRevision": 1,
  "criteria": {
    "path": "docs/criteria.md",
    "version": "C1",
    "sha256": "<实际标准文件 SHA-256>",
    "criterionIds": ["C1"]
  },
  "customerApproval": {"source": "<真实确认来源>", "reference": "<可追溯确认记录>"},
  "requiredNodes": ["repair", "integration"],
  "independentTests": [{"nodeId": "integration", "covers": ["repair"]}]
}
```

`criteria.path` 必须在批准 `criteriaFiles` 中，标准文件已存在且摘要一致，标准 ID 非空且唯一；`requiredNodes` 必须恰好覆盖全部计划节点。跨角色任务要求独立测试覆盖每个非测试阶段，测试 `readSet` 至少包含被覆盖阶段的 `writeSet` 与 `readSet`；生产测试的角色与被测角色不同。前期允许测试在无图上依赖时运行基线，但它获得 `pass` 及当前有效完成时仍必须等 `covers` 的阶段全部获当前有效通过；明确执行先后仍应使用 `dependsOn`。来源文字仅是可追溯引用，不是工具已认证客户身份。

验收从 `status.state` 取最新 `stateRevision`、节点 `attemptId/currentCandidate` 与预检 `criteria`。不能反复沿用例子里的版本值。阶段已报告完成并处于活动、未暂停的 `awaiting-verification` 时可提交三种结论；只有 `pass` 额外要求前置及其测试覆盖阶段全部有当前有效通过。依赖尚未通过或检查证据缺失时，可以据实记录返工或证据不足。例如：

```json
{
  "acceptanceToken": "<验收私密值>",
  "stateRevision": 7,
  "nodeId": "repair",
  "attemptId": "repair-1",
  "candidate": "<status 中该节点 currentCandidate>",
  "criteriaVersion": "C1",
  "criteriaSha256": "<当前标准 SHA-256>",
  "verdict": "pass",
  "summary": "<根据当前原始证据作出的判断>",
  "criteriaResults": [{
    "criterionId": "C1",
    "verdict": "pass",
    "evidence": [{"kind": "check", "checkId": "unit", "sha256": "<run-check 返回 evidence.sha256>"}]
  }]
}
```

当前 `criterionIds` 是任务级列表，每个节点的 `verify` 都必须回答全部 ID，没有按节点另传 ID 列表或 `not-applicable` 结论。标准文档应在预检前明确每个节点的阶段条件，例如：

| 同一个标准 ID | `repair` 阶段怎样判断 | `integration` 阶段怎样判断 |
| --- | --- | --- |
| C1 导出行为达到本阶段交接条件 | 已实现约定入口、数据与错误处理，相关单元/契约检查通过，可以交给测试；完整用户流程仍待后续阶段 | 对当前修复候选实际运行完整导出和失败场景，独立测试结果满足约定 |

开发节点的 C1 `pass` 只表示左侧交接条件已满足，不宣称尚未执行的完整流程通过；最终完成还要全部必需节点及独立测试的当前有效通过。不能在实施后随手把不满足的标准改成“不适用”来通过；标准尚未明确阶段语义时，先交原标准/设计所有者处理必要修订与重新建任务。

逐项结果必须与预检 `criterionIds` 一一对应。`pass` 要全部逐项通过且有非空证据引用；返工或证据不足也要逐项给 `summary` 或证据，至少一项结论与总 `verdict` 一致。引用支持三种形式：`check` 用 `checkId/sha256` 指向该阶段真实检查；`output` 用 `path/sha256` 指向该阶段写入或读取集合中的实际文件；`report` 用 `reportId` 指向该阶段最新报告。任意外部“成功日志”不能代替规定检查。工具核对身份、版本和引用，标准是否确实满足仍由独立验收负责，不会理解任意自然语言标准。

退出码：0 操作成功（含相同报告去重）；2 拒绝或错误；3 已认证但拒收的反馈；4 批准检查真实失败或改变候选。非零结果可能已记录失败事件，先查状态再决定重试。

## 计划与依赖

计划记录任务 ID、实际需求/设计版本、阶段节点、具体所有者、精确 `writeSet`、相关不变 `readSet`、产物、批准检查和前置节点。只包含当前任务；不为图好看而把整个角色绑为不可拆依赖。Harness、fixture 及影响结果的相关输入列入读取集合，避免它们变后旧证据仍看似有效。

独立验收在首次派发前核对客户确认的目标、标准、全部必需节点和所需独立测试覆盖，并固定当前计划快照。需求、设计或依赖修订后预检过期；重新核对前不继续派发、验收或放行依赖。新增角色、节点范围、检查或标准需要审核配置与新任务，不借修订扩权。

统筹每次派发先检查已确认方案与实施指令、角色授权或明确配置预授权、边界、当前依赖和写入碰撞，再预留具体范围。成功后可信启动端才将该次工作凭证交对应角色的新固定上下文。工具不是代理启动器；启动失败须先核对并确认旧写入者停止，不能直接再开一个重复写入者。

## 实际检查与三种验收结论

工作者先确认分配的版本，再运行配置固定 argv 的检查；不通过 shell 执行报告中的任意命令。记录候选、生产角色/工作者/节点/批次、起止时间、退出码、输出摘要和下述环境快照。失败、超时、候选被检查修改、无法执行和未测试均不算通过。开发自测不能冒充独立测试角色产生的完整流程证据。

### 环境证据v2：核对执行者的实际环境

新run-check证据增加 `environmentVersion: 2` 和 `environmentSnapshot: {path, sha256}`，不升级任务状态schema。程序只构造一次实际子进程环境：继承环境、批准check.env覆盖并强制PYTHONDONTWRITEBYTECODE=1；同一映射用于执行前后核对和subprocess。跟踪PATH、PYTHONPATH、NODE_PATH、NODE_OPTIONS、LANG、LC_ALL、TZ、PYTHONDONTWRITEBYTECODE及全部声明env键，区分有值与absent，不额外采集全部os.environ。

实际值仅存工具生成的 `.ans/runtime/check-environments/<task>/<attempt>-<check>-<nonce>.json`，目录0700、文件0600，路径不由请求者指定，safe校验并原子写入。任务记录仅保存路径/摘要、跟踪键集合、environment指纹、声明env摘要及执行文件身份；v2不写明文declaredEnvironment。完整环境、秘密值和私密快照不进入Git、报告、status或云端；配置check.env也不适合放明文秘密。

程序按项目cwd和捕获PATH解析首个可执行文件，记录canonical实际路径与文件摘要，固定该实际路径执行。合法系统可执行符号链接记录其解析目标，复核时须仍指同一实际文件和字节；项目输入路径仍由safe拒绝符号链接。执行后用同一捕获环境重新核对程序、平台/Python身份、候选和日志，记录environmentUnchanged；快照写入失败或程序过程变化不能生成有效通过证据。

status、verify、依赖消费使用同一有效性逻辑：先核原有批准配置、定义、标准、产物、writeSet/readSet、producer/attempt、报告、日志和验收关联，再核私密快照路径/形状/键及absent语义/摘要，最后在原捕获环境下重核执行文件、声明环境、平台与Python运行身份。查询者PATH、LANG等不会替换原检查环境。仅查询者PATH写法不同且原对象不变不误失效；实际程序路径/内容、声明env/批准配置、快照、相关源码/资源/readSet或日志改变仍当前无效。平台/Python改变可保守失效，不承诺跨机器复用。

只有**没有environmentVersion字段**的legacy证据继续按旧environment(root, check)重建查询进程环境比较，原PATH差异仍可能失效。v2快照缺失、损坏、错误形状或摘要不匹配，及未知environmentVersion，均直接当前无效并说明原因；绝不回退legacy或查询者环境，不补写快照，不从旧variablesHash反推原值或追认旧通过。私密快照丢失或换机器无法恢复时，用新审核任务真实复测。

若需实际换检查环境，只有既有状态机允许且仍active的assignment可真实run-check并记录新快照，随后由独立验收对新证据重新verify，不能沿用旧acceptance。candidate/attempt没变时，完成报告沿用既有门禁，不新增通用report与environment绑定系统；verified节点已非active，不能原批次重开/重跑，须新审核任务。check.env或批准配置变更同样需要新审核任务，不改configHash伪装未变，也不编辑快照切环境。

工具代码、批准入口及相关配置/资源需列入readSet；间接工具和其他必要文件也明确声明。继承但未跟踪变量、未声明的动态依赖、数据库和远程服务等不在自动检测承诺内；额外必要变量放批准check.env，文件放readSet。保留全部原检查和失败历史。

完成报告只把节点交给待验收，不能释放业务依赖。验收结论须指向当前计划、标准、候选、批次、完成报告和检查证据，并核对预期状态版本，避免看完旧成果却通过新成果。

| 结论 | 阶段与后续 |
| --- | --- |
| 通过 / `pass` | 仅在原有门禁和全部标准满足时记 `verified`，释放该阶段预约和依赖 |
| 返工 / `needs-work` | 保留原始差异，阶段阻塞；原执行者确认停止后可释放写预约，由统筹按具体返工原因重新派发 |
| 证据不足 / `missing-evidence` | 保持待验收和预约，明确缺什么；当前执行者可在原范围补检查和报告，需要换人或改实现则先停再派发 |

停止确认只释放停止后的写预约，不代表完成、不真实杀进程，也不放行业务依赖。任务完成从全部必需节点的当前有效通过结论派生，统筹没有“直接关闭”捷径。

候选、需求、设计、标准、角色定义、批准配置或必要证据变化，使受影响结论过期。核对包含直接和传递前置节点，不能只看下游文件未变就忽略祖先日志已丢失。旧结论保留历史，不改哈希冒充当前通过。换机器时缺本地原始输出，也要补齐所需证据后再继续。

## 修订与恢复

1. 统筹接收原始问题，暂停受影响依赖；设计或需求文件由其真实所有者修改。修订操作只记录实际新版本和影响，不代写方案。
2. 活动受影响阶段保留写预约，先核对实际工作者，在安全位置停止并用旧分配确认停止；旧批次反馈保留历史但不能覆盖新版。
3. 独立验收复核修订计划与完成标准；统筹重新授权和派发，新批次重新确认、执行必要检查、报告并申请验收。
4. 非影响节点继续需有可核对理由并由新预检复核；不能用“没有影响”的自述绕过真实依赖。

所有写入仍按加锁、校验、提交、原子替换更新一份 `docs/scheduling/<task-id>.md`，包含计划、可读状态和有序机器事件。校验事件顺序、哈希和可读区；原子替换失败保留上一份完整记录，先查状态再重试。恢复只核对已有记录，不发明未提交事件、不恢复丢失凭证或代作验收。

任务记录可随 Git 保存，本地锁和完整检查输出在被忽略的 `.ans/runtime/`。同任务 Git 冲突或人工改写必须先核对，不自动覆盖一方。私密凭证由可信端另外携带；运行中的写入者及本地证据不会自动迁移。

## 旧任务和实际边界

新任务状态为 v2。`status` 可按原 v1 渲染校验读取 Markdown；没有同名 Markdown 时，`Store.load` 可读取 `docs/scheduling/<task-id>/plan.json` 与 `state.json` 的旧目录格式，只读展示，不声称验证旧 JSON 的完整事件链。旧状态返回 `legacyReadOnly: true`、`taskComplete: false` 及原流程验收说明；所有非 status 命令（包括 recover）拒绝旧状态，不原地改凭证、复制旧 verified 或追认为独立验收。继续旧工作时，先核对并停止旧执行者，再用新 ID、已审核配置、角色、计划和标准建立新任务，补齐所需测试与验收。旧记录只链接为历史。

v2 不写旧 `coordinatorTokenHash`、assignment `tokenHash` 或历史批次的旧字段，分别使用 `schedulerCredentialHash`、`assignmentCredentialHash`；不保留旧请求别名绕回协调者自验收。真正旧脚本对 v2 的拒写仍需独立回归证据。新程序不能远程撤销同 OS 用户磁盘上的旧程序，迁移方还需停用旧执行入口。工具也不能阻挡能改可信配置、源码和全部哈希的同 OS 操作者；实际工具与文件权限承担预防边界。

Dashboard 继续只读展示同一记录；云端一个项目 Key 和管理员网页决定不是本地调度、执行或验收凭证。云端同步仍由用户主动决定。

## 实际验证入口

开发与回归使用 `python3 -m unittest discover -s scripts/tests -v`，真实 CLI 由独立测试角色检查。隔离 Timer 回放脚本为 [validate_task_flow.py](../scripts/validate_task_flow.py)，输入与现有源码保持只读；支持 TypeScript stripping 的实际 Node 路径由运行方提供。回放不是浏览器、DOM 或 TypeScript 编译验证。

既有分权接口与本轮新增接口的核对状态分别见本文开头及[D1](../角色卡/项目管理/docs/design/2026-10-20_design_workflow-fixes.md)。以下是2026-10-19既有工作事实，不作为本轮修复的通过结论。[开发者原报告](../角色卡/任务工具/docs/change/2026-10-19_change_task-authority.md)已记录 49 项单测和隔离 timer 回放通过；回放使用子进程、标准输入 JSON 调用真实 CLI，并使用独立测试角色。固定测试的实际命令、受测候选、结果和限制以其[原报告](../角色卡/测试/docs/change/2026-10-19_change_role-authority-split-validation.md)为准，当前正在整理最终证据；独立验收尚未给终验结论。开发自测和接口说明不代替独立 QA 或最终验收。
