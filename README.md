# ChatStar Admin - 手机应用管理后台

一个功能完善的手机应用管理后台系统，基于 FastAPI 和 React 构建，提供实时数据看板、用户管理、主播管理、订单管理和应用配置等功能。

## 功能特性

### 🎯 核心功能
- **实时看板** - 多维度数据可视化展示
  - 新增付费趋势图
  - 总付费统计
  - 新增用户趋势
  - 日活用户统计
  - 新增付费率
  - 日活付费率

- **用户管理** - 完整的用户生命周期管理
  - 用户列表查看（支持分页、搜索、筛选）
  - 用户状态管理（启用/禁用）
  - 会员状态管理
  - 用户信息编辑
  - 用户删除

- **主播管理** - 主播账号管理
  - 主播列表查看（支持分页、搜索、筛选）
  - 主播状态管理
  - 认证状态管理
  - 粉丝数和收入统计
  - 主播信息编辑

- **订单管理** - 订单全流程管理
  - 订单列表查看（支持分页、搜索、筛选）
  - 订单状态更新（完成/取消/退款）
  - 订单统计概览
  - 按时间范围筛选

- **应用配置** - 多应用管理
  - 应用创建和编辑
  - 应用密钥管理
  - 应用状态控制
  - JSON配置管理
  - 密钥重置功能

### 🎨 界面特性
- 现代化UI设计，基于Tailwind CSS
- 响应式布局，支持移动端
- 实时数据图表（使用Recharts）
- 流畅的用户体验
- 直观的数据可视化

## 技术栈

### 后端
- **框架**: FastAPI 0.109.0
- **ORM**: SQLAlchemy 2.0.25
- **认证**: JWT (python-jose)
- **密码加密**: Passlib (bcrypt)
- **数据库**: SQLite (可配置PostgreSQL)
- **数据验证**: Pydantic 2.5.3

### 前端
- **框架**: React 18
- **路由**: React Router 6
- **HTTP客户端**: Axios
- **图表库**: Recharts
- **图标库**: Lucide React
- **样式**: Tailwind CSS
- **构建工具**: Vite

## 项目结构

```
chatstar_admin/
├── backend/                    # 后端代码
│   ├── models/                 # 数据模型
│   │   ├── admin.py           # 管理员模型
│   │   ├── user.py            # 用户模型
│   │   ├── streamer.py        # 主播模型
│   │   ├── order.py           # 订单模型
│   │   ├── app.py             # 应用模型
│   │   ├── payment.py         # 支付模型
│   │   └── activity.py        # 活动模型
│   ├── routers/                # API路由
│   │   ├── auth.py            # 认证接口
│   │   ├── dashboard.py       # 看板接口
│   │   ├── users.py           # 用户接口
│   │   ├── streamers.py       # 主播接口
│   │   ├── orders.py          # 订单接口
│   │   └── apps.py            # 应用接口
│   ├── config.py              # 配置文件
│   ├── database.py            # 数据库配置
│   ├── auth.py                # 认证工具
│   ├── schemas.py             # Pydantic模型
│   ├── main.py                # 应用入口
│   └── init_db.py             # 数据库初始化脚本
├── frontend/                   # 前端代码
│   ├── src/
│   │   ├── components/        # 组件
│   │   │   ├── MainLayout.jsx # 主布局
│   │   │   └── ProtectedRoute.jsx # 路由保护
│   │   ├── contexts/          # 上下文
│   │   │   └── AuthContext.jsx # 认证上下文
│   │   ├── pages/             # 页面
│   │   │   ├── Login.jsx      # 登录页
│   │   │   ├── Dashboard.jsx  # 看板
│   │   │   ├── Users.jsx      # 用户管理
│   │   │   ├── Streamers.jsx  # 主播管理
│   │   │   ├── Orders.jsx     # 订单管理
│   │   │   └── AppConfig.jsx  # 应用配置
│   │   ├── App.jsx            # 应用根组件
│   │   ├── main.jsx           # 入口文件
│   │   └── index.css          # 全局样式
│   ├── index.html             # HTML模板
│   ├── package.json           # 依赖配置
│   ├── vite.config.js         # Vite配置
│   ├── tailwind.config.js     # Tailwind配置
│   └── postcss.config.js      # PostCSS配置
├── requirements.txt           # Python依赖
├── .env.example              # 环境变量示例
└── README.md                 # 项目文档
```

## 快速开始

### 环境要求
- Python 3.8+
- Node.js 16+
- npm 或 yarn

### 后端安装

1. **克隆项目**
```bash
cd chatstar_admin
```

2. **创建虚拟环境**
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows
```

3. **安装Python依赖**
```bash
pip3 install -r requirements.txt
```

4. **配置环境变量**
```bash
cp .env.example .env
```

编辑 `.env` 文件，设置你的配置：
```
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
DATABASE_URL=sqlite:///./chatstar_admin.db
```

5. **初始化数据库**
```bash
python3 init_db.py
```

这将创建数据库并插入示例数据。

6. **启动后端服务**
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

后端服务将在 `http://localhost:8000` 启动

API文档地址: `http://localhost:8000/docs`

### 前端安装

1. **进入前端目录**
```bash
cd frontend
```

2. **安装Node依赖**
```bash
npm install
```

3. **启动前端开发服务器**
```bash
npm run dev
```

前端服务将在 `http://localhost:3000` 启动

### 访问应用

打开浏览器访问 `http://localhost:3000`

## 默认管理员账号

```
用户名: admin
密码: admin123
```

⚠️ **重要**: 首次登录后请立即修改默认密码！

## API接口文档

### 认证接口

#### 登录
```
POST /api/auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "admin123"
}

Response:
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "user": {...}
}
```

#### 获取当前用户
```
GET /api/auth/me
Authorization: Bearer {access_token}
```

### 看板接口

#### 获取总体统计
```
GET /api/dashboard/stats
Authorization: Bearer {access_token}
```

#### 获取应用列表
```
GET /api/dashboard/apps
Authorization: Bearer {access_token}
```

#### 获取应用详细统计
```
GET /api/dashboard/app/{app_id}/stats
Authorization: Bearer {access_token}
```

### 用户管理接口

#### 获取用户列表
```
GET /api/users?page=1&per_page=20&search=&app_id=&is_active=&is_premium=
Authorization: Bearer {access_token}
```

#### 获取单个用户
```
GET /api/users/{user_id}
Authorization: Bearer {access_token}
```

#### 更新用户
```
PUT /api/users/{user_id}
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "is_active": true,
  "is_premium": false,
  "username": "new_username",
  "email": "new@example.com",
  "phone": "13800000000"
}
```

#### 删除用户
```
DELETE /api/users/{user_id}
Authorization: Bearer {access_token}
```

### 主播管理接口

#### 获取主播列表
```
GET /api/streamers?page=1&per_page=20&search=&app_id=&is_active=&is_verified=
Authorization: Bearer {access_token}
```

#### 获取单个主播
```
GET /api/streamers/{streamer_id}
Authorization: Bearer {access_token}
```

#### 更新主播
```
PUT /api/streamers/{streamer_id}
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "is_active": true,
  "is_verified": true,
  "display_name": "新显示名称",
  "bio": "新简介",
  "avatar_url": "https://example.com/avatar.png"
}
```

#### 删除主播
```
DELETE /api/streamers/{streamer_id}
Authorization: Bearer {access_token}
```

### 订单管理接口

#### 获取订单列表
```
GET /api/orders?page=1&per_page=20&search=&app_id=&user_id=&status=&start_date=&end_date=
Authorization: Bearer {access_token}
```

#### 获取单个订单
```
GET /api/orders/{order_id}
Authorization: Bearer {access_token}
```

#### 更新订单状态
```
PUT /api/orders/{order_id}
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "status": "completed"
}
```

#### 获取订单统计
```
GET /api/orders/stats/summary?app_id=
Authorization: Bearer {access_token}
```

### 应用配置接口

#### 获取应用列表
```
GET /api/apps
Authorization: Bearer {access_token}
```

#### 创建应用
```
POST /api/apps
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "name": "应用名称",
  "description": "应用描述",
  "icon_url": "https://example.com/icon.png",
  "config": {}
}
```

#### 获取单个应用
```
GET /api/apps/{app_id}
Authorization: Bearer {access_token}
```

#### 更新应用
```
PUT /api/apps/{app_id}
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "name": "新应用名称",
  "description": "新描述",
  "icon_url": "https://example.com/new-icon.png",
  "is_active": true,
  "config": {}
}
```

#### 删除应用
```
DELETE /api/apps/{app_id}
Authorization: Bearer {access_token}
```

#### 重新生成应用密钥
```
POST /api/apps/{app_id}/regenerate-key
Authorization: Bearer {access_token}
```

## 数据库模型

### Admin (管理员)
- id: 主键
- username: 用户名（唯一）
- email: 邮箱（唯一）
- password_hash: 密码哈希
- is_active: 是否激活
- created_at: 创建时间
- last_login: 最后登录时间

### User (用户)
- id: 主键
- app_id: 应用ID（外键）
- username: 用户名
- email: 邮箱
- phone: 手机号
- is_active: 是否激活
- is_premium: 是否会员
- total_spent: 总消费金额
- created_at: 注册时间
- last_active: 最后活跃时间

### Streamer (主播)
- id: 主键
- app_id: 应用ID（外键）
- username: 用户名
- display_name: 显示名称
- avatar_url: 头像URL
- bio: 简介
- is_active: 是否激活
- is_verified: 是否认证
- follower_count: 粉丝数
- total_earnings: 总收入
- created_at: 创建时间
- last_stream: 最后直播时间

### Order (订单)
- id: 主键
- app_id: 应用ID（外键）
- user_id: 用户ID（外键）
- order_no: 订单号（唯一）
- amount: 金额
- status: 状态（pending/completed/cancelled/refunded）
- payment_method: 支付方式
- product_type: 产品类型
- product_id: 产品ID
- created_at: 创建时间
- completed_at: 完成时间

### Payment (支付)
- id: 主键
- app_id: 应用ID（外键）
- user_id: 用户ID（外键）
- order_id: 订单ID（外键）
- amount: 金额
- payment_type: 支付类型（new/renewal）
- created_at: 创建时间

### Activity (活动)
- id: 主键
- app_id: 应用ID（外键）
- user_id: 用户ID（外键）
- activity_date: 活动日期
- session_count: 会话数
- duration_seconds: 时长（秒）
- created_at: 创建时间

### App (应用)
- id: 主键
- name: 应用名称（唯一）
- app_key: 应用密钥（唯一）
- description: 描述
- icon_url: 图标URL
- is_active: 是否激活
- config: 配置（JSON）
- created_at: 创建时间
- updated_at: 更新时间

## 开发说明

### 添加新的API端点

1. 在 `models/` 中创建或修改数据模型
2. 在 `schemas.py` 中添加Pydantic模型
3. 在 `routers/` 中创建新的路由文件
4. 在 `routers/__init__.py` 中注册路由
5. 在 `main.py` 中注册路由

### 添加新的前端页面

1. 在 `frontend/src/pages/` 中创建新的页面组件
2. 在 `frontend/src/components/MainLayout.jsx` 中添加菜单项
3. 在 `frontend/src/App.jsx` 中添加路由

### 数据库迁移

当前使用SQLite，如需切换到PostgreSQL：

1. 修改 `.env` 中的 `DATABASE_URL`
2. 安装PostgreSQL驱动：`pip install psycopg2-binary`
3. 重新运行 `python3 init_db.py`

## 生产部署建议

### 后端
- 使用生产级ASGI服务器（如Gunicorn + Uvicorn）
- 配置HTTPS
- 使用环境变量管理敏感信息
- 配置数据库备份
- 启用日志记录
- 设置CORS白名单
- 使用强密钥替换 `SECRET_KEY`

启动命令：
```bash
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### 前端
- 构建生产版本：`npm run build`
- 使用Nginx等Web服务器托管静态文件
- 配置CDN加速
- 启用Gzip压缩
- 设置缓存策略

## 安全建议

1. 修改默认管理员密码
2. 使用强密钥替换 `SECRET_KEY`
3. 启用HTTPS
4. 定期备份数据库
5. 限制API访问频率
6. 实施输入验证和SQL注入防护
7. 定期更新依赖包
8. 在生产环境中禁用CORS或设置严格的白名单

## 故障排查

### 后端无法启动
- 检查Python版本是否为3.8+
- 确认所有依赖已安装：`pip3 list`
- 检查端口8000是否被占用
- 查看错误日志

### 前端无法连接后端
- 确认后端服务已启动
- 检查 `vite.config.js` 中的代理配置
- 查看浏览器控制台的错误信息
- 确认CORS配置正确

### 数据库错误
- 删除现有的数据库文件
- 重新运行 `python3 init_db.py`
- 检查数据库文件权限

## 许可证

MIT License

## 联系方式

如有问题或建议，请联系开发团队。
