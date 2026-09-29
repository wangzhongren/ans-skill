# ANS Skill

一套受 [Role-First Software Governance（RFSG）](https://zenodo.org/records/22824700) 论文启发的 AI 开发技能：先明确谁对功能负责、允许改什么，再组织代码、实现需求，并用本地架构页面把角色配合和系统结构展示出来。

## 为什么这样设计

AI 可以跨模块阅读代码、追查问题，但“看懂了哪里”和“有权修改哪里”需要分开。比如排查工单保存失败时，可能一路查到存储模块；找到原因后，仍应由拥有相应职责和权限的角色完成修改。

Role-First 论文提出了从角色和职责出发建立权限与代码归属的治理思路。ANS 从中吸收了三点：

1. **先确定责任，再确定代码归属。**先问谁对这项业务行为负责，再明确它需要哪些模块和文件。
2. **按需广泛阅读，在授权范围内修改。**排查时可以在实际读取权限内跨模块了解情况，当前上下文只加载任务需要的内容。
3. **发现问题后，交给负责的角色处理。**理解另一个模块的问题，不会自动获得修改它的权限。

在本项目中，这些思路落成了角色卡、文件边界和跨角色协作规则。五层代码组织、先写方案、角色架构 JSON 和本地 HTML，是 ANS 为项目开发选择的具体做法；它们不是论文要求的固定目录或工具。

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

角色边界最终落实到具体文件，调用通过约定好的公开入口完成。一个功能不必在每层新建文件；已有项目沿用实际目录，不为套模板搬迁代码。

角色是一份职责和权限定义。实际执行者可以是一个按授权顺序切换角色的 AI，也可以是分工执行的多个 Agent；定义多个角色，不等于必须同时启动多个模型。

## 日常开发怎样进行

在项目里调用 `$ans-governed-construction`，直接说明需求，例如：

> 使用 $ans-governed-construction，调查保存草稿失败的问题，先写修改方案。

1. **调查与分工。**治理角色维护角色定义和文件边界；项目角色负责调查、架构设计和协调；业务或基础能力角色负责自己的实现。
2. **先写方案，再用大白话说明。**文档讲用途、完整流程、具体改动和结果。客户确认并授意实施后才改代码；同版同范围已有授权，不重复问。
3. **必要改动与选装分开。**额外兼容、兜底或扩展必须在文档和聊天总结里说明好处与代价。默认勾选只是推荐，客户同意后才加；取消的选装不重新勾选。
4. **实现、测试、更新架构。**只修改受影响的部分。验证后，由承担该角色的 AI 更新自己的架构 JSON，项目角色生成并交付 HTML。

客户负责确认需求和范围；角色对应的 AI 负责核对代码、整理文档和维护 JSON。绘图程序读取 JSON 生成页面，不会自动从源码推断整个架构。

角色切换遵循客户授权或已批准的项目配置。涉及文件边界变化时，由治理角色处理；架构图本身不授予修改权限。

## 用图看清项目

每个角色维护一份 `architecture.json`，记录自己的抽象、公开约定、依赖、功能关联和数据交接。共享抽象只定义一次，其他角色按 ID 引用。

程序将各角色的数据组合成三个视图：

1. **角色配合图**：谁使用谁提供的什么约定。
2. **数据流向图**：选一个功能，看传递什么数据、经过什么条件、返回什么结果。
3. **内部抽象图**：点击角色或模块，展开其核心抽象、组成关系和支撑的功能点。

图来自已记录的事实。缺少引用或数据流就显示待补，计划中的抽象要明确标注。HTML 是当次快照，JSON 更新后重新生成；绘图不需要额外的画图师角色或模型调用。

## 安装与更新

需要 Git。绘图工具使用 Python 3.10+ 标准库，HTML 自带脚本和样式，不需要前端依赖、服务器或账号。业务项目可以使用其他语言，安装时保留整个仓库。

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

安装或更新后，下一轮对话可使用。Windows 只有 `python` 命令时，把下文的 `python3` 换成 `python`。

## 项目里维护哪些文件

| 文件 | 用途 |
| --- | --- |
| `角色卡/<角色>/role-card.md` | 系统功能归属、角色职责和必读资料 |
| `角色卡/<角色>/boundary.md` | 允许修改的具体文件 |
| `角色卡/<角色>/architecture.json` | 当前架构事实，由该角色对应的 AI 维护 |
| `角色卡/<角色>/features/*.md` | 每个功能的用法、完整流程、分支和结果 |
| 文档目录下的 `design/`、`feature/`、`change/`、`fix/` | 带日期的设计、新增、修改和修复记录 |
| `已有文档根/architecture/index.html` | 程序生成的架构页面 |

数据字段、请求 URL 和接口含义以正式契约、Model 和功能文档为准。不再另行维护 `content.json`、`context.sqlite3` 等重复项目理解索引。

## 生成本地架构页面

角色卡和架构 JSON 准备好后，项目角色在已批准的输出范围内运行：

```sh
python3 /path/to/ans-skill/scripts/render_architecture.py \
  --root /path/to/project \
  --out doc/architecture/index.html
```

命令打印生成 HTML 的绝对路径，直接在本地浏览器打开。任务结束时，项目角色提供页面链接，条件允许时打开页面。

输出沿用项目现有文档根：已有 `doc/` 就复用它，使用 `docs/` 的项目改成 `docs/architecture/index.html`。自定义角色目录可加 `--roles <项目相对目录>`。字段和示例见[架构 JSON 与绘图说明](references/role-architecture-viewer.md)。

## 可选旧工具与验证

旧 Dashboard、云端同步、角色消息和历史文档查询按需要保留，不默认启动，也不要求维护旧项目理解索引。新的架构 HTML 尚未接入旧 Dashboard。需要这些工具时，查阅 [Dashboard 指南](dashboard/README.md)；云端上传仍由用户手动决定。

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
