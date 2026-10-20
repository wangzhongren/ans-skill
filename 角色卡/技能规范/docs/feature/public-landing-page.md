---
id: public-landing-page-feature
type: feature
title: ANS 中英文公开介绍页
created: "2026-10-20"
updated: "2026-10-20"
timezone: Asia/Shanghai
status: verified
related: [public-landing-page-product-p1, public-landing-page-technical-d1]
events:
  - date: "2026-10-20"
    kind: implemented
    summary: 按客户确认的P1和LP-D1（含OPT-EN）实现双语静态页与Pages声明；待独立界面检查、部署及验收
  - date: "2026-10-20"
    kind: deployed
    summary: 可信端双仓发布并完成首次Actions部署，线上五资源200且同候选字节；最终线上验收待独立结论
  - date: "2026-10-20"
    kind: verification
    summary: 消费独立验收最终pass，P1和LP-D1含英文及发布范围通过；保留公开英文复制未成功观察与方法限制
---

# ANS 中英文公开介绍页

第一次听说 ANS 的开发者可以直接阅读角色责任、文件边界和协作方式，再复制 Codex 或 Claude Code 的安装命令，或继续查看源码与论文。中文是主入口，完整英文页讲同一内容。工单草稿例子明确标为协作示意，不代表 ANS 已交付一个工单应用。

页面已经公开部署：[中文首页](https://wangzhongren.github.io/ans-skill/)、[完整英文页](https://wangzhongren.github.io/ans-skill/en/)。独立验收已按客户确认的P1和LP-D1（含英文及发布范围）给出通过结论。线上五份资源返回200，且与已测源码逐字节相同；已公开的README与GitHub About入口均已核对。此处引用独立结论，不代替验收角色判断，也不承诺所有浏览器或第三方服务的未来行为。

## 读者怎样使用

正文、章节链接、安装命令、FAQ 和来源直接写在 HTML 中。读者按问题、草稿示意、角色与五层、开始步骤、安装、验证记录和 FAQ 的顺序阅读，也可以从顶部跳到安装或切换语言。页面用系统字体与 CSS 图示，不加载第三方字体、统计或账户服务。

```mermaid
flowchart TD
  enter[打开中文或英文介绍页] --> read[阅读真实正文和明确标注的协作示意]
  read --> choose{想继续做什么}
  choose -->|查看依据| source[打开源码、README、论文或MIT]
  choose -->|开始使用| install[选Codex或Claude的完整安装命令]
  install --> js{复制增强脚本可用吗}
  js -->|否| manual[选中HTML中的命令手动复制]
  js -->|是| click[按复制按钮]
  click --> clipboard{Clipboard写入成功吗}
  clipboard -->|是| success[可访问状态提示已复制]
  clipboard -->|拒绝或不可用| failed[显示手动复制提示，不报告成功]
  read --> language[通过真实链接切换另一语言页]
```

两组安装命令分别创建 `.agents/skills`、`.claude/skills`，从公开 GitHub 仓库 clone 到对应 `ans-governed-construction` 目录。已有目录按公开 README 更新，不覆盖删除。页面不实际执行安装。禁 JavaScript 时，按钮不出现，完整正文、链接和可选命令仍然可用。

复制按钮使用原生 button，脚本只解除 hidden 并处理 Clipboard。只有真实 writeText 成功才提示成功；无 API 或拒绝时给手动复制提示。状态使用 role=status/aria-live，按钮保留可见键盘焦点。复制不改变页面正文、路由或元数据。

页面陈述的验证事实注明 2026-10-20：源仓库 236 项（包含开发 69 和 CLI 40），库存另 60 种测试方法，链接[原独立验收报告](../../../验收/docs/acceptance/2026-10-20_workflow-fixes-result.md)。这些是此前工作流修复的历史检查，不计为新页面测试，也不承诺提效、性能或未来可靠性。

## 代码位置与发布流程

| 文件 | 实际职责 |
| --- | --- |
| `site/index.html`、`site/en/index.html` | 完整中文/英文正文、命令、来源、lang、description、canonical和双向/自身hreflang |
| `site/style.css` | 共用阅读布局、响应式、命令横向滚动及可见焦点 |
| `site/main.js` | 仅渐进复制和可访问成功/失败状态 |
| `site/sitemap.xml` | 两个实际canonical绝对URL，不编造lastmod |
| `.github/workflows/pages.yml` | main的site或workflow变动触发，手动部署同样仅main；官方Actions上传site产物 |

资源、语言和站点地图均使用 `/ans-skill/` 项目前缀。无 JS 路由、noindex、项目 robots.txt、自动语言重定向、离线缓存或故障切换。页面暂不可访问时，读者可直接打开公开源码 README、论文与 MIT 原地址；没有自动兜底服务。搜索抓取、收录时间、排名和摘要不作保证。

Pages 声明依次使用 checkout@v6、configure-pages@v5、upload-pages-artifact@v4、deploy-pages@v4。仅 contents:read、pages:write、id-token:write，单 deploy job 的 github-pages environment 使用实际page_url。没有构建依赖；上传 path 为 site，不上传整个仓库、治理定义、任务、runtime、密钥或Git数据。

账户操作由获授权可信端执行。本次源仓库发布版本为 `68d5b8c`，公开仓库版本为 `0875d111`。可信端先启用Actions Pages，再同步双仓库相关差额；[首次部署run 39379338186](https://github.com/wangzhongren/ans-skill/actions/runs/39379338186)实际success。Pages使用workflow部署且HTTPS开启。线上中文、英文、style.css、main.js、sitemap.xml五URL均200，逐字节匹配已测最终source。

可信端的 `control/online-release-checks.json`、`pages-enabled.json`、`pages-runs.json` 与实际 `github-pages-artifact.zip` 保留发布检查事实。真实ZIP内TAR仅五份站点文件：index.html、en/index.html、style.css、main.js、sitemap.xml，没有符号链接、私密数据或其他仓库内容。仓库提交包含已批准的所有权和设计资料，Pages artifact仅含site，两者范围不同。

README入口已发布，源版本 `5f175583`、公开版本 `d267c524`；原GitLab安装地址保留。About操作只更新homepage并重新读取核对，description/topics保持原值，记录见可信端 `control/about-updated.json`。独立QA核对了公开README与实际About入口。本角色未持账户权限，未push、commit、安装或改About。后续部署失败仍应保留日志，在已批准范围修复后从main重试。

## 开发核对与交接

已运行 Node 的 `--check site/main.js` 语法检查。Python HTMLParser 定点检查两页 lang、唯一canonical、双向/自身hreflang、唯一ID、本页锚点、`/ans-skill/`本地资源及语言目标存在；XML解析确认 sitemap 仅列两页面。两页完整命令直接在HTML，默认按钮hidden，不依赖JS注入。workflow字段与LP-D1逐项核对；实际Actions部署由可信端完成，见上节发布记录。

固定QA统一启动按 `/ans-skill/` 挂载的本地服务，使用同一浏览器会话查看桌面1440×900、手机390×844，检查键盘焦点、四组中英Codex/Claude复制成功及禁JS阅读；本角色没有另起服务或浏览器。真实浏览器布局、四组本地复制成功与禁JS检查通过；独立QA另核公开中英文页面、语言跳转、FAQ及入口，独立验收最终按LP-D1范围判通过。原始收据由可信端保存，不作为网站资产上传。

公开英文页曾有一次Enter操作：页面显示成功，但读取剪贴板仍为此前的Claude命令，后续读取也未变化；该次未计通过，原因未定，不声称已修复或归因于产品/工具。复制成功判据来自同候选本地四组完整剪贴板匹配，以及线上中文Codex的真实成功。独立验收在保留该观察的前提下，判断现有证据满足本次LP-D1范围；不扩称所有线上交互均已通过。

后续QA在同一公开英文页完成三组有界复核：每组刷新并确认状态恢复初始，先真实复制Claude命令、核对完整剪贴板作为不同基线，再分别用Codex鼠标点击、精确按钮Enter和Space操作；三组完整剪贴板均匹配Codex命令。本轮没有复现旧异常，没有修改代码、部署或环境，也没有增加第四组重试。旧异常记录及原因未定仍保留；这些后续实测不代表已查明原因或完成修复。

复制失败路径以实际main.js在Node中的8个受控拒绝/无API用例补证。这些用例只证明脚本失败分支。浏览器实际Clipboard权限拒绝，以及用户手选两行完整命令后的剪贴板比对，均未实测。论文保留原指定URL；自动GET返回403属于第三方检查限制，没有换链接、绕过限制或声称内容可达已核。页面中的源236项（含69/40）与库存另60项是此前工作流修复历史，不是新页面的测试数量；本次没有重跑该套件。

## 2026-10-20：用短句说明用户价值

按用户直接授权，中英文首屏和四点说明改为接手时少解释、修改前先定范围、多AI分工知道找谁、以后能查修改原因。复用现有样式，链接、安装命令和复制行为保持不变。此次只做HTML结构、既有属性与命令对照及格式静态检查，没有重跑浏览器、复制或业务测试，也不改写此前验收结论。

## 演变历史

| 日期 | 类型 | 状态 | 变化 | 依据 |
| --- | --- | --- | --- | --- |
| 2026-10-20 | 设计/实施 | 静态候选已实现，独立检查与发布待完成 | 中文主入口、完整英文、渐进复制、项目路径元数据与有限Pages声明 | [P1](../../../策划/docs/design/2026-10-20_design_public-landing-page-product.md)、[LP-D1](../../../项目管理/docs/design/2026-10-20_design_public-landing-page.md)，客户明确确认含OPT-EN及发布 |
| 2026-10-20 | 发布/验证 | 已上线，独立验收通过 | 双仓相关差额发布、首次Actions成功、五资源200且字节一致、artifact限定五站点文件，README/About入口核对；保留上述方法限制 | [实际部署run](https://github.com/wangzhongren/ans-skill/actions/runs/39379338186)，公开版本0875d111 |
