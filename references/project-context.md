# 项目理解：让人和 AI 看懂当前项目

每个项目只有一个 `project-context/context.sqlite3`，用 `role_id` 区分角色。它是**当前项目的说明索引**：流程、数据、接口和术语各有总览与详情。角色职责和可修改的文件仍以 `role-card.md`、`boundary.md` 为准；代码和正式设计文档才是行为依据。不要为了让页面好看而猜测源码没有证实的内容。

## 流程先回答“这是干嘛的”

打开一个流程，读者应先知道三件事：

1. **要做什么**：谁要完成什么事，系统帮他达成什么目标，写在 `flow.intent.purpose`。
2. **成功后怎样**：用户看到什么、哪些数据被保存或改变，写在 `flow.intent.success`。
3. **失败时怎样**：用户看到什么、数据是否保持原样；源码有明确处理时写在 `flow.intent.failure`，没有证据就留空并标注待核实。

页面会把 `purpose` 放在流程标题下，并作为流程总览的摘要。**不要**用“从入口到处理结果”“执行相关校验”这类套话，也不要把按钮是否可点、身份是否有效等条件当作流程用途。条件属于下面的触发和判断分支。

旧流程没有 `intent` 时，页面会显示“用途待补充”，`validate` 会列出对应流程 ID。**不要一口气按按钮名称批量生成说明。**只处理当前任务相关的流程：先看入口代码、业务代码和测试，核对用户可见结果，再由拥有该流程的角色更新这一条。其余流程保持“待补充”，比写一段猜测更诚实。

例如，只有源码确实这样工作时，才可以把“保存工单草稿并退出”解释为：“用户暂不提交工单时，保存当前内容为草稿并离开编辑页，之后可以继续编辑。”成功和失败结果也必须分别核对实际代码与测试，不能照抄这个例子。

### 触发、分支和排查点放在哪里

- `flow.triggers` 写**何时开始**，例如“用户点击保存并退出按钮”；按钮处理函数放在 `ref`。同次点击产生的 HTTP 请求是流程的一步，不再另造一个 Event。
- `flow.graph.nodes` 写实际动作、判断、完成和异常；判断节点 `kind: "decision"` 要有代码位置 `ref`。
- `flow.graph.edges` 写从哪个节点到哪个节点。判断的每一条边都必须写 `condition`，如 `if 内容有效`、`else 内容无效`，不能只画两根无名线。
- 完成节点 `kind: "end"` 写清最终结果。异常节点 `kind: "error"` 写清用户看到的失败结果，还要有 `ref` 和至少一个 `checks`：出问题先检查哪项输入、日志或测试。
- `flow.inputs`、`flow.outputs`、`flow.interfaces` 引用**同一角色**已录入的数据和接口主题。流程详情会直接显示这些主题的字段和请求 URL。

图里的每个节点都要能从入口走到，也要有路走到完成或异常；可以有重试环，但不能留下走不出去的孤立分支。只有真实代码中的分支才写进图。旧流程只有 `steps` 时，Dashboard 会画一条线性路径并明确提示“尚未记录判断和异常分支”；**不要由 AI 猜出 if/else**。新分支图可以只写 `graph`，不必再维护一份重复的 `steps`。

下面是格式示意，路径和业务结果必须换成项目中已验证的事实：

```json
{
  "category": "flows",
  "title": "保存草稿",
  "flow": {
    "intent": {
      "purpose": "用户暂不提交时，保存当前内容为草稿，之后可以继续编辑。",
      "success": "草稿已保存，页面返回列表。",
      "failure": "保存未成功时保留当前输入并提示原因。"
    },
    "triggers": [{"when": "用户点击保存草稿", "ref": "src/interface/save_button.py"}],
    "graph": {
      "nodes": [
        {"id": "start", "kind": "start", "title": "点击保存"},
        {"id": "valid", "kind": "decision", "title": "内容能保存？", "ref": "src/services/validate.py"},
        {"id": "saved", "kind": "end", "title": "保存成功", "description": "草稿已保存，页面返回列表。"},
        {"id": "invalid", "kind": "error", "title": "提示错误", "description": "草稿未保存，页面保留当前输入。", "ref": "src/interface/save_button.py", "checks": ["检查必填字段和错误提示"]}
      ],
      "edges": [
        {"from": "start", "to": "valid"},
        {"from": "valid", "to": "saved", "condition": "if 内容有效"},
        {"from": "valid", "to": "invalid", "condition": "else 内容无效"}
      ]
    }
  }
}
```

定位故障时，先在图里找**异常节点或停住的节点**，看是哪条条件边走过来的，再打开该节点的 `ref`，按 `checks` 检查真实输入、日志和测试。图提供线索，不代替运行证据或源码调查。AI 可用下面的 `get <flow-id>` 命令取回同一份图，按节点和条件追踪，不必扫描整个仓库生成代码图谱。

## 数据、接口、定义分别写什么

| 类别 | 要写清的内容 | 页面展示 |
| --- | --- | --- |
| `data` | 数据由哪个角色负责、每个字段叫什么、类型和是否必填 | 字段表 |
| `interfaces` 网络接口 | 协议、HTTP 方法、请求 URL、输入和输出字段 | 网络接口总览与详情 |
| `interfaces` 内部接口 | 对外公开的代码入口、输入和输出字段 | 内部接口总览与详情 |
| `definitions` | 业务术语或稳定规则，写具体含义 | 定义总览与详情 |

流程的按钮点击等开始条件直接写在 `triggers`，不需要为了它额外建立 `events` 主题。旧 Event 数据仍能读，供迁移时参考。不要编造源码没有的字段、URL、条件或错误结果。

## AI 查询和修改用同一个工具

在已安装技能目录运行。把 `/absolute/path/to/project` 换成真实项目根目录；`ticket` 换成角色文件夹名：

```sh
python3 scripts/context_store.py --root /absolute/path/to/project --role ticket outline
python3 scripts/context_store.py --root /absolute/path/to/project --role ticket list --category flows
python3 scripts/context_store.py --root /absolute/path/to/project --role ticket get save-draft
python3 scripts/context_store.py --root /absolute/path/to/project --role ticket validate

# 写入前须有该角色已接受的 boundary.md 行级范围
python3 scripts/context_store.py --root /absolute/path/to/project --role ticket --actor-role ticket upsert save-draft --input flow.json --expect-revision 0
```

写入已有主题前先 `get`，用返回的 `revision` 填 `--expect-revision`；新主题用 `0`。工具只允许角色修改自己的行，但它**不能证明当前 AI 已得到客户授权**，仍须核对角色边界。

新版数据库为第 7 版。原第 6 版可以继续查看和修改旧线性流程；要写新 `intent` 或 `graph` 时，先备份 `project-context/context.sqlite3`，确认项目已授权升级共享数据库，再运行 `python3 scripts/context_store.py --root /absolute/path/to/project --role ticket --actor-role ticket migrate`。迁移保留原有主题；旧版 1–5 也可通过该命令升级。普通的角色行级写入许可本身**不等于**可以升级共享数据库。

这个数据库记录“现在是什么”，不是历史时间线。带日期的设计、功能、修改和修复记录仍放在 `docs/`。每次代码行为经验证发生变化后，拥有该角色的 AI 才更新对应项目理解；缺失或过时的说明不能当作“源码里没有这个功能”的证据。
