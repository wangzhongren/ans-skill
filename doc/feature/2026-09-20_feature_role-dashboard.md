---
id: role-dashboard-feature
type: feature
title: 本地实时角色协作 Dashboard
created: "2026-09-20"
updated: "2026-09-20"
timezone: Asia/Shanghai
status: verified
related:
  - coordination-table-change
events:
  - date: "2026-09-20"
    kind: created
    summary: 以角色卡和调度文件为数据源展示项目协作情况
  - date: "2026-09-20"
    kind: implemented
    summary: 实现本机只读 API、自动刷新页面与记录一致性提示
  - date: "2026-09-20"
    kind: verified
    summary: 后端测试通过，浏览器实测搜索、文档读取及执行中到待验收自动刷新
---

# 角色协作 Dashboard

1. **功能**：角色概览、状态计数、角色搜索与筛选、阶段任务表、需求/设计版本、最新反馈与下一负责人、事件时间线、角色及边界文档只读查看。
2. **数据来源**：读取项目根的角色文件夹和 doc(s)/scheduling 记录，每约 2 秒轮询。没有记录显示未上报；版本、角色或事件序列不一致显示待核对。连接失败保留旧快照并明确标记。
3. **边界**：Python 标准库本地 HTTP 服务，只绑定 127.0.0.1，不提供写入或派发 API，不启动代理，不声称检测代理存活或验证业务证据。
4. **演示**：只读连接现有 test/game-engine，展示 8 个真实角色；该项目没有调度记录，没有为展示效果补造实际任务状态。

## 文件

```text
scripts/serve_dashboard.py
scripts/tests/test_dashboard.py
assets/role-dashboard/index.html
references/dashboard.md
```

- [启动与接入说明](../../references/dashboard.md)
- [服务](../../scripts/serve_dashboard.py)
- [页面](../../assets/role-dashboard/index.html)
- [测试](../../scripts/tests/test_dashboard.py)

中英文 Skill 导航、README 和协同表参考已接入看板。原业务示例源码和用户调度数据未修改。

## 验证

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s scripts/tests -v
python3 scripts/serve_dashboard.py --root test/game-engine --port 8765
```

12 项看板测试涵盖空记录、实时重读、计划/状态版本不一致、设计未确认、未知角色、缺失状态、对象型节点表、事件序列、路径穿越/符号链接、只读 HTTP 和 Host 限制。原有 14 项图谱测试也已通过。

浏览器实际检查：8 个角色正确显示；搜索“渲染”匹配名称及职责；角色详情可只读查看 boundary.md；在独立临时项目中，状态由 running 更新为 awaiting-verification 后，不手动刷新也自动更新计数、卡片、任务表和事件。临时测试服务随后停止；实际项目看板保留。窄窗口布局已截图检查，无横向页面溢出。

测试发现无变化时重建节点会干扰操作，已改为数据变化才重绘；手动刷新复用单个轮询计时器。断线/重新连接提示已纳入显示逻辑，当前未声称完成所有网络故障的浏览器自动化覆盖。

## 使用限制

运行期间有效，终止服务后需按说明重启。它刷新的是磁盘记录，不自动记录执行过程；项目角色仍需按协同协议写入计划、状态与日志。对话和角色模型的全部权限控制并未由此实现。服务不适合作为公开多用户站点，单记录文件限制为 2 MiB。

本次工作保留仓库既有未提交修改，未提交、推送或覆盖已安装 Skill。
