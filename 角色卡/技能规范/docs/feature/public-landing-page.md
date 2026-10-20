---
id: public-landing-page-feature
type: feature
title: ANS 中英文公开介绍页
created: "2026-10-20"
updated: "2026-10-20"
timezone: Asia/Shanghai
status: implemented-unverified
related: [public-landing-page-product-p1, public-landing-page-technical-d1]
events:
  - date: "2026-10-20"
    kind: implemented
    summary: 按客户确认的P1和LP-D1（含OPT-EN）实现双语静态页与Pages声明；待独立界面检查、部署及验收
---

# ANS 中英文公开介绍页

第一次听说 ANS 的开发者可以直接阅读角色责任、文件边界和协作方式，再复制 Codex 或 Claude Code 的安装命令，或继续查看源码与论文。中文是主入口，完整英文页讲同一内容。工单草稿例子明确标为协作示意，不代表 ANS 已交付一个工单应用。

当前页面文件已经写好，开发静态检查已完成；独立浏览器检查、公开部署和验收还没完成。预期中文地址为 `https://wangzhongren.github.io/ans-skill/`，英文为其 `en/` 子页；在真实线上核对前，不把预期地址写成已可用的发布结果，也不向 README 添加入口。

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

页面陈述的验证事实注明 2026-10-20：源仓库 236 项（包含开发 69 和 CLI 40），库存另 60 种测试方法，链接[原独立验收报告](../../../验收/docs/acceptance/2026-10-20_workflow-fixes-result.md)。这些不代表新页面已验收，也不承诺提效、性能或未来可靠性。

## 代码位置与发布流程

| 文件 | 实际职责 |
| --- | --- |
| `site/index.html`、`site/en/index.html` | 完整中文/英文正文、命令、来源、lang、description、canonical和双向/自身hreflang |
| `site/style.css` | 共用阅读布局、响应式、命令横向滚动及可见焦点 |
| `site/main.js` | 仅渐进复制和可访问成功/失败状态 |
| `site/sitemap.xml` | 两个实际预期canonical绝对URL，不编造lastmod |
| `.github/workflows/pages.yml` | main的site或workflow变动触发，手动部署同样仅main；官方Actions上传site产物 |

资源、语言和站点地图均使用 `/ans-skill/` 项目前缀。无 JS 路由、noindex、项目 robots.txt、自动语言重定向、离线缓存或故障切换。页面暂不可访问时，读者可直接打开公开源码 README、论文与 MIT 原地址；没有自动兜底服务。搜索抓取、收录时间、排名和摘要不作保证。

Pages 声明依次使用 checkout@v6、configure-pages@v5、upload-pages-artifact@v4、deploy-pages@v4。仅 contents:read、pages:write、id-token:write，单 deploy job 的 github-pages environment 使用实际page_url。没有构建依赖；上传 path 为 site，不上传整个仓库、治理定义、任务、runtime、密钥或Git数据。

账户操作由获授权可信端执行：先启用 Actions Pages，再按批准范围同步双仓库差额并触发部署；独立线上核对后才添加 README 单条链接与 GitHub About homepage。仓库提交可含本次已批准的所有权和设计资料，Pages artifact 只含 site，二者范围不同。本角色未持账户权限，未 push、commit、安装或改 About。失败应保留真实日志，在已批准范围修复后从main重试，不以本地预览冒充上线。

## 开发核对与交接

已运行 Node 的 `--check site/main.js` 语法检查。Python HTMLParser 定点检查两页 lang、唯一canonical、双向/自身hreflang、唯一ID、本页锚点、`/ans-skill/`本地资源及语言目标存在；XML解析确认 sitemap 仅列两页面。两页完整命令直接在HTML，默认按钮hidden，不依赖JS注入。workflow字段与LP-D1逐项核对，未实际部署Actions。

固定QA统一启动按 `/ans-skill/` 挂载的本地服务并使用唯一浏览器会话；本角色不另外起服务。桌面1440×900、手机390×844、真实键盘/复制成功与拒绝、禁JS、线上HTTP与artifact清单由独立QA实际检查；独立验收另判结果。本轮不重跑236项业务套件。当前记录没有将待检查项目写成通过。

## 演变历史

| 日期 | 类型 | 状态 | 变化 | 依据 |
| --- | --- | --- | --- | --- |
| 2026-10-20 | 设计/实施 | 静态候选已实现，独立检查与发布待完成 | 中文主入口、完整英文、渐进复制、项目路径元数据与有限Pages声明 | [P1](../../../策划/docs/design/2026-10-20_design_public-landing-page-product.md)、[LP-D1](../../../项目管理/docs/design/2026-10-20_design_public-landing-page.md)，客户明确确认含OPT-EN及发布 |
