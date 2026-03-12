# 小红书 SaaS 生产环境部署检查清单

## 1. 环境变量配置

```bash
# .env 文件 (不要提交到 Git)
ENV=production
SECRET_KEY=生成强随机密钥: python3 -c "import secrets; print(secrets.token_hex(32))"
DATABASE_URL=postgresql://user:password@localhost:5432/xhs_saas
ALLOWED_ORIGINS=https://your-domain.com,https://www.your-domain.com

# Redis (用于限流和缓存)
REDIS_URL=redis://localhost:6379/0
```

## 2. 数据库 (PostgreSQL)

```bash
# 安装 PostgreSQL
apt install postgresql postgresql-contrib

# 创建数据库
sudo -u postgres createdb xhs_saas
sudo -u postgres createuser xhs_user
sudo -u postgres psql -c "ALTER USER xhs_user WITH PASSWORD 'your_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE xhs_saas TO xhs_user;"
```

## 3. Nginx 配置 (HTTPS)

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
    ssl_protocols TLSv1.2 TLSv1.3;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /path/to/frontend/dist;
    }
}
```

## 4. Systemd 服务

```ini
# /etc/systemd/system/xhs-saas.service
[Unit]
Description=XHS SaaS Backend
After=network.target postgresql.service

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/xiaohongshu-saas/backend
Environment="PATH=/path/to/venv/bin"
Environment="ENV=production"
ExecStart=/path/to/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always

[Install]
WantedBy=multi-user.target
```

## 5. 安全检查

- [ ] 修改默认 SECRET_KEY
- [ ] 限定 CORS 域名
- [ ] 关闭 DEBUG 模式
- [ ] 配置防火墙规则
- [ ] 启用 Fail2Ban 防暴力破解
- [ ] 配置日志轮转
- [ ] 定期备份数据库

## 6. 一键部署脚本

```bash
#!/bin/bash
# deploy.sh

# 环境检查
if [ "$ENV" != "production" ]; then
    echo "请设置 ENV=production"
    exit 1
fi

# 构建前端
cd frontend && npm run build

# 启动服务
systemctl restart xhs-saas
nginx -t && systemctl reload nginx
```

---

**部署前必做:**
1. ☐ 生成新的 SECRET_KEY
2. ☐ 配置数据库连接
3. ☐ 配置域名和 SSL 证书
4. ☐ 限定 CORS 白名单
5. ☐ 测试所有 API 接口