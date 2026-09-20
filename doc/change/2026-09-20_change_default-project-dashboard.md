---
id: default-project-dashboard-change
type: change
title: Dashboard 成为技能提供的通用项目能力
created: "2026-09-20"
updated: "2026-09-20"
timezone: Asia/Shanghai
status: verified
related:
  - role-function-graphs-feature
events:
  - date: "2026-09-20"
    kind: implemented
    summary: 项目交接时默认启动或复用当前项目 Dashboard，通用页面与服务由技能目录提供
  - date: "2026-09-20"
    kind: verified
    summary: 通用临时项目测试、项目根身份字段、格式与引用检查通过
---

# 通用项目 Dashboard

1. 主实现始终位于技能的 assets/、scripts/ 和 references/。test/game-engine 只提供验证输入和演示定义，不是其他项目的运行依赖。
2. 中英文主文件、bootstrap、项目默认角色和角色反馈流程均接入默认 Dashboard：验收后对实际项目启动或复用本地服务，交付 URL。使用空闲端口，已知旧会话只有根 URI 匹配才能复用。
3. 当前项目只提供角色卡、协同状态和功能演示定义；没有执行记录就显示未上报，没有实现就不伪造流程。项目图谱输出须在获批设计范围内。用户关闭或环境不支持时说明限制，不阻塞其他工作。
4. 删除查看器对示例角色名的默认偏好，服务提供 projectRootUri 供项目身份核对。README 明确通用路径与测试项目区别。

测试：此前完整 62 项回归通过；本次身份字段与默认流程调整后，12 项 Dashboard 测试、10 项角色图谱测试通过；它们使用通用临时 role-cards 项目，不依赖游戏示例。源码和文档引用检查通过。

本地安装目录已确认无独立改动，通用包已从工作区同步，50 个文件逐字节校验一致；未复制验证产物或游戏示例图谱。原安装内容已备份到 output/installed-skill-backup-tplbt7ld。GitLab 提交和推送仍未执行，原有工作区修改保留。
