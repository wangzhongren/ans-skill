---
title: ANS Skill 怎么工作
updated: "2026-09-27"
timezone: Asia/Shanghai
---

# ANS Skill 怎么工作

这份文档只讲主线。**ANS Skill 是开发规则和工具的集合，不是业务项目，也不是云端服务。**其中有两条不同的约束：**角色边界决定谁能改哪些文件；五层架构决定代码之间怎么调用。**Dashboard 只展示记录。项目可以只在本地开发；需要共享查看时再接云端。

## 1. 先分清三个位置

| 位置 | 放什么 | 主要作用 |
| --- | --- | --- |
| **技能目录** `ans-skill/` | `SKILL.md`、`references/`、`scripts/`、`dashboard/` | 给 AI 规则和可执行工具；多个业务项目共用一份 |
| **业务项目目录** | 源码、`角色卡/`、`docs/`、`project-context/context.sqlite3`、可选的 `.ans-dashboard.local.json` | 实际开发、测试和本地项目理解；一个业务项目一份 |
| **云端 Dashboard** | 用户与 Key 元数据、各项目独立的 SQLite 展示数据和协作记录 | 登录查看多个项目；不运行项目源码或 AI 角色 |

```mermaid
flowchart LR
    Skill["技能：规则 + 工具"] -->|指导开发| Project["业务项目：源码 + 角色卡 + 项目理解"]
    Project -->|本机只读| Local["本地 Dashboard"]
    Project -->|用户运行同步命令| Sync["本地版本记录"]
    Sync --> Cloud["云端 Dashboard：每项目独立数据"]
    Client["本地角色通信 CLI"] -->|发送消息和申请| Cloud
    Cloud -->|手动拉取版本、消息和决定| Client
```

**关键区别：**本地 Dashboard 直接读业务项目文件；云端 Dashboard 看上一次由用户上传的展示快照。新版手动同步会先把云端版本和消息拉到本地同步 SQLite，再按版本上传本地管理数据；它不会自动改写源码或授予任务权限。

## 2. 开发一个功能时发生什么

1. **确定角色与边界。**新项目先由内置 ANS Governance 建立角色卡和 `boundary.md`；候选边界需要客户接受。项目默认角色负责总体调查、架构与角色间设计；能力角色写自己拥有的代码；装配角色写根入口并做整体验证。一个聊天框可调查问题，多角色开发需要逐个授权或已有客户批准的配置。角色卡说明职责，**`boundary.md` Section 1 才是可写文件清单**。
2. **按五层职责设计和实现。**构建顺序通常是 `Model → Provider → Service → Pipeline → Interface`；根 `main` 文件只负责启动 Interface。运行调用方向是 `Interface → Pipeline → Service → Provider`，每层只调用相邻下一层，Model 可被共享。新建或明确重构的 Provider 和 Service 使用 `abstract/` 放调用约定、`impl/` 放具体代码、`public/` 放上层能使用的入口；已有项目不因使用技能就自动迁目录。`utils/`、`resource/`、`test/`、`docs/` 只是辅助目录，不增加架构层；简单功能无需每层都新增文件。
3. **验证受影响的层，再接上层。**角色写自己的测试和带日期的设计、功能、修改或修复文档；实际成功/失败、文件范围和版本构成证据。不涉及的层无需为了凑齐五层而新增文件或测试。项目角色管理跨角色依赖。若要建立阶段计划、派发和验收记录，必须通过 `task_ops` 和客户审阅的配置哈希；它写入 `plan.json`、`state.json`、`events.jsonl` 并生成 `board.md`，但不自动启动代理。已授权的独立单角色任务可以不建调度图。
4. **装配与展示。**装配角色跑根入口和端到端测试。项目角色被接受后就可启动本地 Dashboard，在开发过程中查看真实角色、项目理解、阶段任务和协作事件；没有调度记录时，任务视图保持空白，不会编造状态。云端同步由用户另行决定，不属于角色启动流程。

五层规则和角色边界的细节分别在[架构约束](../../references/architecture.md)、[角色卡](../../references/role-card.md)和[项目角色](../../references/project-role.md)。旧的全项目代码图谱默认关闭，只有明确要求时才生成。

| 你要做的事 | 需要的部分 |
| --- | --- |
| 在本地开发一个功能 | 已接受的角色边界、受影响层的代码/测试、相应文档；本地 Dashboard 默认可用 |
| 让多人查看或跨项目沟通 | 在上一行基础上配置云端项目 Key；需要更新时由用户运行同步命令 |
| 记录可审计的阶段派发与验收 | 再接入经过客户审核配置的 `task_ops`；不能凭角色卡或云端 Key 自动启用 |
| 查看旧式全项目代码图谱 | 只有明确要求时才生成；普通开发不需要 |

## 3. 项目理解、任务记录、文档各管什么

| 内容 | 本地位置 | Dashboard 里看到什么 |
| --- | --- | --- |
| 角色职责与可写边界 | `角色卡/<role>/role-card.md`、`boundary.md` | 角色卡、职责与边界 |
| 当前项目理解 | 一份 `project-context/context.sqlite3`，用 `role_id` 区分角色 | 流程先说明用途与成功/失败结果，再显示真实分支图、输入/输出、接口和异常排查点 |
| 执行与版本记录 | `docs/scheduling/<task>/plan.json`、`state.json`、`events.jsonl`、`board.md` | 阶段任务、协作事件与验收状态 |
| 历史与设计依据 | 根 `docs/` 和角色自己的 `docs/`，文件名带日期 | 当前 Dashboard 只可直接打开角色目录根部的角色卡、边界、API、功能说明和变更日志；带日期的记录仍在文件中 |

项目理解是**当前导航索引**，文档是**设计与变更历史**，任务记录是**执行状态**。三者不互相替代。项目理解中的按钮点击属于流程触发条件；协作事件记录任务与设计变化，不记录每次按钮点击。带日期文档有生成时间线所需的元数据，但当前没有默认自动生成的时间线页面。详见[项目理解格式](../../references/project-context.md)、[文档规则](../../references/documentation.md)和[任务操作协议](../../references/task-operations.md)。

## 4. 什么时候需要云端，怎样接入

只在自己电脑看项目时，启动本地 Dashboard 即可，**不需要账号或 Key**。多人查看、跨项目总览或角色云端通信时，再部署云端 Dashboard，并按以下顺序接入：

1. 在**本地业务项目**确定稳定的项目 ID，例如 `orders`。
2. 云端管理员在 `/manage` 用这个 ID 创建项目 Key。服务器会登记项目；首次同步前显示“待同步”。同项目角色共用这个 Key，各自声明角色 ID；服务器验证项目 Key，不能独立证明是哪位角色。
3. 在业务项目根目录建立私有 `.ans-dashboard.local.json`。初始化命令隐藏输入 Key；文件权限为 `0600`。若此时项目已是 Git 仓库，工具会写本地 `.git/info/exclude`；若后来才初始化 Git，需要自行忽略该文件。
4. 先更新云端 Dashboard 程序并备份状态卷，再停用旧定时上传。之后用户想更新云端时手动运行新版同步命令：先拉云端版本与消息，再上传本地改动；只想查看云端变化时使用 `--pull-only`。不运行命令就不上传。

以下命令都从**技能目录**运行。把示例绝对路径换成自己的项目路径；本地 Dashboard 占用当前终端，手动同步命令运行完就退出。

```sh
# 终端 A：启动本地只读 Dashboard
PROJECT_ROOT="/absolute/path/to/business-project"
python3 -m dashboard.server --root "$PROJECT_ROOT" --port 0
```

需要云端时，在另一个终端运行；`PROJECT_ROOT` 是新终端里的变量，要重新设置：

```sh
PROJECT_ROOT="/absolute/path/to/business-project"
# 只初始化一次；命令会交互读取 Key
python3 -m dashboard.local_config init \
  --root "$PROJECT_ROOT" --project-id orders \
  --server-url https://dashboard.example.com/ans-dashboard

# 只拉取云端版本和消息，不上传
python3 -m dashboard.versioned_sync --root "$PROJECT_ROOT" --pull-only
# 用户决定上传时，拉取后上传一次并退出
python3 -m dashboard.versioned_sync --root "$PROJECT_ROOT"
```

要查询云端消息，在**另一个技能目录终端**运行：

```sh
PROJECT_ROOT="/absolute/path/to/business-project"
python3 -m dashboard.channel_cli --root "$PROJECT_ROOT" --role orders list
```

| 会上传到云端 | 不会随快照上传 |
| --- | --- |
| 角色名称、边界、项目理解、任务状态、角色卡和带日期文档的版本 | 业务源码、完整仓库、本地 SQLite 文件、项目 Key |

云端按项目保存 `projects/<project-id>.sqlite3`，另用 `dashboard.sqlite3` 保存用户、项目和 Key **哈希**。网页登录用户默认可查看全部项目；Key 只对所属项目有效。云端管理员的权限申请决定是一条协作记录，**不自动授权本地 `task_ops` 写代码**。部署、Key 和 API 细节见[Dashboard 说明](../../dashboard/README.md)。

## 5. 常见情况

1. **项目尚未配置云端。**继续本地开发；用户要求云端共享时再配置项目 Key，不在每次角色切换时提问。
2. **云端没更新。**手动模式只有用户运行同步命令才更新。先看待上传数量和冲突，再检查网络与项目 ID。
3. **云端有消息，本地没看到。**运行 `dashboard.versioned_sync --pull-only` 把新增消息按游标拉入本地同步 SQLite；它不自动改写任务文件或授权源码修改。
4. **阶段任务为空。**项目尚未产生有效的 `task_ops` 计划和状态时，Dashboard 就是空的；角色卡和项目理解仍可正常显示。
5. **想定时同步。**只有用户明确选择时才加 `--interval`；默认是手动一次。定时进程不是开机服务，也不能和旧版同步器同时运行。
