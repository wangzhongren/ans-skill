# ANS Skill

一套可复用的五层架构与角色协作开发技能。**使用本技能的项目，默认提供自己的本地 Dashboard**：查看角色、任务进展、需求与设计版本，并在同一页面按功能逐步浏览角色图谱。

通用页面、服务和规则都在技能目录中。业务项目只提供自己的角色卡、设计文档和协同记录；`test/game-engine` 是验证样例，不是运行其他项目的依赖。

## 能做什么

1. **约束开发边界**：按角色明确文件归属、按五层约束调用方向，先判断职责，再决定复用或拆分。
2. **统一任务操作**：派发前检查授权、依赖和写入范围，反馈校验批次及版本，验收核对实际测试证据。
3. **一个 Dashboard 看协作**：每约 2 秒读取角色和调度记录，展示执行、阻塞、待验收、设计变更及事件历史。
4. **按功能理解代码**：选择角色、功能和场景，使用上一步、下一步、重置和自动播放联动查看节点、示例状态及源码依据。

## 安装

需要 Git 及能访问 GitHub 的网络。本地工具需要 Python 3.10 或更高版本（已在 Python 3.14.7 验证）；仅加载规则不需要 Python。计时器回归样例另需支持 `stripTypeScriptTypes` 的 Node.js，已使用 Node 24 验证。Dashboard 不依赖 Node 或第三方 Python 包。

下面两种方式选一种，避免重复安装同名 Skill。Codex 的目录与发现机制见 [OpenAI 官方 Skill 文档](https://learn.chatgpt.com/docs/build-skills)。

### 个人安装：所有项目可用

macOS / Linux：

```sh
mkdir -p "$HOME/.agents/skills"
git clone https://github.com/wangzhongren/ans-skill.git "$HOME/.agents/skills/ans-governed-construction"
```

Windows PowerShell：

```powershell
New-Item -ItemType Directory -Force "$HOME/.agents/skills" | Out-Null
git clone https://github.com/wangzhongren/ans-skill.git "$HOME/.agents/skills/ans-governed-construction"
```

### 项目安装：随业务仓库共享

在业务项目的 Git 根目录执行：

```sh
git submodule add https://github.com/wangzhongren/ans-skill.git .agents/skills/ans-governed-construction
```

将 `.gitmodules` 和子模块记录提交到业务仓库。其他成员获取项目后执行：

```sh
git submodule update --init --recursive
```

两种方式都要保留完整的 `SKILL.md`、`references/`、`assets/` 和 `scripts/`，不能只复制主文件。目标目录已存在时请更新，不要覆盖重装。

### 使用与更新

在实际业务项目中调用：

```text
$ans-governed-construction 为当前项目建立角色边界和 Dashboard，再按授权实现订单导出，完成测试与协作记录。
```

调用名称来自 `SKILL.md` 的 `name`：`ans-governed-construction`。Codex CLI / IDE 可通过 `/skills` 或 `$` 查找；桌面端可使用技能选择器。未出现或更新未生效时，重启 Codex。

个人安装更新：

```sh
git -C "$HOME/.agents/skills/ans-governed-construction" pull --ff-only
```

项目子模块更新：

```sh
git submodule update --remote --merge .agents/skills/ans-governed-construction
```

检查后把新的子模块版本记录提交到业务仓库。如果安装目录有本地修改，先保存和处理，不要强制重置。Windows 若只有 `python` 命令，将下文 `python3` 替换为 `python`。

## 角色如何协作

| 角色 | 负责什么 | 不能做什么 |
| --- | --- | --- |
| 内置治理角色 | 创建角色、确定归属和修改边界 | 不实现业务代码 |
| 项目默认角色 | 全局调查、架构与抽象设计、角色对接设计、调度和验收 | 不直接改业务源码、测试或授权配置 |
| 执行角色 | 在获准文件范围内实现并提交验证证据 | 不擅自换角色、扩大权限或派生代理 |
| 装配角色 | 准备必要构建环境，按层集成并验证 | 不借装配跨层访问任意能力 |

角色启用、切换或子代理派发，必须有客户同意，或匹配客户认可的项目配置预授权。读取角色卡不等于激活角色。详见 [项目角色](references/project-role.md)、[调度协议](references/scheduler.md)和[协同记录](references/coordination.md)。

调用方向：`Interface → Pipeline → Service → Provider`，Model 全局共享。设计自下而上，调查从最高相关入口向下；不要求每个功能在每层新增文件。

## 启动项目 Dashboard

在已安装技能所在目录，或使用脚本的绝对路径执行：

```sh
python3 /path/to/installed-skill/scripts/serve_dashboard.py --root /path/to/your-project --port 0
```

打开终端打印的 URL。`--port 0` 自动选空闲端口，避免不同项目冲突。项目角色应在验收后启动或复用一次，并在任务中交付地址；子角色不各自启动一份。

Dashboard 包含 **项目概览、项目理解、阶段任务、事件记录、角色功能图谱** 五个视图。点击角色卡可进入该角色的项目理解，总览里也可打开角色记录或功能图谱。没有执行记录就显示“未上报”，不会用示例数据填充。

项目理解保存在一份 `project-context/context.sqlite3` 中，以 `role_id` 区分角色。Dashboard 直接提供流程、事件、数据、接口和定义总览；点条目进入详情。流程详情展示触发事件、步骤、输入/输出数据和接口；事件详情展示触发条件、动作与消费方。AI 使用 [统一 CRUD 工具](references/project-context.md) 按角色查询或更新。正式定义仍以契约和源码为准。

- `--root` 是项目根目录，不是默认的 `src/`。
- 自动识别 `角色卡/` 或 `role-cards/`，以及 `docs/scheduling/` 或 `doc/scheduling/`。
- 非标准目录使用 `--roles`、`--scheduling`，路径必须位于项目内部。
- 服务仅监听本机，只读；Ctrl+C 停止。它不是开机常驻服务，也不证明代理进程在线。

字段格式、复用方式和限制见 [Dashboard 说明](references/dashboard.md)。

## 角色图谱与功能演示

先根据当前项目的功能描述和实际源码编写流程定义，再生成角色图谱：

```sh
python3 /path/to/installed-skill/scripts/role_atlas.py --root /path/to/your-project --flows doc/design/role-flows.json
```

打开同一个 Dashboard 的“角色功能图谱”标签即可。可选择功能及正常/异常场景，逐步高亮节点、查看示例状态和源码片段；切换标签会暂停播放。仅重建一个角色可增加 `--role ROLE_ID`。

这些是**有源码定位的声明式演示，不是真实运行跟踪**。源码、功能描述或步骤定义变化后，会标记过期并暂停演示。尚未实现的功能不应编造步骤。格式见 [角色图谱说明](references/role-atlas.md)。

仓库附带游戏示例，包含 8 个角色、9 个功能、50 个演示步骤。可复现查看器：

```sh
python3 scripts/role_atlas.py --root test/game-engine --flows doc/design/role-flows.json
python3 scripts/serve_dashboard.py --root test/game-engine --port 0
```

示例仅用于学习和验证。新项目必须使用自己的根目录、角色和功能定义。旧的全项目静态代码图谱工具仍保留，但**默认关闭，不参与普通任务验收**；仅在明确请求时使用 [旧图谱工具](references/code-atlas.md)。

## 统一任务操作入口

先由客户/可信宿主审核配置和计划，准备初始化请求：

```sh
python3 scripts/task_ops.py --root /path/to/project --task repair-export init --request /path/to/init.json
python3 scripts/task_ops.py --root /path/to/project --task repair-export status
```

正常流程为 `dispatch → ack → run-check → report → verify`；另有 `stop`、`revise`、`recover` 处理停止、设计/需求修订和中断恢复。

1. 项目凭证与执行凭证分开，执行角色不能用自己的凭证派发其他角色或验收自己。
2. 计划只能缩小已审核角色范围；依赖未通过、写入冲突、配置变更或版本不符时拒绝继续。
3. 检查命令必须来自审核配置，工具记录真实退出码、候选哈希和证据；完成报告不等于验收通过。
4. 单写者锁和可恢复事件统一维护 `plan.json`、`state.json`、`events.jsonl`、`board.md`，Dashboard 读取同一份记录。

这是本地流程门禁，**不替代客户身份认证或 OS 文件权限隔离，也不自动启动 AI 代理**。配置哈希必须来自真实审核；不要将 AI 自行生成的哈希当作客户同意。完整请求格式见 [任务操作说明](references/task-operations.md)。

## 文件分工

```text
SKILL.md / SKILL.zh.md       # 英文入口与中文说明
references/                 # 角色、架构、测试、文档和工具使用规则
assets/
  role-dashboard/           # 通用协作台
  role-atlas/               # 通用角色功能演示
  code-atlas/               # 可选的旧全项目图谱
scripts/
  serve_dashboard.py        # 本机只读服务
  role_atlas.py             # 角色图谱生成器
  context_store.py          # 项目理解 SQLite 的角色筛选与增删改查
  task_ops.py               # 统一任务入口
  coordination_store.py     # 事件、快照与恢复
  tests/                    # 通用工具测试与回归夹具
  validate_task_flow.py     # 隔离的真实源码回归流程回放
test/game-engine/           # 验证样例，不是通用能力的实现位置
doc/                        # 本技能的变更、修复与验证记录
```

项目生成的快照、验证副本、凭证、项目理解数据库和本机运行输出不随技能发布。角色图谱的示例输入定义会保留，方便重新生成。

## 验证

从本仓库或技能目录运行：

```sh
python3 -m unittest discover -s scripts/tests -v
```

当前 67 项测试通过，覆盖图谱、查询、Dashboard、项目理解增删改查、任务授权、版本一致性、证据和恢复。真实跨角色案例在隔离副本中复现并修复了暂停恢复计时清零，未修改原始示例源码。可用一个尚不存在的输出目录回放：

```sh
python3 scripts/validate_task_flow.py --source test/game-engine --output output/new-validation-run --node /absolute/path/to/node
```

回放执行真实源码回归和流程检查，不再次启动 AI 代理，也不覆盖浏览器初始化或完整 TypeScript 编译。详细记录见 [任务入口验证](doc/feature/2026-09-20_feature_task-operations.md)与[角色图谱验证](doc/feature/2026-09-20_feature_role-function-graphs.md)。

## 许可证

本项目采用 [Apache License 2.0](LICENSE) 开源。
