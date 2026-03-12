# 小红书自动回复 SaaS 平台

<p align="center">
  <img src="https://img.shields.io/badge/React-18.2-blue" alt="React">
  <img src="https://img.shields.io/badge/TypeScript-5.0-blue" alt="TypeScript">
  <img src="https://img.shields.io/badge/FastAPI-0.104-green" alt="FastAPI">
  <img src="https://img.shields.io/badge/License-MIT-yellow" alt="License">
</p>

> 小红书自动回复 SaaS 平台 - 自动化运营工具

## 📚 目录

- [功能特性](#功能特性)
- [技术架构](#技术架构)
- [快速开始](#快速开始)
- [本地开发](#本地开发)
- [Docker 部署](#docker-部署)
- [生产环境部署](#生产环境部署)
- [API 文档](#api-文档)
- [常见问题](#常见问题)

---

## ✨ 功能特性

| 功能 | 说明 |
|------|------|
| 📱 多账号管理 | 同时管理多个小红书账号 |
| 🔄 自动回复 | 关键词匹配/AI智能/随机回复 |
| 📊 数据统计 | 回复数据可视化分析 |
| 👥 会员订阅 | 免费/专业/企业多套餐 |
| ⚙️ 系统设置 | 个性化配置 |

---

## 🏗 技术架构

### 前端
- **框架**: React 18 + TypeScript
- **构建**: Vite
- **状态**: Pinia
- **UI**: Ant Design
- **图表**: ECharts

### 后端
- **框架**: FastAPI
- **数据库**: SQLite (开发) / PostgreSQL (生产)
- **认证**: JWT
- **部署**: Docker Compose

---

## 🚀 快速开始

### 前置要求

| 软件 | 版本要求 |
|------|----------|
| Node.js | ≥ 18.0 |
| Python | ≥ 3.10 |
| Git | - |

### 1. 克隆项目

```bash
git clone https://github.com/LAOBAIv/xiaohongshu-saas.git
cd xiaohongshu-saas
```

### 2. 启动后端

```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或: venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 启动服务
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. 启动前端

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

### 4. 访问系统

- 前端: http://localhost:3000
- 后端: http://localhost:8000
- API 文档: http://localhost:8000/docs

---

## 🐳 Docker 部署

### 使用 Docker Compose

```bash
# 克隆项目
git clone https://github.com/LAOBAIv/xiaohongshu-saas.git
cd xiaohongshu-saas

# 启动所有服务
docker-compose up -d
```

### 手动 Docker 构建

```bash
# 构建后端镜像
docker build -t xhs-saas-backend ./backend

# 构建前端镜像
docker build -t xhs-saas-frontend ./frontend

# 运行容器
docker run -d -p 8000:8000 xhs-saas-backend
docker run -d -p 3000:3000 xhs-saas-frontend
```

---

## ☁️ 生产环境部署

### 1. 服务器要求

| 配置 | 最低 | 推荐 |
|------|------|------|
| CPU | 2 核 | 4 核 |
| 内存 | 4 GB | 8 GB |
| 磁盘 | 20 GB | 50 GB |
| 系统 | Ubuntu 20.04+ | Ubuntu 22.04+ |

### 2. 环境变量配置

创建 `.env` 文件：

```bash
# .env
ENV=production
SECRET_KEY=生成强随机密钥
DATABASE_URL=postgresql://user:password@localhost:5432/xhs_saas
ALLOWED_ORIGINS=https://your-domain.com
```

生成密钥：
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

### 3. PostgreSQL 安装

```bash
# 安装 PostgreSQL
sudo apt update
sudo apt install postgresql postgresql-contrib

# 创建数据库
sudo -u postgres createuser xhs_user
sudo -u postgres createdb xhs_saas
sudo -u postgres psql -c "ALTER USER xhs_user WITH PASSWORD 'your_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE xhs_saas TO xhs_user;"
```

### 4. Nginx 配置

```nginx
# /etc/nginx/sites-available/xhs-saas
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /path/to/fullchain.pem;
    ssl_certificate_key /path/to/privkey.pem;

    # 前端静态文件
    location / {
        root /var/www/xhs-saas/dist;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    # 后端 API 代理
    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

### 5. Systemd 服务

```ini
# /etc/systemd/system/xhs-saas.service
[Unit]
Description=XHS SaaS Backend
After=network.target postgresql.service

[Service]
User=www-data
Group=www-data
WorkingDirectory=/opt/xhs-saas/backend
Environment="PATH=/opt/xhs-saas/backend/venv/bin"
Environment="ENV=production"
ExecStart=/opt/xhs-saas/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always

[Install]
WantedBy=multi-user.target
```

### 6. 启动服务

```bash
# 重载 systemd
sudo systemctl daemon-reload

# 启动服务
sudo systemctl start xhs-saas
sudo systemctl enable xhs-saas

# 检查状态
sudo systemctl status xhs-saas
```

---

## 📖 API 文档

启动后端后访问: http://localhost:8000/docs

### 主要接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/v1/auth/register` | POST | 用户注册 |
| `/api/v1/auth/login` | POST | 用户登录 |
| `/api/v1/user/profile` | GET | 获取用户资料 |
| `/api/v1/accounts` | GET/POST | 账号列表/添加 |
| `/api/v1/accounts/{id}/rules` | GET/POST | 规则列表/创建 |
| `/api/v1/accounts/stats/overview` | GET | 数据统计 |

---

## 🔧 常见问题

### Q: 前端无法连接后端

检查 `frontend/src/api/index.ts` 中的 `API_BASE_URL` 是否正确。

### Q: 数据库连接失败

确认 `.env` 中的 `DATABASE_URL` 格式正确。

### Q: Token 过期

登录后会返回 access_token 和 refresh_token，refresh_token 用于刷新 access_token。

### Q: 如何修改套餐配置

编辑 `backend/app/core/config.py` 中的 `SUBSCRIPTION_PLANS`。

---

## 📄 License

MIT License - 见 LICENSE 文件

---

## 👤 开发者

- GitHub: [@LAOBAIv](https://github.com/LAOBAIv)