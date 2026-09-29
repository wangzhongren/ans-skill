# ANS Skill

ANS Skill 帮助 AI 在项目里回答三个问题：**谁可以改哪些文件、代码该放在哪、改完怎么验证**。它用角色卡限定文件范围，用五层规则约束调用方向，并把测试和文档作为交付的一部分。

可以只在本地使用。默认用一份本地架构 HTML 查看角色配合、功能数据流和内部抽象；各角色只维护自己的 architecture.json，不再要求重复维护项目理解数据库。旧 Dashboard 和云端工具按需要使用。**云端同步由用户手动触发**，角色开始工作不会自动上传。

## 安装

需要 Git。运行本地工具或 Dashboard 需要 Python 3.10+；技能规则本身不要求业务项目使用 Python。完整目录必须保留，不能只复制 `SKILL.md`。

个人安装（macOS / Linux）：

```sh
mkdir -p "$HOME/.agents/skills"
git clone https://github.com/wangzhongren/ans-skill.git "$HOME/.agents/skills/ans-governed-construction"
```

Windows PowerShell：

```powershell
New-Item -ItemType Directory -Force "$HOME/.agents/skills" | Out-Null
git clone https://github.com/wangzhongren/ans-skill.git "$HOME/.agents/skills/ans-governed-construction"
```

也可以在业务仓库根目录作为子模块安装，让团队使用同一版本：

```sh
git submodule add https://github.com/wangzhongren/ans-skill.git .agents/skills/ans-governed-construction
git submodule update --init --recursive
```

已有安装且工作区干净时，用 `git -C "$HOME/.agents/skills/ans-governed-construction" pull --ff-only` 更新；有本地修改时先处理差异，不要强制覆盖。Windows 若只有 `python` 命令，把下文的 `python3` 换成 `python`。

## 在项目里使用

在 AI 中调用 `$ans-governed-construction`，说明要开发或修复什么。一个新项目通常按下面的顺序开始：

1. **确定角色、功能点和范围。**治理角色拟定角色卡与 `boundary.md`；角色卡列出这个角色主要负责的系统功能点，每个功能点各有一份当前说明。客户确认后，角色只能改边界第 1 节列出的文件。项目默认角色负责调查、架构设计、任务安排和验收，不直接代写业务源码。
2. **沿五层设计和排查。**构建时通常按 `Model → Provider → Service → Pipeline → Interface` 思考；运行时只沿 `Interface → Pipeline → Service → Provider` 逐层调用，Model 供各层共享。简单功能不需要每层都新增文件。
3. **先交文档，再实现。**先写对应的[设计、新增、修改或修复说明](references/documentation.md)，在聊天里简要讲给客户听。客户确认文档并授意按它修改后，执行角色才改自己负责的代码和测试。已确认的同版方案不用反复问；测试通过后才能称为已验证。
4. **更新角色架构并交付页面。**架构变化后，各角色更新自己的 `architecture.json`；项目角色运行绘图工具并打开生成 HTML。功能文档写清用途、完整流程、分支及结果；图展示核实过的抽象与数据交接。缺失信息保持待补，不另维护 `content.json` 或 `context.sqlite3`。

角色切换和派发必须有客户同意，或符合客户认可的项目预授权配置。角色卡归属本身不等于执行授权。[中文说明](SKILL.zh.md)、[五层架构](references/architecture.md)、[任务操作](references/task-operations.md)和[本地架构图](references/role-architecture-viewer.md)分别说明细节。

## 查看本地架构页面（默认）

每个角色的数据放在 `角色卡/<角色>/architecture.json`。项目角色在已批准的文档输出范围内运行：

```sh
python3 /path/to/ans-skill/scripts/render_architecture.py \
  --root /path/to/project --out doc/architecture/index.html
```

打开命令打印的 HTML 文件。先看角色之间使用什么约定，再选功能看数据流；点击角色或模块，进入可展开的内部抽象图。模板自带脚本和样式，不需要后端、联网或额外的画图师角色。已有项目使用 `docs/` 时，将输出改成 `docs/architecture/index.html`，不新建第二套文档根。JSON 格式和更新规则见[使用说明](references/role-architecture-viewer.md)。

旧 Dashboard 保留为可选工具；需要查看旧任务记录或已有项目理解数据时，再运行 `scripts/serve_dashboard.py`。不默认启动，也不要求角色填充旧索引。部署和命令仍见 [Dashboard 指南](dashboard/README.md)。

## 手动同步到云端（可选）

先按 [Dashboard 部署与升级说明](dashboard/README.md) 更新服务器、备份状态卷并创建项目 Key。业务项目在本机保存**一个项目 Key**：

```sh
python3 -m dashboard.local_config init \
  --project-id orders \
  --root /path/to/project \
  --server-url https://dashboard.example.com/ans-dashboard
```

之后由用户选择动作；命令都在技能目录运行：

```sh
python3 -m dashboard.versioned_sync --root /path/to/project --status     # 看待上传数量和冲突
python3 -m dashboard.versioned_sync --root /path/to/project --record     # 只把本地改动记入 SQLite
python3 -m dashboard.versioned_sync --root /path/to/project --pull-only  # 只拉云端版本与消息
python3 -m dashboard.versioned_sync --root /path/to/project              # 先拉后上传一次
```

默认命令运行一次就退出；**不运行就不上传**。云端按项目保存展示快照、角色卡、日期文档的版本和协作消息，不接收业务源码或项目 Key。云端版本与本地改动冲突时会停止覆盖并提示客户选择。拉取的内容先进入本地同步 SQLite，**不会自动改写业务文件或项目理解库**；目前以整份快照判断冲突，尚不支持逐条自动合并。服务器未升级前不要启动新版同步；一个项目也不能同时运行新旧同步器。配置、历史设计查询与冲突处理命令见 [Dashboard 指南](dashboard/README.md)。

## 测试与文档

修改本技能后，在仓库根目录运行：

```sh
python3 -m unittest discover -s scripts/tests -q
```

设计与变更记录在 [`doc/`](doc/)；[中文说明](SKILL.zh.md)与[本地架构图说明](references/role-architecture-viewer.md)是当前入口。[旧 Dashboard 总览](doc/guide/2026-09-25_guide_ans-skill-overview.md)供可选旧工具参考；旧角色演示和全项目代码图谱只在明确要求时使用。

本项目以 [Apache-2.0 许可证](LICENSE)开源。
