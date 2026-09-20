---
id: atlas-root-output-fix
type: fix
title: 分离图谱项目根目录、源码根目录与输出位置
created: "2026-09-20"
updated: "2026-09-20"
timezone: Asia/Shanghai
status: verified
related: []
events:
  - date: "2026-09-20"
    kind: created
    summary: game-engine 根目录和 src 下分别生成了 doc/architecture
  - date: "2026-09-20"
    kind: implemented
    summary: 项目根路径规范化，自动识别 src，图谱固定输出到根目录 doc
  - date: "2026-09-20"
    kind: verified
    summary: 52 项回归通过，实际图谱包含 41 个文件和 63 条引用
---

# 图谱目录重复与漏扫修复

1. **原因**：旧 --root 同时代表五层源码位置和输出位置。传项目根只收录 main；传 src 能扫描层目录，却在 src/doc 下生成第二份产物。旧快照分别有 1 个和 40 个文件。
2. **改动**：[同步器](../../scripts/sync_atlas.py) 的 --root/--project-root 表示项目根，自动识别根目录及 src 内的层目录，同时保留根入口和共享资源。非标准布局用 --source-root；所有节点 ID 和源码链接相对项目根。输出默认固定 PROJECT/doc/architecture，自定义 --out 保持可用。
3. **查询与兼容**：[查询器](../../scripts/query_atlas.py) 复用同一布局规则。常规旧 --root PROJECT/src 调用归一到 PROJECT，不再生成 src/doc。src 有自身项目清单时保留独立项目语义，明确 source-root 时遵循显式选择。新增 sourceRoots 元数据参与快照新鲜度检查。
4. **实际整理**：确认两份旧 JSON 都没有 annotations/aiRelations 后，备份至 output/atlas-layout-backup-vrmpl043，再生成根目录快照并将 src/doc/architecture 旧产物移入备份。只移走已核实的 JSON/HTML，随后删除空的 src/doc；未修改业务源码或其他文档。已有根 docs 目录不属于本次重复图谱，不做无关迁移。

## 验证

- 新增 [8 项布局回归](../../scripts/tests/test_atlas_layout.py)：嵌套层与根入口/资源、旧调用同输出、查询路径与入口变更失效、自定义源/输出、Python src 导入、根层与 src 层并存、越界/符号链接拒绝、独立 src 项目。
- 全部 52 项测试通过：`PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s scripts/tests -q`。
- 实际命令 `python3 scripts/sync_atlas.py --root test/game-engine` 生成 41 个文件、63 条静态引用，未解析相对引用和解析错误均为 0。
- 从项目根和旧 src 路径执行 --check 均返回 CURRENT。
- 查询 main.ts → src/interface/engine.ts 成功，引用位置为 main.ts 第 5 行，明确标记为 JS/TS 启发式静态引用。
- 检查 JSON 与 HTML 内嵌快照一致，节点链接基准为项目根；src/doc 不再存在。

README、图谱参考和角色执行命令已同步。旧快照改变文件 ID 基准时必须重新生成；若含人工注释，先确认和迁移，不能直接丢弃。本次实际旧产物不含此类内容。修复不证明静态图等同于完整运行时调用图。

保留此前未提交改动，未提交、推送或覆盖已安装 Skill。
