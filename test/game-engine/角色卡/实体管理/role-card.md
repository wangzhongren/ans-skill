# 实体管理

管理游戏实体的创建、销毁、组件增删查，以及实体生命周期。

## 必读文档

1. `boundary.md` — Section 1 是修改白名单
2. `ans-governed-construction` skill — 治理规则与质量约束
3. `src/models/ecs.ts` — 实体与组件类型定义（只读引用）

## 执行原则

- Section 1 是唯一的修改授权
- 只修改任务所需的文件
- 跨范围修改需回到客户端
- 未列出的文件默认只读
- 实现顺序（Model -> Service）仅在本角色内生效
- 与其他角色并行执行

## 质量约束

**相邻层合规：** Service 层只能引用 Provider 的 public 入口

**代码质量：** 每个方法都有真实实现（无空桩、无 TODO）；变量名描述性强（无单/双字母缩写，循环计数器除外）；禁止三元运算符；每个 try/catch 必须输出错误

**测试：** 测试文件在 `test/实体管理/` 目录下

## 交付物

- `changelog.md`
- `functional-description.md`
- `api-spec.md`