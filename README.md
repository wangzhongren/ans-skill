# ANS Skill

让 AI 按角色和文件边界开发，先把方案说清楚，再改代码，最后把项目结构画给你看。

每个角色维护一份 `architecture.json`。技能把这些文件汇总成一个本地 HTML：看角色怎样配合，选择功能看数据流，点击模块看内部抽象。日常使用只需本地文件和绘图程序。

## 安装与更新

需要 Git。绘图工具使用 Python 3.10+ 标准库，HTML 自带脚本和样式，不需要前端依赖、服务器或账号。业务项目可以使用其他语言。安装时保留整个仓库。

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

团队需要固定技能版本时，可在业务仓库根目录安装为子模块：

```sh
git submodule add https://github.com/wangzhongren/ans-skill.git .agents/skills/ans-governed-construction
git submodule update --init --recursive
```

通过 Git 安装且没有本地改动时，用下面的命令更新；有改动先保留和处理差异：

```sh
git -C "$HOME/.agents/skills/ans-governed-construction" pull --ff-only
```

安装或更新后，下一轮对话可使用。Windows 只有 `python` 命令时，把下文的 `python3` 换成 `python`。

## 在项目里怎么用

调用 `$ans-governed-construction`，说明要开发、修改或修复的功能。例如：

> 使用 $ans-governed-construction，调查保存草稿失败的问题，先写修改方案。

之后按这个顺序处理：

1. **明确谁负责、能改哪里。**角色卡列出负责的系统功能点，boundary.md 列出允许修改的文件。治理角色处理角色和边界变更；项目角色负责调查、设计和协调；开发角色改自己负责的代码。
2. **先交方案。**文档写清用途、完整流程、具体改动和结果。在聊天里再用大白话缩写。客户确认文档并授意实施后才改代码；同版同范围已确认的，不重复问。
3. **把必要改动和选装分开。**额外的兼容、兜底或扩展在文档和聊天总结里都列出来，说明好处与代价。默认勾选只表示推荐，客户同意后才加；已经取消的，不重新勾选。
4. **实现、测试、更新图。**按实际受影响的层修改和验证。架构变化后，各角色更新自己的 JSON，项目角色生成并交付本地 HTML。

代码运行时遵守以下调用方向，Model 是各层共用的数据定义：

```text
Interface（入口）→ Pipeline（组织流程）→ Service（业务规则）→ Provider（外部资源）
Model（共享数据定义）
```

一个功能不需要在每层都新建文件。已有项目沿用实际目录，不为了套模板搬迁代码。角色切换需要客户授权或符合已批准的项目配置；画出的图不扩大文件权限。

## 项目里维护哪些文件

| 文件 | 说明 |
| --- | --- |
| `角色卡/<角色>/role-card.md` | 角色负责哪些系统功能、工作时要读什么 |
| `角色卡/<角色>/boundary.md` | 允许修改哪些文件 |
| `角色卡/<角色>/architecture.json` | 当前抽象、公开约定、依赖、功能关联和数据交接 |
| `角色卡/<角色>/features/*.md` | 每个功能怎样使用、完整流程和结果 |
| 项目或角色文档目录下的 `design/`、`feature/`、`change/`、`fix/` | 带日期的设计、新增、修改和修复说明 |
| `已有文档根/architecture/index.html` | 程序生成的查看页面，重新生成即可更新 |

每个角色只维护自己的 JSON，共享抽象按 ID 引用。数据字段、请求 URL 和接口含义继续以正式契约、Model 和功能文档为准，不再另行维护 `content.json`、`context.sqlite3` 等重复项目理解索引。

## 生成本地架构页面

项目角色在已批准的输出范围内运行：

```sh
python3 /path/to/ans-skill/scripts/render_architecture.py \
  --root /path/to/project \
  --out doc/architecture/index.html
```

命令打印生成 HTML 的绝对路径，直接在本地浏览器打开：

1. **角色配合图**：哪个角色使用谁提供的什么约定。
2. **数据流向图**：选一个功能，查看传递的数据、条件和返回结果。
3. **内部抽象图**：点击角色或模块，展开其核心抽象、组成关系和支撑的功能点。

页面是当前 JSON 的快照。改了 JSON 就重新生成；缺少引用或数据流会显示待补，程序不会猜测，也不会运行应用或调度 AI。任务结束时由项目角色提供页面链接，条件允许时打开它，不需要新增画图师或额外模型调用。

输出沿用项目现有文档根：已有 `doc/` 就复用它，使用 `docs/` 的项目改成 `docs/architecture/index.html`。自定义角色目录可加 `--roles <项目相对目录>`。具体字段、示例和更新时机见[架构 JSON 与绘图说明](references/role-architecture-viewer.md)。

## 可选的旧工具

旧 Dashboard、云端同步、角色消息和历史文档查询仍保留，需要时再用，不默认启动或要求填充旧项目理解数据。云端上传由用户手动决定。

新的架构页面目前在本地生成，尚未接入旧 Dashboard。旧工具的配置、Key、同步、冲突处理和 Docker 部署集中在 [Dashboard 指南](dashboard/README.md)，不属于使用本地架构页面的前置步骤。

## 开发和验证本技能

在技能仓库根目录运行：

```sh
python3 -m unittest discover -s scripts/tests -q
```

客户端的内存 DOM 交互测试使用 Node.js；HTTP 测试需要允许临时绑定本机端口。测试结果与真实浏览器的视觉检查分别记录。

继续阅读：

- [中文技能说明](SKILL.zh.md)
- [五层调用规则](references/architecture.md)
- [角色卡与文件边界](references/role-card.md)
- [四类文档的写法](references/documentation.md)
- [跨角色任务操作](references/task-operations.md)
- [设计与变更记录](doc/)

本项目以 [Apache-2.0 许可证](LICENSE)开源。
