---
id: task-authority-change
type: change
title: 让调度与独立验收使用不同凭证
created: "2026-10-19"
updated: "2026-10-19"
timezone: Asia/Shanghai
status: verified
related: [role-authority-split-design]
events:
  - date: "2026-10-19"
    kind: designed
    summary: 按已批准角色拆分方案记录任务工具实施范围
  - date: "2026-10-19"
    kind: implemented
    summary: 完成v2独立权限与证据门禁，开发49项及真实timer回放通过，等待独立QA
  - date: "2026-10-19"
    kind: verified
    summary: 引用固定测试最终201项及独立验收标准v2 C1–C8通过结论
---

# 让调度与独立验收使用不同凭证

旧任务 CLI 的协调令牌同时能派发与通过验收。本轮依照[已批准方案](../../../项目管理/docs/design/2026-10-19_design_role-authority-split.md)和[前置标准](../../../验收/docs/acceptance/2026-10-19_role-authority-split-criteria.md)，在 `scripts/task_ops.py` 用户入口实现独立凭证、派发前预检、三种结论及当前有效证据判断；`scripts/coordination_store.py` 保持单份 Markdown、事件链、锁和原子替换。当前功能见[任务工具](../feature/task-authority.md)。

状态 v2 删除旧协调与工作认证字段，旧 Markdown/JSON 只读。配置和计划输入仍为 schema 1。验收摘要只来自已审核配置，调度初始化不能生成、覆盖或取得验收秘密。`accept-plan` 固定标准、客户确认来源、全部必需节点和独立测试覆盖；`verify` 接收 pass/needs-work/missing-evidence，只有当前批次、候选、标准、报告、实际检查及祖先证据全部有效才释放依赖。最终完成由所有节点的当前有效通过派生。

修改限四程序文件以及本角色导航、memo、功能与本记录。开发单测由本角色维护 `scripts/tests/test_task_ops.py`；真实 timer 回放只在隔离副本写入。固定测试独占跨角色测试文件，本角色不代替独立测试或最终验收。不增加服务、数据库、TTL、组层级、云端角色 Key 或凭证重置入口。

开发交付时已完成本角色实现与开发验证，随后交固定测试和独立验收；现已取得下述独立通过结论。未发布或安装。旧Markdown保留原v1渲染校验；新增JSON只读路径的plan/state末级文件也各自经过safe检查，避免外链绕过既有路径约束。

开发环境实际为 Python 3.14.7、`/usr/local/bin/node` v24.14.0。`PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s scripts/tests -p test_task_ops.py -v` 运行49项，退出0；原日志：`/tmp/ans-task-unit-final-20261019.log`。覆盖独立凭证、预检/陈旧版本、三种结论、返工新批次、实际argv/环境/生产者、缺产物/超时/改候选、三层祖先证据、非影响复核、旧记录只读/外链拒绝、脱敏，以及既有锁/原子/重复反馈/Git冲突/读取回归。`git diff --check -- scripts/task_ops.py scripts/coordination_store.py scripts/tests/test_task_ops.py scripts/validate_task_flow.py` 退出0。

`PYTHONDONTWRITEBYTECODE=1 python3 scripts/validate_task_flow.py --source test/game-engine --output /tmp/ans-task-timer-delivery-20261019 --node /usr/local/bin/node` 退出0，原日志`/tmp/ans-task-timer-delivery-20261019.log`；汇总`/tmp/ans-task-timer-delivery-20261019/docs/validation-summary.json`。回放使用真实子进程CLI和stdin请求；原始Timer/Engine检查均退出1，修复后的开发及固定测试检查均退出0，24个事件，迟到反馈、依赖过早派发、工作者自验收均实际拒绝，最终全节点当前有效通过。原test/game-engine源码保持只读。

最终四程序文件候选：`c8af7641c83888807ad38939ecfaf0621735b062cf21467e7436f92ffcd7ce8b`。算法为相对路径到文件SHA-256的映射，按键排序、无空格UTF-8 JSON后再SHA-256；逐文件摘要及运行版本保存在`/tmp/ans-task-candidate-20261019.json`。此摘要不含会继续更新的角色文档与其他角色候选，固定QA另有完整最终候选清单，见其原报告；本次只收尾文档状态和结果链接，四程序文件未变。

独立来源：[固定测试正式原报告](../../../测试/docs/change/2026-10-19_change_role-authority-split-validation.md)记录最终全套201项、53.608秒、exit 0、无跳过，其中真实CLI25项，覆盖真正基线旧CLI拒写、Dashboard读取/隔离启动和跨角色完整流程。[独立验收结果](../../../验收/docs/acceptance/2026-10-19_role-authority-split-result.md)按标准v2 C1–C8正式判定pass。本角色引用这些独立报告，没有代跑、代写或把开发自测作为终验。原报告保留PyYAML缺失导致官方quick_validate退出1及替代检查的范围限制。

当前限制：开发49项与回放仍不替代独立全套QA或最终验收；独立结论及覆盖范围以各自原报告为准。timer只覆盖真实源码的确定性回放，未覆盖浏览器初始化或TypeScript编译；不证明同OS操作者无法改配置、不认证客户本人，也不自动发现未声明环境/脚本依赖。
