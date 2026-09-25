---
id: sync-status-tempdir-fix
type: fix
title: 同一同步进程在不同临时目录环境下被误判为停止
created: "2026-09-25"
updated: "2026-09-25"
timezone: Asia/Shanghai
status: verified
related:
  - role-sync-preflight-feature
events:
  - date: "2026-09-25"
    kind: created
    summary: 审核总览文档时发现角色预检在不同 TMPDIR 下误报停止
  - date: "2026-09-25"
    kind: implemented
    summary: POSIX 运行锁固定在 /tmp 的用户私有目录；Windows 使用用户目录，不再由临时目录环境变量决定
  - date: "2026-09-25"
    kind: verified
    summary: 不同 TMPDIR 的父子进程预检和 104 项技能回归测试通过
---

# 同步状态误报

实测同一个 `testa` 同步进程仍在运行：正常环境预检返回 `running=true`；只在检查命令中设置 `TMPDIR=/private/tmp`，便返回 `running=false`。原因是同步器把锁文件放在 `tempfile.gettempdir()` 下，不同终端或托管进程可能得到不同目录，角色预检就无法看到同一把锁，还可能错误地启动第二个同步器。

修复将 POSIX 运行锁固定到 `/tmp/ans-dashboard-sync-<uid>/`，Windows 使用当前用户目录下的 `.ans-dashboard/runtime/`。每个项目仍由规范化根路径的哈希隔离；目录只允许当前用户访问，状态不包含 Key。进程状态和最后成功时间仍由锁与状态文件共同报告。

回归测试在父子进程使用不同 `TMPDIR` 的情况下检查同一项目的租约可见性，并覆盖重复启动；`python3 -m unittest discover -s scripts/tests` 共 104 项通过。真实验证需重启旧版同步进程，让它改用新路径；代码更新本身不会把正在运行的旧进程迁移到新锁。
