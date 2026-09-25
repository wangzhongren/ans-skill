# ANS Skill

一套可复用的五层架构与角色协作开发技能。**使用本技能的项目，默认提供自己的本地 Dashboard**：查看角色、职责边界、项目理解、任务进展以及需求与设计版本。需要多人或多项目共用时，也可单独部署一份云端 Dashboard；各项目只同步展示快照，不上传整个仓库。

通用页面、服务和规则都在技能目录中。业务项目只提供自己的角色卡、设计文档和协同记录；`test/game-engine` 是验证样例，不是运行其他项目的依赖。

## 能做什么

1. **约束开发边界**：按角色明确文件归属、按五层约束调用方向，先判断职责，再决定复用或拆分。
2. **统一任务操作**：派发前检查授权、依赖和写入范围，反馈校验批次及版本，验收核对实际测试证据。
3. **一个 Dashboard 看协作**：每约 2 秒读取角色和调度记录，展示执行、阻塞、待验收、设计变更及事件历史。
4. **按角色理解项目**：直接查看角色职责与修改边界，以及流程、数据和接口的汇总与详情。
5. **跨角色沟通**：共享 Dashboard 的角色收件箱支持消息、版本绑定的权限申请与管理员决定；执行仍经过本地任务门禁。

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

两种方式都要保留完整的 `SKILL.md`、`references/`、`assets/`、`dashboard/` 和 `scripts/`，不能只复制主文件。目标目录已存在时请更新，不要覆盖重装。

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

本地 Dashboard 包含 **项目概览、项目理解、阶段任务、协作事件** 四个视图；共享云端模式另有**协作收件箱**。点击角色卡可进入该角色的项目理解，先看到职责和修改边界。没有执行记录就显示“未上报”，不会用示例数据填充。

### 多项目共用一份 Dashboard

把独立的 [`dashboard/`](dashboard/README.md) 目录部署在服务器，可直接运行 Python，也可使用其中的 `Dockerfile` 和 `compose.yaml`。Compose 持久化状态卷，并只在宿主机回环地址发布端口；对外仍需 HTTPS 反向代理。创建第一个管理员后，在 `/manage` 添加项目、内置账号、项目授权和**每个项目自己的同步 Key**。用户通过 `/p/<project-id>/` 查看获授权项目。

服务器若要跟随 GitLab `main` 自动更新 Dashboard，可从手工复制目录切换为 Git 克隆，并安装 [systemd 定时更新器](dashboard/README.md#自动跟随-gitlab-的-main)。更新器只接受快进提交，重建后等待健康检查；服务器只需要 GitLab 仓库的只读 Deploy Key。

如果挂在已有域名的 `/ans-dashboard/`，配置 `ANS_DASHBOARD_BASE_PATH=/ans-dashboard`（直接运行时用 `--base-path /ans-dashboard`），反向代理保留该前缀；本地同步的 `--server-url` 也带 `/ans-dashboard`。示例见 [路径前缀部署](dashboard/README.md)。

业务项目本地运行 `python3 -m dashboard.sync`，读取角色卡摘要、边界路径、项目理解 SQLite 和任务记录，将**展示快照**同步到对应项目。服务器不用访问业务仓库，也不接收源码或角色文档全文。完整启动、Key 配置和部署示例见 [独立 Dashboard README](dashboard/README.md)。本地单项目模式无需登录，仍使用上面的启动命令。

**服务器按项目分库。**每个业务项目本地各有一份 `project-context/context.sqlite3`；共享服务器为每个项目保存一份 `projects/<project-id>.sqlite3`，存该项目的展示快照和协作记录。服务器另有一份 `dashboard.sqlite3`，保存用户、授权、同步 Key、角色凭证哈希和项目元数据。同步的是页面需要的 JSON，不是本地 SQLite 文件。Docker 部署时这些数据库都位于 `/data` 持久卷中。

共享 Dashboard 的 **协作收件箱** 允许角色用单独的角色凭证发消息、提交精确到任务/节点/版本/文件范围的权限申请；管理员在网页记录批准或拒绝，每次变化进入该项目的审计记录。角色凭证与同步 Key 分开。网页批准只表示协作决定，不替代 `task_ops` 的客户同意或已审核配置。接入方式与请求格式见 [角色沟通说明](dashboard/README.md#role-channel)。

项目理解保存在一份 `project-context/context.sqlite3` 中，以 `role_id` 区分角色。Dashboard 直接提供流程、数据、接口和定义总览；接口总览分为**网络接口**与**内部接口**，网络接口展示协议、请求方法与 URL，两类都展示具体字段。点条目进入详情，流程详情展示触发条件、步骤、输入/输出数据和接口。角色职责与边界直接取自角色卡和边界文档。AI 使用 [统一 CRUD 工具](references/project-context.md) 按角色查询或更新。

按钮点击或键盘激活如果启动了流程，直接写入该流程的触发条件；同次操作产生的 HTTP 请求作为流程步骤。“协作事件”只记录任务状态和设计变更，不采集每次真实按钮点击。

- `--root` 是项目根目录，不是默认的 `src/`。
- 自动识别 `角色卡/` 或 `role-cards/`，以及 `docs/scheduling/` 或 `doc/scheduling/`。
- 非标准目录使用 `--roles`、`--scheduling`，路径必须位于项目内部。
- 服务仅监听本机，只读；Ctrl+C 停止。它不是开机常驻服务，也不证明代理进程在线。

字段格式、复用方式和限制见 [Dashboard 说明](references/dashboard.md)。

旧的角色功能演示和全项目代码图谱工具仅在明确请求时使用，均不参与默认 Dashboard 或普通任务验收。参见 [角色演示](references/role-atlas.md)与[代码图谱](references/code-atlas.md)。

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
  role-atlas/               # 可选的旧角色功能演示
  code-atlas/               # 可选的旧全项目图谱
dashboard/                  # 可独立部署的页面、后端、用户/项目管理与同步器
  channel_store.py           # 每项目消息、申请、决定及审计
  channel_cli.py             # 角色凭证调用的本地消息/申请客户端
scripts/
  serve_dashboard.py        # 兼容的本机启动入口
  role_atlas.py             # 可选的旧角色图谱生成器
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

测试覆盖图谱、查询、本地及云端 Dashboard、项目理解增删改查、项目 Key 隔离、任务授权、版本一致性、证据和恢复。真实跨角色案例在隔离副本中复现并修复了暂停恢复计时清零，未修改原始示例源码。可用一个尚不存在的输出目录回放：

```sh
python3 scripts/validate_task_flow.py --source test/game-engine --output output/new-validation-run --node /absolute/path/to/node
```

回放执行真实源码回归和流程检查，不再次启动 AI 代理，也不覆盖浏览器初始化或完整 TypeScript 编译。详细记录见 [任务入口验证](doc/feature/2026-09-20_feature_task-operations.md)与[角色图谱验证](doc/feature/2026-09-20_feature_role-function-graphs.md)。

## 许可证

本项目采用 [Apache License 2.0](LICENSE) 开源。
