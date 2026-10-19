# 统筹调度工作备忘

- 2026-10-19：本上下文初始绑定 `scheduler`，未曾承担开发、测试、架构或验收身份。写入白名单为本角色 `feature-map.md`、本文件和当日 `docs/coordination/2026-10-19_role-authority-split-handoff.md`。
- 客户已要求落实职责拆分并指示修改；后续明确取消组长层级，角色 `group` 只分类、无 `groupDuty`。统筹直接安排和接收每个角色反馈；招聘与边界由独立内置团队组建角色处理。
- 本仓库改造 task_ops 本身不等于使用 task_ops 派发运行时项目任务。当前没有 scheduling 路径授权，不建立虚构任务、凭证或执行记录；只记录实际角色协作。
- 用户后来新增独立策划角色；团队组建建卡，策划自己只建导航/memo，规范给planning-role及新路由，原PM在设计第11节显式追加新决定。标准显式升v2，仅C8变，C1–C7不变，未重复本轮历史方案或客户授权。
- 任务工具49开发单测、固定测试最终201项（无skip、CLI25）、独立timer/Dashboard已实际通过。原验收上下文 `/root/authority_split_scheduler/acceptance` 对C1–C8正式pass；原报告与限制见[本轮交接](docs/coordination/2026-10-19_role-authority-split-handoff.md)。
- 终验后PM/工具只补当前文档真实状态/链接，源码/设计/标准/法案/契约未变；QA已轻量刷新同196输入清单（最终e2c3fb2b…31712），验收已补最终引用并维持pass，结果sha1f1b0412…89828。本轮完成，未重复程序全套；真实项目任务未启用，无发布/安装/推送。
