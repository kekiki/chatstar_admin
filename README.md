# ChatStar Admin - 管理后台

##在虚拟环境运行项目
1.进入你的项目文件夹
```bash
cd ~/你的项目文件夹
```

2. 创建名为 .venv 可访问全局包的虚拟环境
```bash
python -m venv .venv --system-site-packages
```

3.激活虚拟环境（Mac zsh）,激活成功后，终端前缀会出现 (venv) 标识。
```bash
source .venv/bin/activate
```

4.在虚拟环境里执行 Python /pip 命令
```bash
python -m pip install -r requirements.txt
```

5.退出虚拟环境
```bash
deactivate
```

## 功能特性

### 🎯 核心功能
- **实时看板** - 多维度数据可视化展示
  - 新增付费趋势图
  - 总付费统计
  - 新增用户趋势
  - 日活用户统计
  - 新增付费用户
  - 总付费金额

- **用户管理** - 完整的用户生命周期管理
  - 用户列表查看（支持分页、搜索、筛选）
  - 全字段模糊搜索
  - 注册时间区间筛选

- **主播管理** - 主播账号管理
  - 主播列表查看（支持分页、搜索、筛选）
  - 全字段模糊搜索
  - 收入统计

- **订单管理** - 订单全流程管理
  - 订单列表查看（支持分页、搜索、筛选）
  - 订单状态筛选
  - 支付时间区间筛选
  - 订单数据导出（Excel）

- **应用配置** - 多应用管理
  - 应用列表管理
  - 应用配置管理
  - 应用密钥管理
  - 应用状态控制

## 技术栈

### 后端
- **框架**: FastAPI
- **ORM**: SQLAlchemy
- **认证**: JWT (python-jose)
- **密码加密**: Passlib (bcrypt)
- **数据库**: SQLite (可配置PostgreSQL)
- **模板引擎**: Jinja2
- **Excel导出**: openpyxl
