# ChatStar Admin - 管理后台

一个功能完善的手机应用管理后台系统，基于 React 构建，提供实时数据看板、用户管理、主播管理、订单管理和应用配置等功能。

## 项目结构

```
chatstar_admin/
├── main.py               # 程序入口、路由、登录逻辑
├── database.py           # SQLAlchemy数据库连接
├── models.py             # 数据表模型（管理员、用户、主播、订单、应用）
├── schemas.py            # Pydantic数据模型
├── auth.py               # JWT登录鉴权工具
├── static/               # 静态资源 css/js/echarts
│   ├── css/
│   │   └── admin.css
│   └── js/
│       ├── echarts.min.js
│       └── admin.js
└── templates/            # Jinja2页面模板
    ├── login.html        # 登录页面
    ├── base.html         # 后台通用布局（侧边栏+顶部导航）
    ├── dashboard.html    # 实时看板（多图表）
    ├── user_list.html    # 用户管理
    ├── anchor_list.html  # 主播管理
    ├── order_list.html   # 订单管理
    └── app_config.html   # 应用配置
```

## 许可证

MIT License
