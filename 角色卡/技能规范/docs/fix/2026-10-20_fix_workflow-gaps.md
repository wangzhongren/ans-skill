---
id: skill-spec-workflow-gaps-fix
type: fix
title: 角色工作文档适用范围与交接预检的规范评估
created: "2026-10-20"
updated: "2026-10-20"
timezone: Asia/Shanghai
status: implemented-unverified
related: [workflow-friction-product-p1, workflow-fixes-d1, role-authority-split-feature]
events:
  - date: "2026-10-20"
    kind: created
    summary: 技能规范 owner 只读核对现行规则，提出职责适用与最小同步建议
  - date: "2026-10-20"
    kind: implemented
    summary: 客户确认D1后同步获准规范与当前说明；未运行程序测试，独立验收待交付
---

# 角色工作文档适用范围与交接预检的规范评估

## 已授权的规范同步

客户已确认“确认，按方案完成修复和验证”，覆盖P1、D1-final-1、C1与QA-T1-draft-1。本角色据[D1第6节](../../../项目管理/docs/design/2026-10-20_design_workflow-fixes.md)仅同步以下11份获准文件：SKILL.md、SKILL.zh.md；references下bootstrap-workflow、role-card、module-boundary、task-operations、team-formation、api-spec、scheduler共7份Markdown；本角色当前[角色权责说明](../feature/role-authority-split.md)及本修复记录。

规范现已明确默认feature-map/memo/functional-description、有依据适用或不适用的api-spec、完整roleDefinitions与精确requiredWorkDocuments只做预检、真实card/boundary父目录识别、交接前只读工具路由、精确任务文件交集和保护集合。根治理changelog从执行者交付物和目录树注释中移除，继续由团队组建独占；owner历史仍写自身docs。

任务操作说明按工具owner交付字段同步：preflight-role请求仅configPath，无task；返回status、permissionsComplete、roles（documents/issues）及全局issues，失败exit2且不产生运行文件。合法统筹管理范围可参与规范所有权核对，普通writeFiles仍不能申请状态/配置。环境证据使用environmentVersion=2及environmentSnapshot={path,sha256}，缺坏快照或未知版本直接无效；仅无版本legacy保留旧比较。verified换环境用新审核任务，不新增状态或报告绑定系统。

本轮修改的是规范文本与当前说明；程序实现和单元测试由任务工具owner负责，独立CLI与隔离库存60项由QA负责，验收由独立角色负责。本文不声称它们已通过，也不重写原失败历史。没有修改源码、测试、角色治理、README、evidence、架构指南、旧库存、已安装技能或public，没有init、push或install。

## 本角色真实轻量核对

对11份获准文件核对：全部有本角色Section 1精确条目；200个本地Markdown链接目标存在；没有行尾空白或未闭合代码围栏；限定这11路径的git diff --check通过。另只读定点检查task_ops.py的definitions_for、preflight_role、operate只读分支、environment身份与snapshot分流，响应字段、缺坏v2不回退及声明字段与工具owner交付一致。此为规范/接口核对，没有运行程序检查，不替代独立CLI、库存回归或验收。

## 配置准备归属的同范围定点修正

后续定点复核发现：初始化禁止团队组建写application/configuration，但新增预检段落却写其在配置中准备roleDefinitions，容易暗示治理取得配置写权。现已统一相关入口：团队组建只提供完整登记内容与角色权限；已接受统筹在自己的边界内落候选配置。新项目先接受统筹定义，独立固定统筹上下文仅准备配置，随后只读preflight齐全，再交接/派发其余实际工作；已有项目由原统筹写配置。旧迁移句也明确按原owner分别修改定义和配置。

本次只澄清已有批准的owner与入口顺序，不增角色、源文件或审批，不改工具、批准快照、隔离项目或冻结节点候选；没有重跑程序套件。本次9份定点文档的190个本地链接目标存在、无行尾空白，限定这些路径的git diff --check通过。

## 准备阶段独立评估（保留当时结论）

以下记录来自客户实施确认前的只读准备阶段，“当前/本回合/尚未”等状态指该阶段；其适用清单建议已由D1最终字段和上节实施记录承接，不能据旧措辞覆盖已确认决定。

本评估针对交接时漏掉角色自己的工作文档权限、任务工具拒绝已获准角色文档、普通 PATH 查询造成验收误失效三项实际摩擦。建议沿用现有任务工具与审核配置，但必须把“角色需要维护哪些文档”“谁授权这些路径”“本次任务实际能改哪些文件”分开说明。清单和预检不能变成新授权源。

本文由固定技能规范角色撰写，仅修改本文件。源码基线由统筹指定为 `main d95d006`；没有修改 SKILL、references、角色定义、程序或测试，没有初始化任务，也没有安装或发布。本文形成时未收到 PM D1 正文，以下是对统筹转交提议的独立规范建议，不是 D1 审核结论。产品目标见[策划 P1](../../../策划/docs/design/2026-10-20_design_workflow-friction-product.md)，工具可行性由[任务工具 owner 评估](../../../任务工具/docs/fix/2026-10-20_fix_workflow-gaps.md)负责。本角色现有相关功能入口见[功能导航](../../feature-map.md)、[角色权责拆分说明](../feature/role-authority-split.md)和[法案与 memo 说明](../feature/project-rules-memo.md)；这些当前说明没有被本文提前改写。

## 已有规则哪里不够清楚

1. [初始化规则](../../../../references/bootstrap-workflow.md) Path A 第 3 步明确 grant feature-map 与 docs 子树，目录图却还列 memo；Path B 要求 functional-description 说明当前结构。规则没有把这些根工作文档的明确授权串成同一检查，容易得到“应交付但没有写权”的角色。角色卡要求交付并不意味着 Section 1 自动授权。
2. [模块边界](../../../../references/module-boundary.md)明确 functional-description 是边界的伴随描述，适用于统筹、PM、验收等项目角色，不只代码开发者；但其白名单示例仅示范 feature-map 与 docs，没有 memo、functional-description 和适用 api-spec。示例未授予隐含权限，后续应补齐的是可核对的清单和示例。
3. [角色卡模板](../../../../references/role-card.md)第 4 个执行检查点、Deliverables 与目录树，把根 changelog 写成角色执行阶段交付；同文件随后又规定它记录角色创建、边界调整、拆分与合并。[本仓库治理边界](../../../governance-boundary.md)逐项把各根 changelog 授予治理 owner。因此这是模板归属歧义，应改模板，不能据此给执行角色增权。角色自己的 `docs/change/`、`docs/fix/` 工作历史与根治理 changelog 不同。
4. [API 指南](../../../../references/api-spec.md)实际针对 implementation owner 的真实导出、依赖、装配与合同实现报告；角色卡模板却没有说明非实现角色何时不适用。这会把纯协作角色误导为必须编造导出或代码层。

## 工作文档必须项与不适用项

下表是供 PM 定案的适用原则，不是本轮角色扩权决定。实际路径仍须由团队组建按现有授权落实到 Section 1，并同步 YAML。

| 文档 | 建议适用性及所有者 | 如实表达方式 |
| --- | --- | --- |
| 自身 `feature-map.md` | 默认每个项目角色需要，由角色自己维护 | 没有直接拥有的系统功能时明确写“本角色没有直接负责的系统功能”；不把调度、评审或测试职责伪装成产品功能，不强制生成虚构 feature 文件 |
| 自身 `memo.md` | 默认每个项目角色需要，由角色自己维护 | 文件可只说明当前没有需保留的续接线索，不为每次工具调用造记录；不能代替全局状态或 PM 法案 |
| 自身 `functional-description.md` | 默认每个项目角色需要，由角色自己维护 | 开发者记实际能力与代码位置；纯协作角色说明自己的职责、真实交接输入输出和文档位置，并明确“无自身代码模块”；链接现有导航和 PM 架构，不复制全项目架构 |
| 自身 `api-spec.md` | 有真实跨角色程序能力、导出或装配接口的实现 owner 适用，包括 PM 的实际 shared 能力；纯协作角色可显式不适用 | 写明“不适用：无对外程序接口或装配接口；协作交接见 functional-description”；不能只漏填，不能把一份拟议接口写成已实现 |
| 自身 `docs/feature/`、`docs/design/`、`docs/change/`、`docs/fix/` 等 | 按真实职责给有界路径，不机械要求所有角色拥有全部子目录 | 策划方案、测试报告、验收标准/结论、PM 架构等仍按各自实际职责和既有授权维护；未出现的工作不为凑清单制造文档 |
| `role-card.md`、`boundary.md`、同名 `boundary.yaml`、根 `changelog.md` | 治理 owner 独占 | 这些是保护资料，不是执行者可写的根工作文件；同步 YAML 也不成为第二授权源 |

“API 不适用”应在角色建立/交接时有可追溯依据，由团队组建与职责定义核对，角色可以提出事实说明，不能执行时临时删项来绕过缺权检查。`workDocuments` 若最终只是精确路径数组，可以只列适用文件，把不适用原因写在现有角色定义/交接资料并被审核配置引用；不必为此新建配置文件或发明空 api-spec。具体字段形式由 PM 明确，不能假称工具能从自然语言自动判断职责。若缺少适用性决定，应报告“待确认”，而不是把空清单当角色完整。

feature-map、memo、functional-description 是本次建议的默认交接要求；这不等于宣布现有全部角色立即违规或获得新写权。已接受的旧边界若漏项，按实际差额由治理 owner 调整后再进行受影响写入，不批量迁移历史样例。内置团队组建继续沿用自身内置职责与边界例外，不为它再建一张项目卡。

代码架构规则保持现状：不要求纯协作角色建立代码层，不要求每个功能凑满五层；真正使用 Service/Provider 的能力，仍须满足 `abstract/`、`public/`、`impl/` 和相邻层调用规则。其依据是[现行架构规则](../../../../references/architecture.md)，本轮没有必要修改该规则。

## 预检与实际写权如何衔接

赞同复用 `task_ops.py` 的只读 `preflight-role`，在现有审核配置可选增加全角色 `roleDefinitions`，登记真实 card、boundary 和适用工作文件的精确项目相对路径。不要新建第二份权限配置。登记应覆盖项目实际角色，包括非执行者、统筹与验收；由团队组建提供真实项目角色范围，不能只枚举本次 `roles`，也不能把隔离样例仓库递归混进项目角色。登记完整性可核对到什么程度、遗漏如何报告，需 PM 明写工具能力边界。

`workDocuments` 只表达需要检查的适用文件，不授予权限、不复制 Section 1，不要求拟创建文档已经存在。预检应检查其归属、保护冲突和实际边界覆盖；读到缺项时给具体路径和原因，并交团队组建处理。不应因为文件尚未创建就让获准 owner 永远无法接手创建；授权完整与内容完成是两种检查。

实际任务可写范围仍取交集：自身有限根工作文件或自身 `docs/` 子树 ∩ 实际 `boundary.md` Section 1 ∩ 审核配置精确 `writeFiles` ∩ 当前节点精确 `writeSet`。同时满足任务授权与已有版本/保护门禁。根工作文件建议限于上表前四种，不开放整个角色根。dated docs 可在已接受的有界目录内长出新文件；没有在初始化 workDocuments 中逐份预列未来历史文件，不应否定原有目录授权，但本次文件仍须精确进入配置和节点。

所有角色治理文件、其他角色工作资料、`.ans`、统筹状态与任务机器记录继续保护。统筹维护状态只能通过既有任务工具路由；即使调度文件位于其自身 docs 中，也不能借普通工作文档路径直接修改状态。项目自定义治理/状态实际位置须纳入保护判断，不能只保护示例英文目录。具体安全校验与实现由任务工具 owner 负责。

“交接前真实工具可检”需要落到现行路由：团队组建提交定义前可只读预检；定义接受、登记配置可读后，在交给新统筹或角色上下文前，对实际将交接的角色执行预检并传结果。缺权返回治理，未决定适用性返回职责定义 owner；不能把成功结果当客户批准、派发或验收。统筹后续安排需要角色文档的任务时复用同源检查，init 亦核对该规则。预检本身不依赖已建任务，不产生锁、runtime、日志或状态写入；这是待实现要求，当前没有此命令的执行证据。

PATH 修复的规范要求由用户结果约束：相同实际执行对象下，仅查询者无关 PATH 原文不同不应推翻验收；实际程序、相关环境、源码/readSet、批准配置、日志等必要证据变化仍失效，无法判断相关性时说明原因并保守视为当前无效。不要把“忽略 PATH 字符串”写成“忽略环境变化”，也不要声称能核对所有外部库、远程服务或系统状态。运行资料格式及新旧证据兼容由 PM 和工具 owner 定案；不能改旧哈希来追认。

## 最小规范同步建议

下面是按上述方案实施时应同步的具体位置；本回合没有修改这些文件，也不据此认定客户已经确认方案。

| 精确路径 | 最小必要内容 |
| --- | --- |
| `references/bootstrap-workflow.md` | Path A/B 同一套适用文档与 Section 1 覆盖检查；给出默认三项和 API 条件；把真实只读预检放入接受/交接节点，区分定义候选与接手写作，不以内容预先完成为权限检查前提 |
| `references/module-boundary.md` | 白名单示例补 memo、functional-description、条件 api-spec；明确有限根文件、有界自身 docs、治理与状态保护，清单不授权；保留 Markdown 唯一权威及 YAML 原规则 |
| `references/role-card.md` | 执行检查点、Deliverables、目录树三处一致区分根治理 changelog 与 owner 工作文档；明确协作角色 functional-description 的真实写法、API 不适用及交接检查；不把模板变扩权条款 |
| `references/api-spec.md` | 加职责适用条件和显式不适用说明；保持 PM 合同设计与 owner 实现报告的归属 |
| `references/team-formation.md` | 团队组建交接全角色登记/适用性依据并调用真实预检；“职责说明”区分治理定义与 owner 后续 functional-description，避免让治理接管角色工作文档 |
| `references/scheduler.md` | 接手与“查授权和范围”步骤链接同源预检；缺项交治理，不代改；状态继续由 task_ops 唯一写入 |
| `references/task-operations.md` | 以最终实码说明可选登记、无任务只读 preflight-role、准确参数/结果、有限文档交集和保护拒绝；更新当前环境比较段落，明确新旧证据分流、真实失效条件与局限 |
| `SKILL.md`、`SKILL.zh.md` | 在角色边界/初始化/交接入口简述适用文档与真实预检并链接上列唯一详细规则，保持中英文一致，不复制完整配置契约 |

实施后，`references/governance-changelog.md` 可按真实完成和验证状态追加这一轮规范变更事实；它是技能规范产品历史，不是各角色根治理 changelog。当前角色功能说明和导航只有在对应行为实际交付后按已获准范围同步；如涉及尚未获准的新功能文件，应先报精确路径，不能利用本次评估文件授权扩写。

无必要改 `references/architecture.md`、`references/feature-point.md`、`references/role-memo.md`、`references/built-in-boundary.md` 或其 YAML：现行代码层规则、无直接系统功能的表达、memo owner 和治理规则已足够。README 当前仅导航，不列冲突的执行配置或环境算法，可保持现状。各实际角色 card/boundary/YAML/changelog 若需补权，由治理 owner 按差额处理；PM 的 project-rules、工具程序与测试各由原 owner 维护，本角色不代改。

## 当前状态与旧证据

依据是上述现行规范与[旧实测观察](../../../../../ans-full-trial-2026-10-19-bqf0vjof/角色卡/scheduler/docs/handoff/2026-10-19_trial-observations.md)、[旧最终交接](../../../../../ans-full-trial-2026-10-19-bqf0vjof/角色卡/scheduler/docs/handoff/2026-10-19_final-handoff.md)的只读内容。旧交接记录 stateRevision 93、taskComplete=true、60 个测试方法、77 次调用和 20 个源码及测试文件；本文保留这些既有事实，不声称本轮重新运行或当前环境再次验证。

当前仅完成规范 owner 准备评估，待 PM 将适用性、保护集合、实际调用路由与环境算法写入 D1 后核对。没有实施，没有运行程序测试，没有 QA 或独立验收结论。最终实现范围仍待客户确认；本评估没有新增选装，也没有请求扩大任何角色权限。
