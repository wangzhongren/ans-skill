---
id: public-landing-page-technical-d1
type: design
title: ANS 静态介绍页与 GitHub Pages 发布方案
created: "2026-10-20"
updated: "2026-10-20"
timezone: Asia/Shanghai
status: draft
related: [public-landing-page-product-p1]
events:
  - date: "2026-10-20"
    kind: reviewed
    summary: 完成静态介绍页技术方案、实质评审与拟完成标准，待客户确认实施发布及英文选项
---

# ANS 静态介绍页与 GitHub Pages 发布方案

版本 **LP-D1**；承接[产品 P1](../../../策划/docs/design/2026-10-20_design_public-landing-page-product.md)。评审建议：**recommend approval，可供客户决定**。本次只写此文档，未建站、未测试、未改账户设置或部署；GitHub Pages 平台选择不等于本方案实施或发布授权。

## 1. 用户会看到什么

第一次听说ANS的人打开网页，即可看懂它怎样用角色责任、文件边界和明确交接组织AI开发，再复制安装命令或查阅依据。页面主中文，正文依次为：是什么/解决何事 → 工单草稿协作示意 → 角色与五层 → Codex/Claude安装 → FAQ → 源码/论文/MIT。工单例子明确标“示意”，不能写成ANS已经交付的业务应用；角色可跨多个代码层，Model共享，不是一层一个角色。

视觉采用清楚的长页叙述、章节导航和可阅读的协作/层次关系图，以大标题、具体例子和连续流程带出内容；用系统字体、CSS排版与HTML图示，不堆空泛卡片、额外图片资产或第三方字体。手机布局按阅读顺序纵向展开，图示不只靠颜色表达。

仅陈述README可核对的历史检查：截至2026-10-20源仓库236项，开发69和CLI40均包含其中；库存另60项。它们不是提效、速度或未来可靠性保证，不编用户量、评价或提升百分比。

安装区给macOS/Linux的两组完整可复制命令：先创建相应skills父目录，再从 `https://github.com/wangzhongren/ans-skill.git` clone到Codex的 `~/.agents/skills/ans-governed-construction` 或Claude的 `~/.claude/skills/ans-governed-construction`；目的目录已存在时提示按README更新，不覆盖删除。Windows及更多安装方式链接公开README；不改现有README的GitLab地址。

固定来源链接：[公开源码/README](https://github.com/wangzhongren/ans-skill)、[RFSG论文](https://zenodo.org/records/22824700)、[MIT](https://github.com/wangzhongren/ans-skill/blob/main/LICENSE)。页面不可访问时读者可手动访问这些原地址，不增加离线缓存、自动故障转移或服务。

## 2. 最小技术与搜索抓取方案

采用纯静态 `site/`：正文、安装命令、FAQ及真实 `a href` 链接直接写入HTML，CSS负责响应式排版；少量渐进JS只增强复制按钮，不生成正文、路由或SEO标签。不需要后端、框架、构建依赖、账户、表单、数据JSON或OpenAI Sites项目。正文直接在响应HTML有利于读取与发现链接，依据[Google的JS抓取说明](https://developers.google.com/search/docs/crawling-indexing/javascript/javascript-seo-basics)。

复制按钮由JS启用，键盘可操作；Clipboard成功显示“已复制”，拒绝/不可用显示“请选中命令手动复制”，状态用可访问文本提示。禁JS仍能完整阅读、点击和手动复制，不能显示虚假的复制成功。

预期项目地址为 `https://wangzhongren.github.io/ans-skill/`。中文HTML设 `lang="zh-CN"`、具体title/description和唯一canonical到该绝对地址；资源使用带 `/ans-skill/` 的正确URL，不能误指域名根 `/style.css`。无客户端路由、自动语言跳转或误设noindex。

`site/sitemap.xml` 以UTF-8列实际公开HTML的绝对canonical URL，中文必需范围只列首页，页脚有真实sitemap链接；不把README外链当本站页面。此位置覆盖项目子路径，依据[Google sitemap规则](https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap)。不伪造lastmod或依赖提交动作使页面可读。

robots.txt必须位于域名根，`/ans-skill/robots.txt`不能控制该站点爬虫；本次不新增它或改用户根站，依据[Google robots位置规则](https://developers.google.com/crawling/docs/robots-txt/create-robots-txt)。Search Console首次验证/提交需要后续账户授权与操作，不在此次站点部署中冒称已完成；收录、抓取时间、排名和摘要展示均不作完成保证。

- [x] **OPT-EN：完整英文页**（默认推荐，**待客户明确确认**）。额外路径仅 `site/en/index.html`，完整翻译同一内容与安装/FAQ，复用原CSS/JS；中文/英文有可见互链，各自canonical为 `/ans-skill/`、`/ans-skill/en/`，lang为zh-CN/en，两页互相且含自身的hreflang为zh-CN/en，sitemap列两URL。收益是英语读者可直接阅读；成本是整页翻译以及以后双语同步核对。未选时不生成英文页、英文占位链接或hreflang；无其他选装。

## 3. 唯一所有者与有限实施文件

推荐**复用现有技能规范 / skill-spec**为静态站点和Pages声明的唯一维护者：它已负责README、安装口径和对外规则；这是一份说明入口，没有运行时业务依赖。另建站点角色会增加定义、交接与双份内容维护，当前收益不足；未来若扩成业务应用再评估。此次不硬造五层源目录、Service/Provider或无意义程序API。

下表是未来拟授予的精确范围，**当前不生效**。客户授权后，团队组建同步调整 `角色卡/技能规范/role-card.md` 的职责/执行说明，以及 `boundary.md`、`boundary.yaml`、`changelog.md`：明确该角色维护静态HTML、CSS、复制JS及Pages发布声明，不能只加路径却保留“仅文档、不能实现页面”的歧义。不新建角色，owner不会因本设计自行获得代码写权；既有工具/规范行为和已批准workflow资料保持原边界。

| 唯一实施owner：skill-spec | 用途 |
| --- | --- |
| `site/index.html` | 完整中文正文、安装命令、元数据与来源链接 |
| `site/style.css` | 桌面/手机、可见焦点、流程图及命令区样式 |
| `site/main.js` | 仅复制增强及明确成功/失败反馈 |
| `site/sitemap.xml` | 本次实际语言页的绝对公开URL |
| `.github/workflows/pages.yml` | 唯一Pages发布声明，只上传site |
| `README.md` | 仅增加一条经线上核对的真实站点链接，保留GitLab安装地址及其余内容 |
| `角色卡/技能规范/docs/feature/public-landing-page.md` | 实施后当前页面/复制/部署流程与本设计历史链接 |
| `角色卡/技能规范/feature-map.md` | 在已有导航中链接该当前功能说明 |
| 仅OPT-EN确认后：`site/en/index.html` | 完整英文页面，其他共用文件按同一选项同步 |

独立测试角色检查真实界面、路径和部署产物，独立验收据本次客户确认范围判断；本文件列拟标准，不代写他们的通过结论，也不新增签审/标准文档。统筹安排，可信根在发布授权后处理GitHub账户/提交推送和部署；静态文件owner不能用维护权限代替账户授权。

公开仓库About的homepage设为 `https://wangzhongren.github.io/ans-skill/` 也是本次必需发布范围，由可信根通过GitHub账户API只修改homepage字段；README文字归skill-spec，不修改About的description/topics或新增账户功能。基本站点代码仍为五文件，OPT-EN仅加一HTML。

## 4. GitHub Pages 发布过程

基线：源HEAD `37b0bff`、公开版本 `a500334`。统筹已只读核实GitHub CLI认证有效、公开仓库 `wangzhongren/ans-skill` 当前账号admin=true，main存在、has_pages=false且Pages GET为404；尚无站点/Pages workflow。此为已核事实引用，不把旧“未认证需手工”当阻点，也不现在索取token或改设置。

拟议顺序：客户确认LP-D1及OPT-EN选择并授权实施/发布 → 治理落实精确owner范围 → owner实现、独立本地检查 → 可信根先通过API启用Pages且source选 **GitHub Actions** → 按既有双仓库方式同步本次已审查相关差额到源GitLab和GitHub main，站点/workflow变更触发首次部署 → 独立线上核对 → 双仓库发布README站点链接并在GitHub设置About homepage，核对两个入口。先启用Pages再推送，不假定未启用时configure-pages也会成功；失败保留日志并按已授权范围修复，用main的workflow_dispatch重试。

**仓库发布与站点artifact范围不同。** 推荐且纳入本次批准范围的是双仓库同步本次相关delta：第3节站点/workflow、README单条入口、技能规范功能说明/导航；`角色卡/技能规范/role-card.md`、`boundary.md`、`boundary.yaml`、`changelog.md` 的本次ownership定义；本轮P1与LP-D1两文档；以及授予LP-D1路径的 `角色卡/项目管理/boundary.md`、`boundary.yaml`、`changelog.md` 必要差额。完整路径按各角色根展开，仅同步本次相关变更，不整段推送源Git历史或夹带无关治理/工具差额，使公开实现仍有ownership与可读设计链接。Pages仅由GitHub提供；GitLab同步源码/文档，不另启站点或本地安装。

`.github/workflows/pages.yml` 仅在main的 `site/**` 或自身文件变化时push触发，另允许workflow_dispatch但只在main部署；无站点构建步骤。使用 `checkout@v6 → configure-pages@v5 → upload-pages-artifact@v4(path: site) → deploy-pages@v4`，单个deploy job、`github-pages` environment，记录实际page_url；权限为 `contents: read`、`pages: write`、`id-token: write`。配置依据[GitHub官方workflow](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)及[站点建立步骤](https://docs.github.com/en/pages/getting-started-with-github-pages/creating-a-github-pages-site)。

**Pages artifact只能是site目录**，与上述仓库提交范围无关；不得把角色定义、设计文档、任务、runtime、密钥、Git数据或整个仓库上传为站点。workflow使用GitHub提供的短期身份，不新建PAT/Secrets。部署失败保留失败日志、显示未发布成功，修复本次范围后重跑；不以本地预览替代线上可用。

## 5. 拟完成标准与验证方式（均待执行）

| 检查 | 可判定的完成条件 |
| --- | --- |
| 内容/来源 | P1六段完整；示意与真实交付区分，角色/五层准确，236含69/40、库存另60，无虚构承诺；源码/README/论文/MIT均到真实公开目标。 |
| 桌面/手机 | 至少1440×900与390×844实际浏览器查看；阅读顺序清楚，导航/流程/代码块可用，无遮挡或页面横向溢出；命令区必要滚动不挤坏正文。 |
| 键盘/复制 | Tab焦点可见、按钮可用Enter/Space；Codex和Claude分别复制完整命令且目标正确；受控拒绝Clipboard能提示失败并手动复制，无虚假成功。 |
| 禁JS/子路径 | 禁JS后原响应HTML仍有全部正文、命令、链接；本地预览按 `/ans-skill/` 挂载，CSS/JS/安装/语言链接正常，不能只测域名根。 |
| 元数据/语言 | title、description、lang、唯一canonical正确；sitemap解析成功且URL与部署一致；若选EN，英文完整且两页互链/hreflang/sitemap一致；未选无英文占位。 |
| 发布/隔离 | Pages后台Actions、实际run成功、公开 `/ans-skill/` 首页/CSS/JS/sitemap和选定语言页线上200且正文正确，README/About入口均到同一地址；检查artifact清单只有site，保留当前commit、URL、日志与检查证据。 |

独立测试按功能风险核对可访问HTML正文、真实项目URL/子路径、复制/键盘与手机，并报告实际界面和HTTP结果；不写逐字镜像正文的测试。独立验收再判断；本次静态页与入口变动不重复236项业务回归，若确实影响业务文件才按影响追加。Search Console提交、Google收录/排名、访问量不是通过条件。

## 6. 实质评审与一次审批简报

PM本人完成此方案与评审，没有虚构另一个PM或执行owner已经签收。对照DOC-01/TASK-01/ROLE-01，页面不参与任务状态或应用调用，无现有程序接口/数据消费者须迁移；跨角色影响仅是技能规范新增有限静态维护责任、治理落实、独立测试/验收和可信根发布，不影响旧workflow与库存代码。无需召开额外技术评审会议。

**建议批准。** 比README直接当首页更适合连贯介绍与独立搜索元数据；比框架/静态生成器更少依赖，源码本身就是抓取正文；比新建站点团队更贴近现有文档责任。成本是维护HTML及少量CSS/JS、一个workflow和真实跨视口/线上检查；风险是内容与README漂移、项目子路径错误、Pages/Actions失败及搜索收录不可控，以上通过唯一owner、精确路径和验证条件控制。没有架构方案上的实质未决；待客户决定实施/发布和唯一OPT-EN选择，执行范围需随后治理落地。

1. **做什么：** 按P1和LP-D1建设一个主中文ANS介绍长页，正文直接可读，能复制Codex/Claude安装命令，并发布到 `https://wangzhongren.github.io/ans-skill/`。
2. **为什么这样做：** 只用静态HTML/CSS和复制增强JS，复用技能规范owner；维护简单、抓取不依赖脚本，做完还须独立检查手机/桌面和真实项目地址。
3. **唯一选项：** OPT-EN默认推荐、待明确确认；增加一份完整英文页及以后双语同步成本。不选则只做中文，没有其他选装。
4. **确切批准范围：** 请求确认 **P1 + LP-D1**、选择是否含OPT-EN，并授权第3节实施及第4节明确的本次ownership、功能文档/导航、两份方案、必要PM授权定义和README单条入口差额，沿既有方式同步到源GitLab与 `wangzhongren/ans-skill` main；由可信根启用Actions Pages、首次部署及设置About homepage。先启用再推送，线上通过后发布入口；Pages artifact仅site，按第5节独立检查。基本站点代码仍五文件，OPT-EN只加一HTML；不含无关源码/旧workflow差额、整段Git历史、全库同步、本地安装、自定义域名、统计/站内账号或Search Console账户操作。本轮目前只完成方案。
