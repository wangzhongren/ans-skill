---
id: task-operations-feature
type: feature
title: 统一任务入口与真实跨角色修复验证
created: "2026-09-20"
updated: "2026-09-20"
timezone: Asia/Shanghai
status: verified
related:
  - coordination-table-change
  - role-dashboard-feature
events:
  - date: "2026-09-20"
    kind: created
    summary: 将授权、反馈版本、事件与状态写入集中到统一操作入口
  - date: "2026-09-20"
    kind: implemented
    summary: 实现项目/执行凭证隔离、依赖门禁、真实检查证据和可恢复记录
  - date: "2026-09-20"
    kind: verified
    summary: 44 项测试通过；两角色真实源码修复及最终工具版本回放均完成
---

# 统一任务操作入口

1. **已实现**：[task_ops.py](../../scripts/task_ops.py) 提供 init、dispatch、ack、run-check、report、stop、revise、verify、status、recover。配置需审核后固定哈希；派发检查白名单、操作、依赖、冲突和并发容量。无自动授权时，客户同意记录需精确匹配本次任务、角色、范围、计划版本和执行次数。
2. **角色隔离**：项目凭证负责派发、修订、验收和恢复；执行凭证绑定角色、任务、批次和 workerId，只能确认版本、执行获准检查和反馈。重复反馈幂等，旧批次或旧版本反馈不能覆盖当前状态。凭证原文不写入事件/状态，不提交仓库。
3. **持久化**：[coordination_store.py](../../scripts/coordination_store.py) 使用 OS 文件锁、持久事件、哈希链和原子快照替换，统一生成 board.md（含证据链接）。日志提交后快照写入中断可恢复；日志断尾、篡改或缺失不能静默修补。
4. **验证案例**：独立主循环执行代理与装配执行代理在隔离副本中完成真实 Timer/GameLoop/Engine 暂停恢复修复。原始 test/game-engine 应用源码未修改。

## 文件结构

```text
scripts/
  task_ops.py
  coordination_store.py
  validate_task_flow.py
  tests/
    test_task_ops.py
    helpers/timer_regression.cjs
    fixtures/timer-repair.json
references/task-operations.md
```

现有项目角色、调度和协同规范接入统一工具；Dashboard 继续只读读取同一份计划、状态和事件，并补充新事件标签。

## 真实问题与角色交接

原实现 GameLoop.pause 调用 Timer.stop，resume 调用 Timer.start。start 会清空累计时间和帧数。固定时钟下，恢复后一帧实际累计时间为 0.1 秒，预期为 0.2 秒；真实 Engine 生命周期包装也复现此问题。

- D1：经批准的检查实际失败，主循环角色报告契约冲突。
- D2：明确 start 是新会话、pause/resume 保留累计数据并排除暂停时间；调度记录阻塞受影响任务并保留旧批次占用，直到确认停止。
- 迟到 D1 完成反馈被拒绝；装配在主循环尚未验收前派发被拒绝。
- 主循环代理仅修改 Timer 抽象、PerformanceTimer、GameLoop 三个获准文件，实际回归通过后提交待验收。
- 项目角色核对当前证据后放行装配代理；装配只写集成说明，执行真实 Engine 生命周期包装回归，随后由项目角色验收。

初次真实代理记录位于工作区 `output/task-ops-timer-case/`。加入项目凭证保护后，使用这两个代理产出的实际修复，通过 [validate_task_flow.py](../../scripts/validate_task_flow.py) 在新副本中重放最终工具版本。回放不伪装成再次启动代理，记录位于 `output/task-ops-release-validation/`；已展示的 Dashboard 连接的是同样通过的 `output/task-ops-final-validation/`。这些输出属于本地验证产物，不要求随 Skill 发布。

## 测试与证据

环境：Python 3.14.7、Node v24.19.0。

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s scripts/tests -v
python3 scripts/validate_task_flow.py --source test/game-engine --output output/new-validation-run --node /absolute/path/to/node
```

全部 44 项脚本测试通过（任务入口 18 项，原图谱/查询/看板 26 项）。最终同意记录增加执行次数绑定后，任务入口 18 项重新通过；最终 board 证据链接调整后，任务入口及完整真实源码回放再次通过。覆盖未授权派发、角色/配置变更、同意不能重放、批次与版本核对、依赖与写入占用、重复报告、越界声明、失败/缺失/过期证据、实际检查退出码、项目凭证隔离、文件锁、日志投影恢复及 dashboard 一致性。

最终回放结果：修复前两个检查退出码均为 1；修复后 owner 与 integration 均为 0；旧反馈拒绝、提前依赖派发拒绝、执行代理自行验收拒绝均为 true；两项节点均 verified，生成 22 条事件。浏览器实际展示两角色“已完成（已验收）”，R1/D2、状态版本 22 和对应事件。

Markdown 引用、章节锚点、代码围栏、Python 语法、Skill 格式和差异空白检查通过。

## 边界与后续

检查使用真实源码、确定性时钟/RAF 和初始化依赖替身；不覆盖 DOM 启动、真实浏览器调度或 TypeScript 编译检查。原应用修复保存在验证副本，未自动应用回用户业务项目。

工具提供本地流程门禁，不是 OS 沙箱或人类身份认证系统。客户审核来源与项目凭证必须由可信宿主管理；有权改写全部文件、凭证并以同一 OS 身份运行代码的人仍在安全边界之外。CLI dispatch 返回授权分配，不自行调用 AI 服务；本次真实代理由协调者在门禁成功后通过宿主工具启动。

本次保留原有未提交修改，未提交、推送或覆盖已安装 Skill。
