---
id: role-sync-preflight-feature
type: feature
title: 每个开发角色的云端同步状态预检
created: "2026-09-25"
updated: "2026-09-25"
timezone: Asia/Shanghai
status: verified
related:
  - local-dashboard-config-feature
events:
  - date: "2026-09-25"
    kind: created
    summary: 角色激活时检查云端配置和本机持续同步进程
  - date: "2026-09-25"
    kind: implemented
    summary: 添加无密钥状态命令、独占运行租约和角色卡预检指令
  - date: "2026-09-25"
    kind: verified
    summary: 102 项回归测试及 testa 真实进程停止、运行、拒绝重复启动和未配置场景通过
  - date: "2026-09-25"
    kind: verified
    summary: 真实 SSL 意外断开暴露持续进程会退出；增加临时网络故障重试与认证失败停机测试
---

# 角色同步预检

角色在开始开发前运行技能的 `scripts/check_dashboard_sync.py --root <project>`。命令只检查本地项目是否有云端配置、持续同步进程是否持有独占租约，以及最后一次成功上传时间；不读取或输出 Key。未配置云端时，角色应提醒并询问用户该项目是否需要云端，回答在同一项目中跨角色保留，避免反复打扰。已配置但进程停止时应报告云端可能过期，并只在现有授权内恢复；运行中则复用。

持续同步进程独占一个项目租约，第二个相同项目的进程被拒绝。进程正常退出或崩溃后，锁自动释放，状态检查会报告停止，即使上次成功时间仍保留。状态只说明本机进程与最近上传，不证明云端数据已可读；需要时仍做云端回查。

在 `testa` 真实运行中，同步器曾因 `SSL: UNEXPECTED_EOF_WHILE_READING` 退出；预检正确显示 `running=false` 和 `lastError=URLError`。持续模式现对临时网络失败与服务器 5xx 记录错误后按间隔重试，上传成功时清除错误；认证或非法请求等不可重试 4xx 仍停止，避免无效 Key 无限请求。一次性同步保留失败即返回的行为。

验证：`python3 -m unittest discover -s scripts/tests` 共 102 项通过。真实 `testa` 项目中，停止旧版进程后预检显示 `configured=true, running=false`；启动新版持续同步后显示 `configured=true, running=true` 和最近成功时间；第二个持续进程退出码 2，未发送重复请求。未配置的临时项目显示 `configured=false, running=false`。本功能没有改动 Dashboard 页面，检查发生在角色开发预检。
