# ANS Skill

一套受 [Role-First Software Governance（RFSG）](https://zenodo.org/records/22824700) 论文启发的 AI 开发技能：先明确谁对功能负责、允许改什么，再组织代码、实现需求，由项目管理角色说明整体架构，各开发角色用功能文档和流程图解释实际行为。

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

跨角色复用由项目管理角色统一安排：它设计并编写 `shared/`、对应单元测试和共享组件文档，再安排各角色修改自己的调用代码。它不能直接改其他角色的业务代码。项目管理角色自己的 `docs/architecture/shared-components.md` 记录组件用途、入口、使用角色、输入输出、例子、测试和修改影响。目录和权限变化仍由治理角色处理；已有项目不会因为升级技能就自动搬迁代码或扩大权限。

## 谁来测试

1. **开发角色**：验证自己写的代码，每层完成时运行单元和契约测试。
2. **项目管理角色**：验证自己维护的共享组件，安排跨角色工作、修复和验收。
3. **装配角色**：准备运行环境，完成接线和启动检查。
4. **固定测试角色**：独立做跨角色联调、完整流程和回归。发现问题交给项目管理角色安排修复，修好后复测。

固定测试角色是项目里的正式角色，不是新增内置角色，也不要求一直启动一个 Agent。详细规则见[common 与共享清单](references/shared-directories.md)和[固定测试角色](references/test-role.md)。

## 日常开发怎样进行

在项目里调用 `$ans-governed-construction`，直接说明需求，例如：

> 使用 $ans-governed-construction，调查保存草稿失败的问题，先写修改方案。

1. **调查与分工。**治理角色维护角色定义和文件边界；项目管理角色负责调查、设计、共享代码和跨角色安排；开发角色负责自己的实现，固定测试角色负责联调和回归。
2. **先写方案，再用大白话说明。**文档讲用途、完整流程、具体改动和结果。客户确认并授意实施后才改代码；同版同范围已有授权，不重复问。
3. **必要改动与选装分开。**额外兼容、兜底或扩展必须在文档和聊天总结里说明好处与代价。默认勾选只是推荐，客户同意后才加；取消的选装不重新勾选。
4. **实现、测试、更新说明。**开发角色更新自己的功能文档、流程图和历史链接；项目管理角色维护整体架构，交付文档链接。

客户负责确认需求和范围；各角色对应的 AI 核对代码、维护自己的 Markdown 文档和图。图来自实际行为，不靠按钮名或文件名猜流程。

角色初次绑定和工作派发遵循客户授权或已批准的项目配置。治理完成启动准备后，交给独立的项目管理上下文；项目管理保持自己的角色，为开发、装配和测试派发各自独立的上下文，只传递任务所需资料，不复制管理角色的完整对话来改换身份。无法使用子代理时，准备交接资料，由独立新上下文顺序承接；无法创建独立上下文就报告待办，不能在原上下文切换角色。涉及文件边界变化时，由独立治理上下文处理；架构图本身不授予修改权限。

## 按角色看架构，按功能看流程

项目管理角色在自己的 `docs/architecture.md` 解释整体结构、角色职责、接口和配合关系，并链接各角色的 `feature-map.md`。

每个开发角色沿用自己的 `docs/`：

```text
角色卡/工单/
  role-card.md
  boundary.md
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

## Meeting：跨角色讨论

需要多个角色一起讨论方案或评审时，可以这样调用：

> 使用 $ans-governed-construction meeting，讨论保存草稿的接口设计，请工单、存储和测试角色参与，最多两轮，输出会议纪要。

由项目管理角色主持，各角色在自己的独立上下文中提出建议和依据。默认两轮：先收集意见，再针对分歧回应；提前达成结论就结束。纪要记录各方意见、共识、未解决问题、拟负责后续工作的角色和需要客户决定的事项，由项目管理写入自己已授权的 `docs/meetings/`，沿用其现有文档根目录。

meeting 是技能讨论流程，不是新增命令行工具或主持人角色。会议共识只是建议，不自动授予权限，也不替代方案确认与实施授权。无法启动某个独立角色上下文时，明确记录缺席或待办，不在主持人的上下文里扮演该角色。详见 [meeting 规则](references/meeting.md)。

## 安装与更新

安装需要 Git。日常说明直接阅读 Markdown，在支持 Mermaid 的预览器里查看流程图，不需要账号或服务端。可选的任务工具和旧绘图工具使用 Python 3.10+；业务项目可以使用其他语言。安装时保留整个仓库。

个人安装，macOS / Linux：

```sh
mkdir -p "$HOME/.agents/skills"
git clone https://github.com/wangzhongren/ans-skill.git "$HOME/.agents/skills/ans-governed-construction"
```

Windows PowerShell：

```powershell
New-Item -ItemType Directory -Force "$HOME/.agents/skills" | Out-Null
git clone https://github.com/wangzhongren/ans-skill.git "$HOME/.agents/skills/ans-governed-construction"
```

团队需要固定技能版本时，在业务仓库根目录安装为子模块：

```sh
git submodule add https://github.com/wangzhongren/ans-skill.git .agents/skills/ans-governed-construction
git submodule update --init --recursive
```

更新前先保留和处理本地改动。**个人安装**且工作区干净时：

```sh
git -C "$HOME/.agents/skills/ans-governed-construction" pull --ff-only
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
| `角色卡/<角色>/boundary.md` | 允许修改的具体业务文件和明确归属的 common、测试目录 |
| `src/common/<角色>/`、`src/common/shared/` | 角色自己的基础代码，以及项目管理角色维护的共享组件 |
| `角色卡/<项目管理>/docs/architecture/shared-components.md` | 共享组件的用途、入口、使用者、测试与修改影响 |
| `角色卡/<项目管理>/docs/architecture.md` | 当前整体架构、角色配合和功能导航链接 |
| `角色卡/<角色>/feature-map.md` | 本角色的功能导航 |
| `角色卡/<角色>/docs/feature/<功能名>.md` | 当前用途、流程图、分支和历史链接 |
| 角色 docs 下的 `design/`、`change/`、`fix/` | 带日期的设计、修改和修复历史 |

数据字段、请求 URL 和接口含义以正式契约、Model 和功能文档为准。不再另行维护 `content.json`、`context.sqlite3` 等重复项目理解索引。

## 怎么查看

从项目管理角色的 `docs/architecture.md` 看整体，再进入角色的 `feature-map.md`，打开具体功能文件。用支持 Mermaid 的 Markdown 预览器看图，也可以直接阅读流程的文字说明。

默认不再运行 HTML 生成命令。原有 JSON 绘图器只保留给旧数据，不支持读取这些 Markdown。以后若需要 HTML 查看页，应读取这套文档，不让 AI 再维护第二份 JSON。

## 可选旧工具与验证

多角色任务使用 `task_ops` 时，新任务写入一份 `docs/scheduling/<任务 ID>.md`，包含计划、步骤状态和事件历史，可以随项目提交到 Git。项目授权配置仍使用一份 `.ans/project.json`；本地锁和检查输出保存在被忽略的 `.ans/runtime/`。换机器后能读历史，但运行中的工作和本地检查证据需重新核对。详见[任务操作说明](references/task-operations.md)。

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

本项目以 [Apache-2.0 许可证](LICENSE)开源。
