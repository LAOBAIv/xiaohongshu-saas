# 小红书自动回复 SaaS 平台

一个多租户的小红书自动化运营平台，支持多用户独立配置和管理。

## 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                        用户端                                │
├──────────┬──────────┬──────────┬──────────┬────────────────┤
│  Web端   │  移动端  │  小程序  │   API    │   Chrome插件   │
└────┬─────┴────┬─────┴────┬─────┴────┬─────┴───────┬────────┘
     │          │          │          │             │
     └──────────┴──────────┴──────────┴─────────────┘
                          │
                 ┌────────▼────────┐
                 │   API 网关      │
                 │   (Nginx)       │
                 └────────┬────────┘
                          │
     ┌────────────────────┼────────────────────┐
     │                    │                    │
┌────▼────┐        ┌─────▼─────┐       ┌──────▼──────┐
│ 用户服务 │        │ 机器人服务 │       │  支付服务   │
│         │        │           │       │             │
└────┬────┘        └─────┬─────┘       └──────┬──────┘
     │                   │                    │
     │        ┌──────────┼──────────┐         │
     │        │          │          │         │
     │   ┌────▼───┐ ┌────▼───┐ ┌────▼───┐    │
     │   │Worker1 │ │Worker2 │ │Worker3 │ ... │
     │   └────────┘ └────────┘ └────────┘    │
     │                                        │
     └────────────────┬───────────────────────┘
                      │
              ┌───────▼───────┐
              │   数据库      │
              │  PostgreSQL   │
              └───────────────┘
```

## 核心功能

### 👤 用户管理
- [x] 用户注册/登录（邮箱、手机号）
- [x] 第三方登录（微信、Google、GitHub）
- [x] 会员等级体系（免费/专业/企业）
- [x] 用户个人中心

### 🔧 配置管理
- [x] 多账号管理（小红书账号）
- [x] Cookie 自动刷新
- [x] 回复规则配置
- [x] 关键词库管理
- [x] 敏感词过滤

### 🤖 自动化功能
- [x] 自动监控评论
- [x] 自动监控私信
- [x] 智能关键词匹配回复
- [x] AI 语义理解回复（可选）
- [x] 定时任务调度

### 📊 数据统计
- [x] 回复数据统计
- [x] 趋势图表
- [x] 导出报表
- [x] 实时日志

### 💰 订阅支付
- [x] 多种套餐选择
- [x] 微信/支付宝支付
- [x] 会员到期提醒
- [x] 套餐升降级

### 🔌 扩展功能
- [x] Webhook 通知
- [x] API 接口
- [x] Chrome 浏览器插件
- [x] 企业微信集成

## 技术栈

### 后端
- **语言**: Python 3.12+
- **框架**: FastAPI
- **数据库**: PostgreSQL + Redis
- **任务队列**: Celery + RabbitMQ
- **ORM**: SQLAlchemy 2.0

### 前端
- **框架**: React 18 + TypeScript
- **UI**: Ant Design 5.0
- **状态管理**: Zustand
- **图表**: ECharts

### 部署
- **容器**: Docker + Docker Compose
- **反向代理**: Nginx
- **HTTPS**: Let's Encrypt

## 快速开始

### 开发环境

```bash
# 克隆项目
git clone https://github.com/your-repo/xiaohongshu-saas.git
cd xiaohongshu-saas

# 启动开发环境
docker-compose -f docker-compose.dev.yml up -d

# 访问服务
# 前端: http://localhost:3000
# 后端: http://localhost:8000
# API文档: http://localhost:8000/docs
```

### 生产环境

```bash
# 配置环境变量
cp .env.example .env
# 编辑 .env 文件

# 启动服务
docker-compose -f docker-compose.prod.yml up -d

# 配置 Nginx
cp nginx/nginx.conf.example nginx/nginx.conf
```

## 项目结构

```
├── backend/                    # 后端服务
│   ├── app/
│   │   ├── api/               # API 路由
│   │   │   ├── v1/
│   │   │   │   ├── auth.py    # 认证接口
│   │   │   │   ├── user.py    # 用户接口
│   │   │   │   ├── account.py # 账号接口
│   │   │   │   ├── rule.py    # 规则接口
│   │   │   │   └── stats.py   # 统计接口
│   │   │   └── deps.py        # 依赖注入
│   │   ├── core/              # 核心配置
│   │   │   ├── config.py      # 配置管理
│   │   │   ├── security.py    # 安全相关
│   │   │   └── database.py    # 数据库
│   │   ├── models/            # 数据模型
│   │   │   ├── user.py        # 用户模型
│   │   │   ├── account.py     # 账号模型
│   │   │   └── rule.py        # 规则模型
│   │   ├── schemas/           # Pydantic 模型
│   │   ├── services/          # 业务逻辑
│   │   │   ├── auth.py        # 认证服务
│   │   │   ├── account.py     # 账号服务
│   │   │   ├── crawler.py     # 爬虫服务
│   │   │   └── reply.py       # 回复服务
│   │   ├── tasks/             # 异步任务
│   │   └── utils/             # 工具函数
│   ├── alembic/               # 数据库迁移
│   ├── tests/                 # 测试
│   └── main.py                # 入口文件
│
├── frontend/                   # 前端应用
│   ├── src/
│   │   ├── api/              # API 调用
│   │   ├── components/       # 公共组件
│   │   ├── pages/            # 页面组件
│   │   ├── hooks/            # 自定义 Hooks
│   │   ├── stores/           # 状态管理
│   │   ├── styles/           # 样式文件
│   │   ├── types/            # TypeScript 类型
│   │   ├── utils/            # 工具函数
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── public/
│   ├── index.html
│   ├── package.json
│   └── vite.config.ts
│
├── worker/                     # 异步任务 worker
│   ├── crawler/               # 爬虫任务
│   │   ├── xhs_client.py      # 小红书客户端
│   │   └── comment_monitor.py # 评论监控
│   ├── reply/                 # 回复任务
│   │   └── reply_engine.py    # 回复引擎
│   └── main.py
│
├── nginx/                      # Nginx 配置
├── docker/                     # Docker 配置
├── scripts/                    # 运维脚本
├── docs/                       # 文档
└── README.md
```

## API 接口

### 认证接口
| 方法 | 路径 | 描述 |
|------|------|------|
| POST | /api/v1/auth/register | 用户注册 |
| POST | /api/v1/auth/login | 用户登录 |
| POST | /api/v1/auth/logout | 退出登录 |
| POST | /api/v1/auth/refresh | 刷新 Token |
| POST | /api/v1/auth/forgot-password | 忘记密码 |

### 用户接口
| 方法 | 路径 | 描述 |
|------|------|------|
| GET | /api/v1/user/profile | 获取用户信息 |
| PUT | /api/v1/user/profile | 更新用户信息 |
| GET | /api/v1/user/subscription | 获取订阅信息 |

### 账号接口
| 方法 | 路径 | 描述 |
|------|------|------|
| GET | /api/v1/accounts | 获取账号列表 |
| POST | /api/v1/accounts | 添加账号 |
| PUT | /api/v1/accounts/{id} | 更新账号 |
| DELETE | /api/v1/accounts/{id} | 删除账号 |
| POST | /api/v1/accounts/{id}/refresh-cookie | 刷新 Cookie |

### 规则接口
| 方法 | 路径 | 描述 |
|------|------|------|
| GET | /api/v1/rules | 获取规则列表 |
| POST | /api/v1/rules | 创建规则 |
| PUT | /api/v1/rules/{id} | 更新规则 |
| DELETE | /api/v1/rules/{id} | 删除规则 |

### 统计接口
| 方法 | 路径 | 描述 |
|------|------|------|
| GET | /api/v1/stats/overview | 统计概览 |
| GET | /api/v1/stats/replies | 回复统计 |
| GET | /api/v1/stats/trend | 趋势数据 |

## 套餐说明

| 功能 | 免费版 | 专业版 | 企业版 |
|------|--------|--------|--------|
| 账号数量 | 1 | 5 | 无限 |
| 每日回复上限 | 50 | 500 | 无限 |
| 评论监控 | ✓ | ✓ | ✓ |
| 私信监控 | ✗ | ✓ | ✓ |
| 关键词规则 | 5 | 50 | 无限 |
| AI 智能回复 | ✗ | ✓ | ✓ |
| 数据统计 | 基础 | 完整 | 完整 |
| API 接口 | ✗ | ✓ | ✓ |
| 专属客服 | ✗ | ✗ | ✓ |
| 价格 | ¥0/月 | ¥99/月 | ¥299/月 |

## 安全特性

- [x] 密码加密存储（bcrypt）
- [x] JWT Token 认证
- [x] 访问频率限制
- [x] SQL 注入防护
- [x] XSS 防护
- [x] CORS 配置
- [x] 请求日志审计

## 监控告警

- [x] 系统健康检查
- [x] 异常告警通知
- [x] 业务指标监控
- [x] 日志聚合分析

## 常见问题

### Q: 如何获取小红书 Cookie？
A: 
1. 浏览器打开小红书并登录
2. 按 F12 打开开发者工具
3. 切换到 Network 标签
4. 刷新页面，点击任意请求
5. 在 Request Headers 中找到 Cookie

### Q: 账号被封禁怎么办？
A: 
1. 降低回复频率
2. 使用更自然的回复内容
3. 使用多个账号轮询
4. 建议使用企业号

### Q: 支持哪些支付方式？
A: 
- 微信支付
- 支付宝
- 企业对公转账（企业版）

## 贡献指南

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/xxx`)
3. 提交更改 (`git commit -m 'Add xxx'`)
4. 推送分支 (`git push origin feature/xxx`)
5. 创建 Pull Request

## 许可证

MIT License - see [LICENSE](LICENSE) for details

## 联系方式

- 邮箱: support@example.com
- QQ群: 123456789
- 微信: 添加备注"SaaS咨询"