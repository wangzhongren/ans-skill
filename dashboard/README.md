# ANS Dashboard（独立后端）

Dashboard 可以部署一份服务，供多个项目共用。服务端只保存用户、项目权限、项目 Key 和**展示快照**；不需要上传业务仓库、角色文档全文或项目 SQLite 文件。每个项目通过 `/p/<project-id>/` 访问，网页按登录用户权限筛选；本地同步器通过该项目的 Key 上传角色摘要、职责、边界路径、项目理解和任务状态。

仅部署云端时，复制整个 `dashboard/` 目录到服务器即可。它只使用 Python 3.10+ 标准库。运行命令需要从 `dashboard/` 的**父目录**执行，或者将该父目录加入 `PYTHONPATH`。项目业务语言不受 Python 限制。

## 1. 首次配置

```sh
python3 -m dashboard.admin --state-dir /srv/ans-dashboard/state --username admin
python3 -m dashboard.server --cloud-state /srv/ans-dashboard/state --port 8765 --trusted-host dashboard.example.com
```

第一条命令交互输入管理员密码，至少 15 个字符。只可用它创建第一个管理员；以后在网页 `/manage` 添加用户、项目和项目 Key。Key **仅创建时显示一次**，请交给对应项目的同步端。用户权限与 Key 分开：用户登录看获授权项目；Key 只允许同步和读取它所属项目的投影。

服务固定监听 `127.0.0.1`。线上用 HTTPS 反向代理把域名转发到该端口，并把原始 `Host` 传给服务。`--trusted-host` 写公开域名（如使用非默认端口则包含端口）；生产会话 Cookie 设置 `Secure`，所以网页必须经 HTTPS 访问。确保状态目录只允许服务账号读写，并备份其中的 `dashboard.sqlite3`。建议用服务器的进程管理器托管上述命令。不要将本地预览参数 `--insecure-local-preview` 用在线上。

一个 Nginx 入口示例：

```nginx
server {
    listen 443 ssl;
    server_name dashboard.example.com;
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    location / {
        proxy_set_header Host $host;
        proxy_pass http://127.0.0.1:8765;
    }
}
```

证书、域名和进程服务配置按实际环境替换；同时将 HTTP 重定向至 HTTPS。

## 2. 管理项目与用户

登录 `https://dashboard.example.com/manage`，依次添加项目 ID、用户，授权该用户访问项目，再为项目创建同步 Key。管理员可查看全部项目；普通用户只看获授权项目。管理页可停用用户、撤销 Key。停用用户会使其现有会话失效；撤销 Key 后需重新创建并更新同步端。

## 3. 在项目本地同步

同步端需要 `dashboard/` 代码和业务项目的本地读取权限；它不需要部署在云端服务器上。以下命令在技能目录执行：

```sh
read -r -s ANS_DASHBOARD_KEY
export ANS_DASHBOARD_KEY
python3 -m dashboard.sync \
  --root /path/to/business-project \
  --project-id orders \
  --server-url https://dashboard.example.com \
  --interval 10
```

在 `read` 提示时粘贴项目 Key 并回车。也可以由本地机密管理器将 `ANS_DASHBOARD_KEY` 注入进程；不要把 Key 写进仓库、命令行参数或 URL。省略 `--interval` 即只同步一次。该同步器读取 `角色卡/` 或 `role-cards/`、共享 `project-context/context.sqlite3` 及 `docs/scheduling/` 或 `doc/scheduling/`，整理后发送到 `/p/orders/api/sync`。目录不标准时加 `--roles`、`--scheduling`（必须位于项目根目录内）。同步内容上限 4 MiB；不会递归上传业务源码或角色文档全文。同步请求不跟随重定向，避免项目 Key 被转发。

默认本地单项目模式仍可使用：

```sh
python3 -m dashboard.server --root /path/to/business-project --port 0
```

或者调用兼容入口 `scripts/serve_dashboard.py`。本地模式只监听回环地址，直接读本机记录，不需要账号或 Key。

## 数据边界

云端快照包括角色名称、职责摘要、边界路径、项目理解的流程/数据/接口/定义条目，以及任务状态与协作事件。条目中的说明、字段和自定义引用会按原值同步，因为页面要展示这些内容；请在本地项目理解里只记录适合授权用户查看的信息。同步器不递归读取角色文档正文或完整仓库文件，并会剔除自动采集的项目根目录 URI。Dashboard 是观察页，不负责派发角色、修改业务代码或自动验收。

验证：`python3 -m unittest discover -s scripts/tests -v`。
