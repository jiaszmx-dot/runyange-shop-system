# 润阳阁小儿推拿艾灸馆 · 全国连锁云店铺系统

基于你提供的需求文档与参考风格图，已完成一套可运行的「总部 + 门店 + 会员端（小程序骨架）」云店铺系统，包含：

- 总部统一管理：门店、项目、耗材、提成规则、评价治理、推荐奖励审核。
- 门店运营闭环：预约、开单、抖音导单核销、库存自动扣减、员工提成、看板。
- 会员体系：会员档案、卡项、推荐奖励进度、消息通知。
- 结算与风控：跨店核销记录、每日自动结算任务、操作日志、数据备份任务。

## 1. 项目结构

```text
.
├─ backend/                  # FastAPI + SQLAlchemy
│  ├─ main.py                # API 入口
│  ├─ app/
│  │  ├─ models.py           # 全量业务模型
│  │  ├─ schemas.py          # 请求/响应模型
│  │  ├─ services.py         # 核心业务服务（核销/结算/提成/推荐）
│  │  ├─ security.py         # JWT + 密码 + 敏感字段加解密
│  │  └─ seed.py             # 初始化演示数据
│  └─ tests/
│     └─ test_core_flows.py  # 关键业务流自动化测试
├─ frontend/                 # Vue3 + Pinia + ECharts
│  ├─ src/
│  │  ├─ pages/              # 总览/会员/订单/库存/员工/评价/推荐页
│  │  └─ components/         # 布局与统计卡片
│  └─ public/logo.png        # 你提供的润阳阁 LOGO
├─ miniapp/                  # 微信小程序原生骨架（会员端）
├─ docker-compose.yml        # MySQL + Redis + Backend + Frontend 一键部署
└─ render.yaml               # Render 蓝图部署
```

## 2. 本地运行（开发模式）

### 2.1 启动后端

```bash
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

### 2.2 启动前端

```bash
cd frontend
npm install
npm run dev -- --host 127.0.0.1 --port 5173
```

打开 `http://127.0.0.1:5173` 即可访问。

默认演示账号：

- 总部：`hq_admin / Admin@123`
- 上海店长：`sh_admin / Admin@123`
- 上海员工：`sh_staff_01 / Admin@123`

## 3. Docker 一键部署（推荐）

```bash
docker compose up --build -d
```

访问地址：

- 前端：`http://localhost:8080`
- 后端：`http://localhost:8000`

包含：

- `mysql`：业务主库
- `redis`：缓存/消息预留
- `backend`：FastAPI 服务
- `frontend`：Nginx 托管前端并反向代理 `/api`

## 4. Render 部署（云端）

仓库推送后可直接使用 `render.yaml` 创建：

- `runyangge-api`（Python Web Service）
- `runyangge-web`（Static Site）

> 注：Render 蓝图默认采用 SQLite 挂载盘以便快速上线；如你要严格生产化的 MySQL/Redis，请使用 Docker 方案部署到云主机，或切换到支持 MySQL 的云平台。

## 5. 功能与测试结果

已完成自动化与人工可视化验收：

- 后端自动化：`python -m pytest -q` 通过（核心业务流：登录、开单、抖音导单核销、结算）。
- 前端构建：`npm run build` 通过。
- 浏览器肉眼验收：登录页、经营总览、会员档案、预约开单、耗材库存、员工绩效、评价中心、推荐奖励页面均已截图验证。

截图输出路径：

- `.playwright-cli/page-2026-03-20T04-20-13-399Z.png`
- `.playwright-cli/page-2026-03-20T04-21-35-552Z.png`
- `.playwright-cli/page-2026-03-20T04-22-19-755Z.png`
- `.playwright-cli/page-2026-03-20T04-23-13-021Z.png`
- `.playwright-cli/page-2026-03-20T04-23-54-506Z.png`
- `.playwright-cli/page-2026-03-20T04-24-30-485Z.png`
- `.playwright-cli/page-2026-03-20T04-25-03-105Z.png`

## 6. 已使用的 Skills

- `skill-installer`：联网安装所需技能。
- `figma`：用于设计系统规则与 Figma 设计链路接入准备。
- `playwright`：执行真实浏览器回归测试与截图验收。
- `render-deploy`：生成 Render 蓝图部署配置。

> `imagegen` 已安装；当前环境未设置 `OPENAI_API_KEY`，因此页面素材采用高质量本地 SVG 资源（已可直接使用）。
