# ChatStar Admin - 项目结构文档

## 项目结构

```
chatstar_admin/
├── models/                    # 数据模型
│   ├── __init__.py           # 模型导出
│   ├── admin.py              # 管理员模型
│   ├── app.py                # 应用模型
│   ├── user.py               # 用户模型
│   ├── anchor.py             # 主播模型
│   ├── order.py              # 订单模型
│   └── stat.py               # 统计模型
├── routers/                   # API路由
│   ├── __init__.py           # 路由导出
│   ├── auth.py               # 认证路由
│   ├── dashboard.py          # 看板路由
│   ├── user.py               # 用户路由
│   ├── anchor.py             # 主播路由
│   ├── order.py              # 订单路由
│   └── app.py                # 应用路由
├── templates/                 # Jinja2模板
│   ├── login.html            # 登录页
│   ├── dashboard.html        # 看板页
│   ├── user_list.html        # 用户列表
│   ├── anchor_list.html      # 主播列表
│   ├── order_list.html       # 订单列表
│   ├── app_list.html         # 应用列表
│   └── app_config.html       # 应用配置
├── static/                    # 静态文件
├── database.py                # 数据库配置
├── auth.py                    # 认证工具
├── tools.py                   # 工具函数
├── init_admin.py              # 管理员初始化脚本
├── main.py                    # 应用入口
├── requirements.txt           # Python依赖
└── README.md                  # 项目文档
```

## 快速开始

### 环境要求
- Python 3.8+

### 安装步骤

1. **安装Python依赖**
```bash
pip install -r requirements.txt
```

2. **初始化管理员账号**
```bash
python init_admin.py
```

3. **启动服务**
```bash
python main.py
```

或使用 uvicorn:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

服务将在 `http://localhost:8000` 启动

### 访问应用

打开浏览器访问 `http://localhost:8000`

## 默认管理员账号

运行 `python init_admin.py` 后会创建默认管理员账号，默认用户名和密码为：
```
用户名: admin
密码: admin123
```

⚠️ **重要**: 首次登录后请立即修改默认密码！

## 数据库模型

### AdminUser (管理员)
- id: 主键
- username: 用户名（唯一）
- password: 密码哈希
- create_time: 创建时间

### AppList (应用列表)
- id: 主键
- app_name: 应用名称
- package_name: 包名
- is_online: 是否上线

### AppInfo (应用配置)
- id: 主键
- app_id: 应用ID（外键）
- app_name: 应用名称
- app_key: 应用密钥（唯一）
- status: 状态
- config_json: 配置JSON

### AppUser (用户)
- id: 主键
- app_id: 应用ID（外键）
- register_time: 注册时间
- last_login: 最后登录时间
- is_anchor: 是否主播

### Anchor (主播)
- id: 主键
- user_id: 用户ID（外键）
- nickname: 昵称
- income: 收入

### PayOrder (订单)
- id: 主键
- app_id: 应用ID（外键）
- user_id: 用户ID
- pay_amount: 支付金额
- pay_time: 支付时间
- status: 状态（0未支付 1已支付）

### DailyStat (日统计)
- id: 主键
- app_id: 应用ID
- stat_date: 统计日期
- new_user: 新增用户
- dau: 日活
- new_pay_user: 新增付费用户
- total_pay_money: 总付费金额

## 开发说明

### 添加新的数据模型

1. 在 `models/` 中创建新的模型文件
2. 在 `models/__init__.py` 中导出新模型
3. 数据库表会在首次运行时自动创建

### 添加新的路由

1. 在 `routers/` 中创建新的路由文件
2. 在 `routers/__init__.py` 中导出新路由
3. 在 `main.py` 中注册新路由

### 添加新的页面

1. 在 `templates/` 中创建新的HTML模板
2. 在对应的路由文件中添加路由处理函数
3. 使用 Jinja2 模板语法渲染数据

## 生产部署建议

- 使用生产级ASGI服务器（如Gunicorn + Uvicorn）
- 配置HTTPS
- 使用环境变量管理敏感信息
- 配置数据库备份
- 启用日志记录
- 设置CORS白名单
- 修改 `auth.py` 中的 `SECRET_KEY`

启动命令：
```bash
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## 安全建议

1. 修改默认管理员密码
2. 使用强密钥替换 `SECRET_KEY`
3. 启用HTTPS
4. 定期备份数据库
5. 限制API访问频率
6. 定期更新依赖包
7. 在生产环境中设置严格的CORS白名单

## 许可证

MIT License
