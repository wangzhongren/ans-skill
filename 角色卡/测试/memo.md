# 测试角色工作备忘录

- 2026-10-10：本轮负责独立设计并验证项目工程法案与角色 memo 指南；授权范围只有自己的 memo、feature-map、指定 design/change 文档。依据：[角色边界](boundary.md)与[已确认方案](../../doc/design/2026-10-10_design_project-plan-role-memo.md)。
- 当前指南位于 `references/project-rules.md`、`references/role-memo.md`；按[验证设计](docs/design/2026-10-10_design_project-rules-memo-validation.md)检查，不能把场景推演当成 GUI/线程行为或性能实测。
- 已确认规范功能说明与 change 记录存在且链接可达；当前法案版本标为 1。后续复核已关闭首轮元数据与状态问题；最新指南 SHA-256、链接和元数据结果见[最终验证记录](docs/change/2026-10-10_change_project-rules-memo-validation.md)。后补功能与 change 两份 YAML 头的复核均通过，当前 SHA 分别为 `092f155b…` 和 `382fbfbf…`。
- 续接时先读本 memo 和当前验证设计，再记录实际候选版本、输入、已运行检查及未测范围；写入始终以当次 Section 1 为准。
- README 增量已单独复核：本仓库法案路径、memo、初始化、权限/角色隔离与当前三角色分工表述符合方案；25 个本地链接/锚点有效，安装命令和来源引用保留。候选 README SHA-256 `30763672…`，详情见最终验证记录。
- 2026-10-19：固定【测试】按已授权分权方案新增独占 `scripts/tests/test_role_authority_flow.py`，使用真实子进程 CLI，不复用开发者 operate helper；本轮真实结果、候选与续接证据见[验证报告](docs/change/2026-10-19_change_role-authority-split-validation.md)。已有角色源码、单测、构建与治理文件仍只读。标准显式升 v2，仅 C8 补策划路由，C1–C7 程序标准不变。
- 当前独立25方法与最终完整发现201方法通过；本轮临时证据保存在 `/tmp/ans-independent-qa-20261019/`，最终全套日志 `full-suite-final.log`。Git新增用例曾因错误文案断言过窄失败，修正及重跑经过见原报告，旧日志仍保留。若相关产品/测试输入变化，再复测对应范围；不要把本轮 timer 当作浏览器或 TypeScript 编译证据，也不要把测试通过写成验收通过。
