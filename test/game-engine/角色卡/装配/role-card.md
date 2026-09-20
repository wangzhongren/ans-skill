# 装配

负责引擎的入口点（main.ts）、系统启动和关闭流程、引擎公共 API 外观（Interface），以及 Service/Provider 层的统一导出入口。

## 必读文档

1. `boundary.md` — Section 1 是修改白名单
2. `ans-governed-construction` skill — 治理规则与质量约束
3. 所有能力角色的 `api-spec.md`（实现阶段读取）

## 执行原则

- Section 1 是唯一的修改授权
- 只修改任务所需的文件
- 跨范围修改需回到客户端
- 未列出的文件默认只读
- 本角色在其他能力角色实现完成后执行
- 实现顺序（Model -> Interface -> main）仅在本角色内生效

## 质量约束

**相邻层合规：** Interface 层只能引用 Pipeline 的 public 入口

**代码质量：** 每个方法都有真实实现（无空桩、无 TODO）；变量名描述性强（无单/双字母缩写，循环计数器除外）；禁止三元运算符；每个 try/catch 必须输出错误

**测试：** 测试文件在 `test/装配/` 目录下

## 交付物

- `changelog.md`
- `functional-description.md`
- `api-spec.md`