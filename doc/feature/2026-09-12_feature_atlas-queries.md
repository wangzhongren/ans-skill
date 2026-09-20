---
id: atlas-queries-feature
type: feature
title: AI 查询本地五层引用图谱
created: "2026-09-12"
updated: "2026-09-12"
timezone: Asia/Shanghai
status: verified
related: []
events:
  - date: "2026-09-12"
    kind: created
    summary: 支持 AI 从 JSON 查询依赖、引用方、路径与影响范围
  - date: "2026-09-12"
    kind: implemented
    summary: 新增只读查询工具、快照一致性检查与有限 JSON 输出
  - date: "2026-09-12"
    kind: verified
    summary: 14 项脚本测试及 Skill 格式检查通过
---

# AI 查询本地五层引用图谱

## 需求与实现

在已有同步工具上新增查询能力，让 AI 只读取相关子图，不必将完整 JSON 放入上下文。该功能属于 Skill 工具，不改变业务项目的五层调用规则或图谱格式。

```text
scripts/
  sync_atlas.py                 # 复用现有扫描与证据核对逻辑
  query_atlas.py                # 新增：查询命令
  tests/test_query_atlas.py     # 新增：8 项查询测试
references/code-atlas.md        # 查询参数、结果与限制
README.md                      # 查询用法
SKILL.md                       # 查询任务加载路由
```

- [查询实现](../../scripts/query_atlas.py)
- [查询测试](../../scripts/tests/test_query_atlas.py)
- [查询说明](../../references/code-atlas.md)

支持直接依赖、直接引用方、一个最短有向候选路径和反向传递依赖。环路不会导致无限遍历。结果保留源文件行号、引用类型和证据类型，并用节点数、深度及结果数量限制输出；触及界限时明确标记截断。

查询前按当前源码重建并比对 JSON 中的文件、关系和证据，防止过期或被手动改写的扫描事实参与查询。核对阶段只读，不自动写回 JSON 或 HTML。退出码：0 为当前快照查询完成（可以没有路径），3 为过期，2 为错误。

## 验证

从仓库根目录执行：

```sh
python3 -m unittest discover -s scripts/tests -v
```

全部 14 项通过，其中新增 8 项覆盖方向与行号证据、最短路径与无路径、环中的传递影响、三种遍历/输出界限、非法节点与格式、过期与篡改、只读 CLI 输出、同点零长度路径。测试发现 macOS 临时目录别名比较问题，已通过统一 resolve 修正。

Skill 格式、Markdown 链接、代码围栏和 `git diff --check` 检查通过。未修改 HTML、同步器或被扫描业务项目，不需重测页面交互或生成工具自身的五层业务图谱。

## 限制

静态文件引用不等于运行时函数调用；查不到路径不证明不存在动态调用。影响查询只返回候选依赖方，不证明行为受影响，也不自动给出完整测试清单。每次一致性核对仍需扫描配置的源码范围；有限输出不等于常数时间查询，检查完成后的源码改动也不会被实时锁定。
