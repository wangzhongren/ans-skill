# 输入

管理键盘、鼠标、游戏手柄等输入设备的轮询和事件处理。

## 必读文档

1. `boundary.md` — Section 1 是修改白名单
2. `ans-governed-construction` skill — 治理规则与质量约束
3. `src/models/input.ts` — 输入类型定义（只读引用）

## 执行原则

- Section 1 是唯一的修改授权
- 只修改任务所需的文件
- 跨范围修改需回到客户端
- 未列出的文件默认只读
- 实现顺序（Model -> Provider）仅在本角色内生效
- 与其他角色并行执行

## 质量约束

**相邻层合规：** Provider 层只能加载基础设施

**代码质量：** 每个方法都有真实实现（无空桩、无 TODO）；变量名描述性强（无单/双字母缩写，循环计数器除外）；禁止三元运算符；每个 try/catch 必须输出错误

**测试：** 测试文件在 `test/输入/` 目录下

## 交付物

- `changelog.md`
- `functional-description.md`
- `api-spec.md`