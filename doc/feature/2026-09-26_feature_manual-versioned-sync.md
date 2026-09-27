---
id: manual-versioned-sync-feature
type: feature
title: 手动同步云端快照与历史设计
created: "2026-09-26"
updated: "2026-09-27"
timezone: Asia/Shanghai
status: verified
related:
  - manual-bidirectional-sync-design
events:
  - date: "2026-09-26"
    kind: created
    summary: 记录用户决定手动同步及冲突提醒的要求
  - date: "2026-09-26"
    kind: implemented
    summary: 加入本地 SQLite 变更记录、云端版本链、手动拉取上传和冲突提醒
  - date: "2026-09-27"
    kind: verified
    summary: 完整测试 121 项通过，Python 与 JavaScript 语法、文档链接和差异检查通过
---

# 手动版本同步

用户运行 `python3 -m dashboard.versioned_sync --root <项目目录>` 时，客户端先拉云端新版本和协作事件，再把本地管理数据快照按基础版本上传；不运行命令就不上传。`--pull-only` 只拉不推，`--record` 只把本地当前变更写入 Git 忽略的 `.ans/project.sqlite3`。现有 `dashboard.sync` 保留给尚未切换的项目；一个项目开始使用新版后，服务器拒绝旧接口继续覆盖它。

新版本会把角色卡、边界和带日期的文档原文放进版本记录，云端页面仍读取经过处理的展示快照。`GET /api/changes` 可分页取某版本之后的全部快照版本；`GET /api/channel/changes` 用游标读取超过最近 100 条的消息/审批；`GET /api/design-docs` 按路径和云端版本查询历史设计。服务器每项目仍只有一份 SQLite；网页写入经过一个有界的写线程队列。

本地同步库保存每次调用 `--record` 或手动同步时发现的快照及其角色、任务、项目理解和文件级差异。两端版本不符时，服务器返回 `409`，保留冲突候选，Dashboard 在记录检查中提醒客户；本地停止上传该冲突。客户核对后可运行 `--resolve <changeId> --choice local|cloud`。源码全文不上传，由 Git 管理。

本版的冲突单位仍是**整份项目快照**，所以不同条目的并行修改也可能需要人工核对。拉取内容进入本地同步 SQLite，供 `--remote-summary`、`--remote-artifact`、`--remote-context` 查看；它不会自动改写业务源码、角色文件或现有 `project-context/context.sqlite3`。直接文件编辑在两次记录之间产生又消失的中间版本无法事后复原；要保留每次变更，修改入口必须及时调用 `--record`。这些限制要在客户决定同步或处理冲突时说明清楚，不称作自动逐条合并或完整的本地文件恢复。

受影响文件：`dashboard/versioned_sync.py`、`dashboard/write_queue.py`、`dashboard/cloud_store.py`、`dashboard/channel_store.py`、`dashboard/server.py`、`dashboard/sync_runtime.py`、`SKILL.md`、`references/dashboard.md`、`README.md` 与 `dashboard/README.md`。对应测试位于 `scripts/tests/test_versioned_sync.py`，既有 Dashboard 和角色通道测试也需继续通过。

验证于 2026-09-27 在本地 Python 3.14.7 执行：`python3 -m unittest discover -s scripts/tests -q`，**121 项通过**，覆盖手动默认只运行一次、`--record`/`--pull-only` 不上传、项目 Key 隔离、冲突不覆盖、超过 100 条事件分页、旧客户端切换保护和已有页面回归；HTTP 测试使用本机回环地址。`python3 -m compileall -q dashboard scripts`、`node --check dashboard/app.js`、`git diff --check` 通过，7 份相关文档的链接、元数据和空白检查通过。部署到用户服务器及业务项目的迁移**尚未执行**；这些本地测试不证明线上已经更新。
