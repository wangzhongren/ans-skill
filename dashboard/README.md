# ANS Dashboard（独立后端）

Dashboard 可以部署一份服务，供多个项目共用。服务端保存用户、供同一项目角色共用的 Key、**展示快照**与协作记录；不需要上传业务仓库、角色文档全文或项目 SQLite 文件。每个项目通过 `/p/<project-id>/` 访问；所有启用的用户登录后默认可查看全部项目。本地同步器通过该项目的 Key 上传角色摘要、职责、边界路径、项目理解和任务状态。

仅部署云端时，复制整个 `dashboard/` 目录到服务器即可。它只使用 Python 3.10+ 标准库。可用下面的 Docker Compose 部署，也可直接运行 Python。项目业务语言不受 Python 限制。

## Docker Compose 部署

服务器需安装 Docker Engine 和 Compose，并准备一个对外的 HTTPS 反向代理。在服务器的 `dashboard/` 目录执行：

```sh
cp .env.example .env
# 编辑 .env：ANS_DASHBOARD_HOST 填真实域名；默认示例路径是 /ans-dashboard
docker compose build
docker compose run --rm --no-deps dashboard python -m dashboard.admin --state-dir /data --username admin
docker compose up -d
docker compose ps
```

管理员初始化命令会交互读取密码，至少 15 个字符；只执行一次。Compose 项目名固定为 `ans-dashboard`，元数据库和各项目数据库都保存在 `dashboard-state` 命名卷中，容器以非 root 身份运行。宿主机只发布 `127.0.0.1:${ANS_DASHBOARD_PORT:-8765}`；用下方 Nginx 示例将 HTTPS 域名转发到这个端口，修改端口时同步修改代理配置。不要将容器端口直接发布到公网，也不要用 `docker compose down -v` 删除状态卷。升级时在新代码目录运行 `docker compose up -d --build`，保留同一个 Compose 项目名和状态卷。查看日志用 `docker compose logs -f dashboard`。

Docker 镜像只包含 Dashboard 的 Python/HTML/CSS/JS；业务项目文件仍在各自本地，通过下方同步命令发送展示快照。容器内服务监听 `0.0.0.0`，这是为了接收 Docker 端口映射；宿主机映射依然只监听回环地址。首次启动前必须创建管理员，否则服务会拒绝启动。

### 自动跟随 GitLab 的 `main`

服务器可以每约五分钟检查 GitLab，有可快进的新提交时自动重建 Dashboard，并等待容器健康。这只更新 **ans-skill 的 Dashboard 程序**，不会从业务项目仓库采集数据；业务项目仍使用下文的本地快照同步器。当前若是**手工复制**的目录，先一次性切换成 Git 克隆；自动更新器不会对普通复制目录执行 `git pull`：

1. 在 GitLab 的 `ans-skill` 项目设置中添加服务器的**只读 Deploy Key**，确认服务器可以无交互访问仓库。[GitLab Deploy Key 说明](https://docs.gitlab.com/user/project/deploy_keys/)。若服务器还没有专用密钥，可先运行 `install -d -m 700 /root/.ssh` 和 `ssh-keygen -t ed25519 -f /root/.ssh/ans-skill-deploy -N ''`，把 `/root/.ssh/ans-skill-deploy.pub` 的内容添加到 GitLab；私钥留在服务器，不要发给他人。首次连接应核对 GitLab 的 SSH 主机指纹，不要关闭主机校验。
2. 在服务器克隆一个新目录，复制旧目录中现有的 `.env`：

   ```sh
   GIT_SSH_COMMAND='ssh -i /root/.ssh/ans-skill-deploy -o IdentitiesOnly=yes' git clone git@gitlab.chinatinghai.com:ai-bigdata/wzr/ans-skill.git /opt/ans-skill-git
   git -C /opt/ans-skill-git config core.sshCommand 'ssh -i /root/.ssh/ans-skill-deploy -o IdentitiesOnly=yes -o BatchMode=yes'
   cp -p /原先手工复制的/dashboard/.env /opt/ans-skill-git/dashboard/.env
   cd /opt/ans-skill-git/dashboard
   docker compose up -d --build --wait --wait-timeout 120
   ```

   Compose 项目名固定为 `ans-dashboard`，因此会沿用原有数据库卷；不要重新创建管理员，也不要运行 `docker compose down -v`。确认页面正常后再处理旧目录。
3. 从新克隆的目录安装定时器：

   ```sh
   cd /opt/ans-skill-git
   bash dashboard/install_auto_update.sh
   systemctl start ans-dashboard-auto-update.service
   systemctl list-timers ans-dashboard-auto-update.timer
   journalctl -u ans-dashboard-auto-update.service -n 50 --no-pager
   ```

定时器只接受 `main` 的快进提交、拒绝有本地改动的仓库。新容器健康检查失败时，会尝试恢复旧代码和镜像，并在 systemd 日志中报告失败。**数据库内容不随代码自动回滚**；启用自动更新前先备份完整状态卷，涉及数据库结构变更时应额外检查备份和迁移。更新脚本本身如有改动，重新运行 `install_auto_update.sh` 才会更新 systemd 中的安装副本。若 GitLab 的 `main` 不是受控发布分支，应先限制可合入人员和完成测试，再启用自动部署。Docker Compose 重建容器时保留命名卷。[Compose 更新行为](https://docs.docker.com/reference/cli/docker/compose/up/)。

### 挂到现有域名的 `/ans-dashboard/`

若访问地址希望是 `https://dashboard.example.com/ans-dashboard/`，在 `dashboard/.env` 设置 `ANS_DASHBOARD_BASE_PATH=/ans-dashboard` 后重建容器。直接运行 Python 时加 `--base-path /ans-dashboard`。也支持其他前缀和多段路径；留空则部署在域名根路径。反向代理应保留 `/ans-dashboard`，不要剥掉它：

```nginx
location = /ans-dashboard { return 308 /ans-dashboard/; }
location /ans-dashboard/ {
    proxy_set_header Host $host;
    proxy_pass http://127.0.0.1:8765;
}
```

这里的 `proxy_pass` **没有尾部 `/`**，会把 `/ans-dashboard/...` 原样转给后端；写成 `proxy_pass http://127.0.0.1:8765/;` 会改写请求路径。完整配置仍需放在下方示例的 HTTPS `server` 块内。管理页为 `/ans-dashboard/manage`，项目页为 `/ans-dashboard/p/<project-id>/`。本地同步命令的 `--server-url` 也填 `https://dashboard.example.com/ans-dashboard`，同步器会向该前缀下的项目 API 发送快照。

## 直接运行 Python

从 `dashboard/` 的**父目录**执行，或将该父目录加入 `PYTHONPATH`：

### 首次配置

```sh
python3 -m dashboard.admin --state-dir /srv/ans-dashboard/state --username admin
python3 -m dashboard.server --cloud-state /srv/ans-dashboard/state --port 8765 --trusted-host dashboard.example.com
```

第一条命令交互输入管理员密码，至少 15 个字符。只可用它创建第一个管理员；以后在网页 `/manage` 添加用户、项目和项目 Key。Key **仅创建时显示一次**，请交给对应项目的角色及同步端。所有启用的用户可查看全部项目；Key 只对所属项目有效，可同步快照、读取该项目数据、以声明的角色 ID 发消息和申请，但不能审批。

直接运行时服务默认监听 `127.0.0.1`。线上用 HTTPS 反向代理把域名转发到该端口，并把原始 `Host` 传给服务。`--trusted-host` 写公开域名（如使用非默认端口则包含端口）；生产会话 Cookie 设置 `Secure`，所以网页必须经 HTTPS 访问。确保状态目录只允许服务账号读写，并备份整个状态目录（元数据库与 `projects/`）。建议用服务器的进程管理器托管上述命令。不要将本地预览参数 `--insecure-local-preview` 用在线上。

一个部署在域名根路径的 Nginx 入口示例（使用 `/ans-dashboard/` 时采用上方的 `location`）：

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

## 管理项目与用户

登录 `https://dashboard.example.com/manage`，先添加项目，再从“所属项目”列表选择它并创建 Key；不存在的项目 ID 不能直接创建 Key。所有启用的用户默认查看全部项目；管理员额外可以管理和审批。管理页可停用用户、撤销 Key。停用用户会使其现有会话失效；撤销 Key 后需重新创建并更新同步端与角色。

## 在项目本地同步

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

在 `read` 提示时粘贴项目 Key 并回车。也可以由本地机密管理器将 `ANS_DASHBOARD_KEY` 注入进程；不要把 Key 写进仓库、命令行参数或 URL。省略 `--interval` 即只同步一次。该同步器读取 `角色卡/` 或 `role-cards/`、共享 `project-context/context.sqlite3` 及 `docs/scheduling/` 或 `doc/scheduling/`，整理后发送到 `/p/orders/api/sync`；若 `--server-url` 带 `/ans-dashboard`，则发送到 `/ans-dashboard/p/orders/api/sync`。目录不标准时加 `--roles`、`--scheduling`（必须位于项目根目录内）。同步内容上限 4 MiB；不会递归上传业务源码或角色文档全文。同步请求不跟随重定向，避免项目 Key 被转发。

默认本地单项目模式仍可使用：

```sh
python3 -m dashboard.server --root /path/to/business-project --port 0
```

或者调用兼容入口 `scripts/serve_dashboard.py`。本地模式只监听回环地址，直接读本机记录，不需要账号或 Key。

## 数据库存储

1. **业务项目本地**：每个项目各有自己的 `project-context/context.sqlite3`，按 `role_id` 保存角色理解。同步器只读取它并生成展示 JSON；原数据库文件不会上传。
2. **共享服务器**：每个项目的展示快照、角色消息、权限申请、决定和审计记录存于 `<cloud-state>/projects/<project-id>.sqlite3`。共享的 `<cloud-state>/dashboard.sqlite3` 保存用户、会话、项目登记、项目 Key 的哈希及最近同步时间，不保存新写入的项目快照。Docker 中 `<cloud-state>` 是 `/data`，这些文件都在同一个持久卷里。
3. **隔离与备份**：项目展示数据是物理分库，查看与同步权限仍由共享元数据库校验。备份时应停止服务并备份整个状态目录或卷，包含 `dashboard.sqlite3` 和 `projects/`；只备份一个项目文件不能恢复该项目的账号和授权。

### 从旧版共享库升级

先停止旧服务并备份完整状态目录或 Docker 状态卷。用新代码启动时，服务会把旧 `dashboard.sqlite3` 中的项目快照迁移到 `projects/<project-id>.sqlite3`，然后清空旧的快照字段；用户、授权与 Key 保留。迁移失败会停止启动，尚未迁移的旧记录不会清空；修复原因后可重新启动继续迁移。确认各项目页面和授权正常后，再恢复同步器。

## 数据边界

云端快照包括角色名称、职责摘要、边界路径、项目理解的流程/数据/接口/定义条目，以及任务状态、计划操作、写入范围、批次、反馈与协作事件。条目中的说明、字段和自定义引用会按原值同步，因为页面要展示这些内容；请在本地项目理解里只记录适合授权用户查看的信息。同步器不递归读取角色文档正文或完整仓库文件，并会剔除自动采集的项目根目录 URI。展示视图是观察页；协作收件箱可写入消息和决定，但 Dashboard 不负责派发角色、修改业务代码或自动验收。

## Role channel

共享云端 Dashboard 的“协作收件箱”提供角色消息、权限申请、管理员决定和审计记录；本地单项目只读模式不启用此功能。先让本地同步器上传真实角色与任务快照，再由管理员在 `/manage` 为项目创建 Key。各角色自己用**同一个项目 Key** 发送消息和申请，并在请求里声明自己的角色 ID；项目 Key 可读取该项目的全部收件箱，但不能审批。网页管理员可给角色发消息、查看完整申请并记录批准或拒绝。所有启用的用户可查看全部项目的收件箱。

角色在项目本地使用与快照同步相同的 `ANS_DASHBOARD_KEY`，不能把 Key 写入仓库或命令行参数。每个角色用自己的 `--role` 参数声明身份：

```sh
read -r -s ANS_DASHBOARD_KEY
export ANS_DASHBOARD_KEY
python3 -m dashboard.channel_cli --server-url https://dashboard.example.com/ans-dashboard --project-id orders --role orders list
python3 -m dashboard.channel_cli --server-url https://dashboard.example.com/ans-dashboard --project-id orders --role orders send --input message.json
python3 -m dashboard.channel_cli --server-url https://dashboard.example.com/ans-dashboard --project-id orders --role orders request --input permission.json
```

`message.json` 示例：

```json
{"clientMessageId":"task-1-question-1","toRoleId":"reviewer","taskId":"task-1","kind":"question","body":"请确认接口字段。","revision":"D1"}
```

`permission.json` 示例（字段必须与当前已同步的任务、角色、计划及需求/设计/边界版本一致）：

```json
{"clientRequestId":"task-1-node-1-attempt-1","taskId":"task-1","nodeId":"node-1","workerId":"worker-1","operation":"implement","writeSet":["src/orders.py"],"planRevision":1,"attemptNumber":1,"requirementRevision":"R1","designRevision":"D1","boundaryRevision":"B1","reason":"需要写入订单导出实现文件。"}
```

相同 `clientMessageId` 或 `clientRequestId` 重试只返回原记录；同 ID 的不同内容会被拒绝。申请提交和批准时均检查当前快照版本，旧设计/边界版本不能批准。管理员批准记录一小时有效，拒绝和过期状态保留在审计中。**Dashboard 的批准只是一条协作决定，不是源码写入、角色激活或任务验收授权。**执行前仍需按 [task_ops 协议](../references/task-operations.md) 由可信宿主核对客户同意文件及其已审核哈希，或匹配已审核的项目预授权配置；不能由 AI 自行把 Dashboard 决定转换成批准哈希。

共用项目 Key 表示服务器只能确认“来自这个项目”，不能单独证明请求中的角色 ID 是谁。角色应在自己的执行上下文里使用 `--role` 自行发送；对角色切换、任务范围和实际代码写入的严格检查仍由本地角色/任务门禁承担。

消息正文、申请理由、写入路径与版本会保存在服务器的项目数据库中，并对所有启用的网页用户及持有该项目 Key 的角色可见；不要把密码、访问令牌或不应共享的源码片段写进去。任务或角色版本变化后，未处理或已批准的旧申请在页面显示“版本失效”，需提交新申请。

服务端升级时保留同一状态卷，运行 `docker compose up -d --build`。新增协作表会在首次使用项目收件箱时创建；原项目快照和账号不需要重建。Dashboard 不启动代理进程；角色由本地 CLI 发送和查询，网页继续约每 2 秒刷新当前收件箱。

验证：`python3 -m unittest discover -s scripts/tests -v`。
