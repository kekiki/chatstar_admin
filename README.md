# ChatStar Admin - 手机应用管理后台

一个功能完善的手机应用管理后台系统，基于 React 构建，提供实时数据看板、用户管理、主播管理、订单管理和应用配置等功能。

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

### 前端
- **框架**: React 18
- **路由**: React Router 6
- **图表库**: Recharts
- **图标库**: Lucide React
- **样式**: Tailwind CSS
- **构建工具**: Vite

## 项目结构

```
chatstar_admin/
└── frontend/                   # 前端代码
    ├── src/
    │   ├── components/        # 组件
    │   │   ├── MainLayout.jsx # 主布局
    │   │   └── ProtectedRoute.jsx # 路由保护
    │   ├── contexts/          # 上下文
    │   │   └── AuthContext.jsx # 认证上下文
    │   ├── pages/             # 页面
    │   │   ├── Login.jsx      # 登录页
    │   │   ├── Dashboard.jsx  # 看板
    │   │   ├── Users.jsx      # 用户管理
    │   │   ├── Streamers.jsx  # 主播管理
    │   │   ├── Orders.jsx     # 订单管理
    │   │   └── AppConfig.jsx  # 应用配置
    │   ├── App.jsx            # 应用根组件
    │   ├── main.jsx           # 入口文件
    │   └── index.css          # 全局样式
    ├── index.html             # HTML模板
    ├── package.json           # 依赖配置
    ├── vite.config.js         # Vite配置
    ├── tailwind.config.js     # Tailwind配置
    └── postcss.config.js      # PostCSS配置
```

## 快速开始

### 环境要求
- Node.js 16+
- npm 或 yarn

### 安装步骤

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

## 默认登录

```
用户名: admin
密码: admin123
```

**注意**: 当前版本使用模拟数据，任何用户名和密码都可以登录。

## 开发说明

### 添加新的前端页面

1. 在 `frontend/src/pages/` 中创建新的页面组件
2. 在 `frontend/src/components/MainLayout.jsx` 中添加菜单项
3. 在 `frontend/src/App.jsx` 中添加路由

## 生产部署

### 前端
- 构建生产版本：`npm run build`
- 使用Nginx等Web服务器托管静态文件
- 配置CDN加速
- 启用Gzip压缩
- 设置缓存策略

## 许可证

MIT License
