# ANS Skill

一套受 [Role-First Software Governance（RFSG）](https://zenodo.org/records/22824700) 论文启发的 AI 开发技能：先明确谁对功能负责、允许改什么，再组织代码、实现需求，由项目管理角色说明整体架构，各开发角色用功能文档和流程图解释实际行为。

[中英文介绍页](https://wangzhongren.github.io/ans-skill/)

## 为什么这样设计

AI 可以跨模块阅读代码、追查问题，但“看懂了哪里”和“有权修改哪里”需要分开。比如排查工单保存失败时，可能一路查到存储模块；找到原因后，仍应由拥有相应职责和权限的角色完成修改。

Role-First 论文提出了从角色和职责出发建立权限与代码归属的治理思路。ANS 从中吸收了三点：

1. **先确定责任，再确定代码归属。**先问谁对这项业务行为负责，再明确它需要哪些模块和文件。
2. **按需广泛阅读，在授权范围内修改。**排查时可以在实际读取权限内跨模块了解情况，当前上下文只加载任务需要的内容。
3. **发现问题后，交给负责的角色处理。**理解另一个模块的问题，不会自动获得修改它的权限。

在本项目中，这些思路落成了角色卡、文件边界和跨角色协作规则。五层代码组织、先写方案、角色功能文档和流程图，是 ANS 为项目开发选择的具体做法；它们不是论文要求的固定目录或工具。

## 角色管责任，分层管代码

可以把角色理解为项目里的事业部门或能力团队，例如工单、支付、库存、平台接入、数据存储。角色有稳定的职责、公开约定和文件范围。分析、设计、编码、测试是它在任务中开展的工作。

**角色回答“谁对结果负责”，代码分层回答“不同职责的代码怎样协作”。**一个角色可以跨多个层，不需要一层配一个角色。

以保存工单草稿为例：

| 需要完成的事 | 负责角色 | 代码职责 |
| --- | --- | --- |
| 接收页面输入 | 工单角色 | Interface：入口 |
| 组织保存过程、处理结果 | 工单角色 | Pipeline：流程组合 |
| 检查内容和业务规则 | 工单角色 | Service：业务规则 |
| 读写草稿记录 | 存储角色 | Provider：外部资源 |
| 定义草稿数据 | 指定的 Model 拥有者 | Model：供各层共享的数据定义 |

运行时遵守以下调用方向：

```text
Interface → Pipeline → Service → Provider
Model 供各层共享
```

角色边界落实到具体业务文件，以及明确归属的 common 和测试目录，调用通过约定好的公开入口完成。一个功能不必在每层新建文件；已有项目沿用实际目录，不为套模板搬迁代码。

角色是一份职责和权限定义。**一个对话或代理上下文从绑定开始到结束只能承担一个角色，禁止在同一上下文来回切换。**其他角色通过独立子代理或新上下文承接工作；可以按顺序运行，不要求多个模型同时启动。续接对话、任务结束后继续使用或上下文压缩，都不解除角色绑定。读取其他角色资料只是参考，不授予它的权限。

每张角色卡用 `group` / “组别”字段标明常协作的角色。角色保持平级，权限仍看各自边界第 1 节；组别只说明协作关系。角色卡示例：

```markdown
# 售后角色
组别：订单组
```

组别只用于分类，不设置组长或组内职责。统筹直接评估每个角色的工作量、逐角色授权和范围预留、派发任务并接收反馈；角色之间不增加汇报层级。角色数按已接受的定义计算，开多个同 `roleId` 上下文不等于增员。需要新角色时，统筹把缺口交团队组建按已获准范围建立。详见[团队组建](references/team-formation.md)与[统筹](references/scheduler.md)。

每张角色卡也明确一个共同的工作立场：**你是所负责部分的长期维护者，参与的是会被真实使用、持续修改的正式项目。**从实际使用、与现有系统配合和后续维护出发判断怎样设计与实现，对自己的交付负责。详见[角色的工作立场](references/role-card.md#working-stance-for-every-role)。

## 角色自己的框架和大家共用的代码

工具函数和基础框架统一放在 `common/`，不再新建独立的 `utils/`：

```text
src/common/
  order/          # 工单角色维护自己的工具与框架
  messaging/      # 消息角色维护自己的工具与框架
  shared/         # 项目管理角色维护跨角色共用的组件
```

目录经过授权后，角色可以在任务范围内新增、拆分和整理内部文件，不必为每个文件重改角色边界。具体业务规则仍放在五层里，common 不能反过来调用业务层。

跨角色复用由项目管理设计并编写 `shared/`、对应单元测试和共享组件文档，再由统筹安排各角色修改自己的调用代码。它不能直接改其他角色的业务代码。项目管理角色自己的 `docs/architecture/shared-components.md` 记录组件用途、入口、使用角色、输入输出、例子、测试和修改影响。目录和权限变化仍由团队组建角色处理；已有项目不会因为升级技能就自动搬迁代码或扩大权限。

## 谁来安排，谁来判完成

治理、统筹、架构、测试和验收各管一件明确的事：

| 角色 | 负责什么 |
| --- | --- |
| **ANS 团队组建** | 按已获准需要建立角色、组别和文件边界；不派发实现或验收交付 |
| **统筹** | 主聊天默认接需求，调查影响和工作量，安排逐角色授权、范围预留、进度与返工 |
| **策划** | 后续新需求的问题、用户目标、完整产品流程分支、输入输出、范围和可选项方案 |
| **项目管理** | 技术架构、实现设计和技术评审、工程法案，以及 shared 代码和它的测试 |
| **开发／装配** | 实施自己负责的代码和单元测试，或构建、接线与启动检查 |
| **固定测试** | 实际运行跨角色联调、完整流程和回归，保留成功、失败与未测记录 |
| **独立验收** | 实施前说清怎样才算完成，交付时根据当前版本和原始证据判通过、返工或证据不足 |

统筹安排测试和修复，代码由原所有者修；测试角色复测，独立验收判断成果。工作者说“做完”或测试退出成功，都不自动让整个任务完成。统筹凭证不能把自己的安排验收通过；独立验收也不能派发实现或修改代码让它通过。

**招聘与边界调整由独立内置 ANS 团队组建（原 ANS Governance）负责。**它承接原治理身份，不增设第二个重叠岗位，也不是组长或项目管理的附带职责。其他职责是可复用模板，由团队组建在具体项目落实为独立的角色卡和边界。模板不授予全局写权，也不意味着始终运行固定数量的 Agent。角色可按需顺序参与；普通小任务不要求全员开会。详见[团队组建](references/team-formation.md)、[统筹规则](references/scheduler.md)、[策划方案](references/planning-role.md)、[架构职责](references/project-role.md)、[固定测试](references/test-role.md)和[独立验收](references/acceptance-role.md)。

## 日常开发怎样进行

在项目里调用 `$ans-governed-construction`，直接说明需求，例如：

> 使用 $ans-governed-construction，调查保存草稿失败的问题，先写修改方案。

1. **调查与分工。**团队组建维护角色定义和文件边界；统筹接待和调查需求，把后续新需求交策划形成产品方案，再交项目管理做技术架构、实现设计与技术评审；独立验收先明确完成标准。
2. **先讲产品，再定技术。**策划写用户要完成什么及完整流程，项目管理写技术上怎样实现；客户确认并授意实施后，统筹安排各所有者工作。同版同范围已有授权不重复问，也不重写本轮已完成的原技术方案。
3. **必要改动与选装分开。**额外兼容、兜底或扩展必须在文档和聊天总结里说明好处与代价。默认勾选只是推荐，客户同意后才加；取消的选装不重新勾选。
4. **实现、真实测试与验收。**各角色实施并交当前证据；固定测试运行联调与回归，独立验收按标准判定。各所有者更新自己的功能和历史文档，项目管理维护架构，统筹按验收结论安排返工、补证或交付。

客户负责确认需求和范围；各角色对应的 AI 核对代码、维护自己的 Markdown 文档和图。图来自实际行为，不靠按钮名或文件名猜流程。

新项目按四步开始：

1. 团队组建写好角色及权限，准备完整的角色登记内容。
2. 确认统筹角色，由它在自己的权限范围内准备项目配置。已有项目由原统筹更新配置。
3. 运行只读预检，发现漏权或冲突就交原负责角色修正。
4. 预检通过且已获授权后，统筹安排各角色开始工作。

每个角色使用独立、固定的对话或代理上下文。统筹只传角色、边界、有效授权和任务所需资料，执行者直接报告结果。无法使用子代理时，可由独立新上下文顺序接手；无法创建时就报告待办，不在原上下文切换角色。

预检会指出角色自己的工作文档哪里缺权、哪里与其他角色或治理资料冲突，不创建任务、锁或运行日志。例如，在技能仓库目录下检查项目配置：

```sh
printf '%s\n' '{"configPath":".ans/project.json"}' | python3 scripts/task_ops.py --root /path/to/project preflight-role --request -
```

把 `/path/to/project` 换成实际项目根目录；配置须含完整角色登记。预检通过表示权限检查齐全，不表示文档已写完，也不替代客户批准或派发。详见[初始化与交接](references/bootstrap-workflow.md)及[任务操作](references/task-operations.md)。

旧项目须先盘点现有角色、配置和运行中的任务，明确迁移后再交接。旧 PM 上下文不自动变成统筹或验收，旧任务历史不冒充独立验收结果。工具旧版任务保留只读，继续执行须核对并停止旧写入者、按新授权建立新任务并补齐必要证据。

## 按角色看架构，按功能看流程

项目管理角色在自己的 `docs/architecture.md` 解释整体结构、角色职责、接口和配合关系，并链接各角色的 `feature-map.md`。

每个开发角色沿用自己的 `docs/`：

```text
角色卡/工单/
  role-card.md
  boundary.md
  boundary.yaml
  memo.md
  functional-description.md
  api-spec.md             # 有实际对外代码能力或装配接口时维护
  feature-map.md
  docs/
    feature/
      save-draft.md
      submit-order.md
    design/
    change/
    fix/
```

1. **导航找功能。**`feature-map.md` 列出功能名称、一句话用途、状态和链接。
2. **上面讲用途，下面讲过程。**`docs/feature/save-draft.md` 先讲为什么保存草稿，再用 Mermaid 流程图和短句说明触发、步骤、判断分支、输入输出及角色交接。
3. **从功能查看历史。**文末按时间记录变化，链接本角色 docs/design、docs/change、docs/fix 中的详细记录；历史文档也链接回功能。

功能文档使用稳定文件名，主体保持最新，历史持续追加。设计、修改和修复记录带日期；待实施方案不能提前替换当前流程。需要恢复某一时刻的完整文档和代码时用 Git。

不再新建角色根目录的 `features/`，不再要求维护架构 JSON、content.json 或项目理解数据库。现有历史文件在批准迁移前保留。详见[功能文档写法](references/feature-point.md)。

## 项目工程法案与角色备忘录

项目工程法案是**全项目角色共同遵守的工程约束**，由项目管理角色在自己的角色目录下维护唯一的 `docs/project-rules.md`。其他角色从项目管理角色卡或正式文档引用并读取同一实际路径，不在各自目录另建法案。每条规则写清适用范围、要求、正确做法和检查方式，并使用稳定编号或名称；理由按需补充。

法案只记录有实际项目依据、并已按项目流程确认的约束。草稿和建议要标清状态；项目没有确认的做法不会因为写进技能或示例而自动生效。比如，GUI 主线程示例只适用于确认采用相应 GUI 运行模型的项目；单纯给函数加 `async` 不会把重计算移到后台，也不表示所有项目都禁止主线程工作。

初始化时先建立并确认项目管理角色及其边界，再由项目管理调查和整理法案；缺少法案不阻止项目启动或已有授权的工作。每个角色开始或续接任务时，阅读自己的 `memo.md`，并按项目管理角色卡找到同一份法案及本次相关条目；法案缺失时如实报告，继续遵守通用规则和项目已确认约定。角色只维护自己的 memo，留下少量有日期、有来源的事实、待核实事项和继续线索。Memo 不是全局规则或任务状态表，新增全局约束仍交项目管理评审并写入法案。

本仓库本轮采用的实际[项目工程法案](角色卡/项目管理/docs/project-rules.md)、技能规范角色维护的[功能说明](角色卡/技能规范/docs/feature/project-rules-memo.md)和[最终独立验证报告](角色卡/测试/docs/change/2026-10-10_change_project-rules-memo-validation.md)可供查看；详细使用方法见[法案指南](references/project-rules.md)和[角色 memo 指南](references/role-memo.md)。

## 本仓库的实际分工

维护 ANS 产品时同样按文件归属协作：团队组建维护真实角色卡和边界，策划维护后续新需求的产品方案，技能规范维护入口与指南，任务工具维护任务程序，测试运行独立检查，验收核对标准和证据，统筹协调各自的交接；项目管理维护本仓库的[架构](角色卡/项目管理/docs/architecture.md)与[工程法案](角色卡/项目管理/docs/project-rules.md)。这些是本仓库的分工，其他项目按实际职责建立自己的角色。

角色分工的[设计方案](角色卡/项目管理/docs/design/2026-10-19_design_role-authority-split.md)和[技能当前说明](角色卡/技能规范/docs/feature/role-authority-split.md)可供查看。所有角色在独立固定上下文中，只改自己边界允许的文件。

2026-10-20 的[工作流修复独立验收](角色卡/验收/docs/acceptance/2026-10-20_workflow-fixes-result.md)已通过。源仓库完整测试 236 项，其中包含开发 69 项和独立 CLI 40 项；库存隔离副本另跑 60 项回归，并完成两个真实节点的独立验收。

## 项目管理先审核，再交客户审批

后续新需求先由[策划](references/planning-role.md)形成产品/需求方案，项目管理承接其方案做技术架构、实现设计和技术评审。各实现角色提交具体提案后，项目管理核对需求、整体架构、已有可复用能力和跨角色影响，判断是否有更合适、代价更小的方案。影响接口、数据或其他角色行为时，请相应角色在独立上下文里评审；必要且已授权时用 meeting 解决分歧。需要修改的方案交回原负责角色，不能由项目管理越权代改。

项目管理对方案给出“建议通过、需要修改、暂不能通过”的建议，再把适合审批的方案缩略给客户：要解决什么、改完会怎样、推荐理由、影响哪些角色、风险和代价、未解决问题与选装，以及本次具体批准哪个版本和实施范围，并链接完整方案和审核记录。架构审核不等于客户批准，也不等于独立验收通过；同版同范围已有批准不重复索取。详见[方案审核流程](references/proposal-review.md)。

## Meeting：跨角色讨论

需要多个角色一起讨论方案或评审时，可以这样调用：

> 使用 $ans-governed-construction meeting，讨论保存草稿的接口设计，请工单、存储和测试角色参与，最多两轮，输出会议纪要。

需要联合讨论时由统筹组织最小必要参与范围；不因同组就要求全员参会，也不为每个小任务开会。各角色在自己的独立上下文中提出建议和依据。默认两轮：先收集意见，再针对分歧回应；提前达成结论就结束。实际主持人只在自己已授权的 `docs/meetings/` 路径写纪要。

meeting 是技能讨论流程，不是新增命令行工具或主持人角色。会议共识只是建议，不自动授予权限，也不替代方案确认与实施授权。无法启动某个独立角色上下文时，明确记录缺席或待办，不在主持人的上下文里扮演该角色。详见 [meeting 规则](references/meeting.md)。

## 安装与更新

安装需要 Git。日常说明直接阅读 Markdown，在支持 Mermaid 的预览器里查看流程图，不需要账号或服务端。运行权限预检和任务工具需要 Python 3.10+；只阅读 Markdown 不需要启动服务。业务项目可以使用其他语言。安装时保留整个仓库。

Codex 个人安装到 `~/.agents/skills/ans-governed-construction`，macOS / Linux：

```sh
mkdir -p "$HOME/.agents/skills"
git clone https://github.com/wangzhongren/ans-skill.git "$HOME/.agents/skills/ans-governed-construction"
```

Claude Code 个人安装到 `~/.claude/skills/ans-governed-construction`，macOS / Linux：

```sh
mkdir -p "$HOME/.claude/skills"
git clone https://github.com/wangzhongren/ans-skill.git "$HOME/.claude/skills/ans-governed-construction"
```

Codex 的 Windows PowerShell 示例：

```powershell
New-Item -ItemType Directory -Force "$HOME/.agents/skills" | Out-Null
git clone https://github.com/wangzhongren/ans-skill.git "$HOME/.agents/skills/ans-governed-construction"
```

团队需要固定技能版本时，在业务仓库根目录安装为子模块：

```sh
git submodule add https://github.com/wangzhongren/ans-skill.git .agents/skills/ans-governed-construction
git submodule update --init --recursive
```

更新前先保留和处理本地改动。**个人安装**且工作区干净时，按实际安装位置选择一条更新命令：

```sh
git -C "$HOME/.agents/skills/ans-governed-construction" pull --ff-only  # Codex
git -C "$HOME/.claude/skills/ans-governed-construction" pull --ff-only  # Claude Code
```

**项目子模块**由团队维护者确认升级后，在业务仓库根目录执行：

```sh
git submodule update --remote .agents/skills/ans-governed-construction
git add .agents/skills/ans-governed-construction
```

核对新版本后，将子模块版本变更提交到业务仓库。其他成员使用 `git submodule update --init --recursive` 跟随仓库已固定的版本。

安装或更新后，下一轮对话可使用。运行可选工具时，Windows 若只有 `python` 命令，就把 `python3` 换成 `python`。

## 项目里维护哪些文件

| 文件 | 用途 |
| --- | --- |
| `角色卡/<角色>/role-card.md` | 系统功能归属、角色职责和必读资料 |
| `角色卡/<角色>/boundary.md` | 唯一授权来源：第 1 节列出允许修改的文件和目录 |
| `角色卡/<角色>/boundary.yaml` | 与 Markdown 同名同目录的结构化同步副本，不单独授权 |
| `角色卡/<角色>/memo.md` | 由本角色维护的简短事实、依据与续接线索 |
| `角色卡/<角色>/functional-description.md` | 真实职责、交接输入输出及代码或文档位置 |
| `角色卡/<角色>/api-spec.md`（适用时） | 实际对外代码能力、共享能力或装配接口的实现报告 |
| `角色卡/<项目管理>/docs/project-rules.md` | 项目管理维护、所有角色共读的已确认工程约束 |
| `src/common/<角色>/`、`src/common/shared/` | 角色自己的基础代码，以及项目管理角色维护的共享组件 |
| `角色卡/<项目管理>/docs/architecture/shared-components.md` | 共享组件的用途、入口、使用者、测试与修改影响 |
| `角色卡/<项目管理>/docs/architecture.md` | 当前整体架构、角色配合和功能导航链接 |
| `角色卡/<角色>/feature-map.md` | 本角色的功能导航 |
| `角色卡/<角色>/docs/feature/<功能名>.md` | 当前用途、流程图、分支和历史链接 |
| `docs/scheduling/<任务 ID>.md` | 项目根下由工具单写的全局计划、步骤和历史 |
| 独立验收角色自己获准的标准和结论文件 | 当前完成条件、版本、原始证据及通过/返工/证据不足判断 |
| 角色 docs 下的 `design/`、`change/`、`fix/` | 带日期的设计、修改和修复历史 |

边界 YAML 只供需要结构化读取的工具使用；当前执行仍按 Markdown Section 1，不表示工具已接入 YAML。数据字段、请求 URL 和接口含义以正式契约、Model 和功能文档为准。不再另行维护 `content.json`、`context.sqlite3` 等重复项目理解索引。

## 怎么查看

从项目管理角色的 `docs/architecture.md` 看整体，再进入角色的 `feature-map.md`，打开具体功能文件。用支持 Mermaid 的 Markdown 预览器看图，也可以直接阅读流程的文字说明。

默认不再运行 HTML 生成命令。原有 JSON 绘图器只保留给旧数据，不支持读取这些 Markdown。以后若需要 HTML 查看页，应读取这套文档，不让 AI 再维护第二份 JSON。

## 任务工具与可选旧工具

多角色任务使用 `task_ops` 时，新任务写入一份 `docs/scheduling/<任务 ID>.md`，包含计划、步骤状态和事件历史，可以随项目提交到 Git。项目授权配置仍使用一份 `.ans/project.json`；本地锁和检查输出保存在被忽略的 `.ans/runtime/`。换机器后能读历史，但运行中的工作和本地检查证据需重新核对。详见[任务操作说明](references/task-operations.md)。

角色可以把自己的功能导航、备忘录、职责说明，以及工作需要的接口报告和其他文档列入任务。每个文件必须同时获角色权限、项目配置和本次任务允许。整个目录有权限，也要列清这次具体改哪些文件。其他角色的资料、角色卡、权限文件和任务状态仍受保护。

换终端查看结果时，仅 PATH 写法不同不会再误报检查失效；真正的程序、配置、相关输入或证据变了，结果仍会失效。旧检查只有环境摘要，仍按旧方式核对，不会自动升级。新检查的执行环境记录若丢失或损坏，需要按流程重新检查。细节见[任务操作说明](references/task-operations.md)。

[旧 JSON 架构 HTML](references/role-architecture-viewer.md)、Dashboard、云端同步、角色消息和历史文档查询按需要保留，不默认启动，也不要求维护旧 JSON 或项目理解索引。本轮没有改造旧工具使其读取新的 Markdown 导航。需要这些工具时，查阅 [Dashboard 指南](dashboard/README.md)；云端上传仍由用户手动决定。

开发本技能时，在技能仓库根目录运行：

```sh
python3 -m unittest discover -s scripts/tests -q
```

内存 DOM 交互测试使用 Node.js，HTTP 测试需要允许临时绑定本机端口。代码测试与真实浏览器视觉检查分别记录。

## 设计来源与进一步阅读

Wang, Zhongren. 2026. *Role-First Software Governance: Asymmetric Authority Boundaries for AI-Native Agent Systems*. Zenodo 预印本，2026-09-18。DOI：10.5281/zenodo.22824700。[论文记录与 PDF](https://zenodo.org/records/22824700)。

- [中文技能说明](SKILL.zh.md)
- [五层调用规则](references/architecture.md)
- [角色卡与文件边界](references/role-card.md)
- [四类文档的写法](references/documentation.md)
- [跨角色任务操作](references/task-operations.md)
- [设计与变更记录](doc/)

本项目以 [MIT 许可证](LICENSE)开源。
