---
id: role-maintainer-stance
type: change
title: 角色以正式项目长期维护者的立场工作
created: "2026-09-30"
updated: "2026-09-30"
timezone: Asia/Shanghai
status: verified
related: [role-common-and-testing]
events:
  - date: "2026-09-30"
    kind: created
    summary: 在角色卡开头明确长期维护者的工作定位
---

# 让角色从长期维护项目的角度作判断

角色知道自己能改哪些文件，也需要理解自己的工作会进入真实项目，被用户使用，并由后续维护者继续修改。

这次在每张角色卡开头明确工作立场：把自己看作所负责部分的长期维护者，理解上下游和项目已有设计，对实际交付负责，考虑接手的人能否理解并继续完善。设计投入与当前需求相称。

## 改在哪里

1. [角色卡模板](../../references/role-card.md#working-stance-for-every-role)：增加通用工作立场，并放进生成角色卡的正文开头。
2. [项目管理角色](../../references/project-role.md)、[测试角色](../../references/test-role.md)：沿用相同立场，分别从整体配合和真实使用效果理解自己的责任。
3. [初始化规则](../../references/bootstrap-workflow.md)：创建或更新角色卡时写入这个定位，覆盖开发、装配、项目管理和测试角色。
4. [技能入口](../../SKILL.md)、[中文说明](../../SKILL.zh.md)、[README](../../README.md)：说明这套角色共同的工作定位。

本次调整的是角色作判断的出发点，没有增加针对日志等具体做法的禁令、技术检查表或审批步骤。原有的权限、测试、方案确认和选装规则保持不变。没有修改业务代码或已有项目的角色卡。

## 验证

已检查本次文档的本地链接、角色工作立场的引用位置、YAML 头部和改动范围，`git diff --check` 通过。原有测试及错误处理规则没有变化。这次没有改程序，不重复运行程序测试。角色在真实任务中是否更稳定地采用这一立场，还需要后续观察。
