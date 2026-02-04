# 湖湘文化数字化平台后端

## 项目简介

这是湖湘文化数字化平台的后端项目，基于Flask框架构建，为前端提供API服务。项目实现了用户认证、文化资源管理、社区互动等功能，采用RESTful API设计，支持前后端分离架构。

## 技术栈

| 技术/框架 | 版本 | 用途 |
|---------|------|------|
| Flask | 2.3.3 | Python Web框架，提供后端API服务 |
| Flask-SQLAlchemy | 3.0.5 | ORM框架，简化数据库操作 |
| PyMySQL | 1.1.0 | MySQL数据库驱动，用于数据库连接和操作 |
| Flask-CORS | 4.0.0 | 处理跨域请求，支持前端API调用 |
| Flask-Migrate | 4.0.5 | 数据库迁移工具，管理数据库结构变更 |
| Werkzeug | 2.3.7 | WSGI工具库，提供Web服务器网关接口实现 |
| PyJWT | 2.8.0 | JSON Web Token实现，用于用户身份验证 |
| flask-jwt-extended | 4.5.3 | JWT扩展库，提供更完善的认证功能 |

## 快速开始

### 1. 环境准备

确保已安装Python 3.8+

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置数据库

编辑 `.env` 文件，配置数据库连接信息：

```env
DATABASE_URL=mysql+pymysql://username:password@localhost/huxiang_culture
DEV_DATABASE_URL=sqlite:///instance/huxiang_culture_dev.db
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here
```

### 4. 初始化数据库

```bash
python init_db.py
```

### 5. 启动服务

```bash
python app.py
```

服务器将在 `http://localhost:5000` 上运行。

## API 接口

### 用户认证

- `POST /api/register`: 用户注册
- `POST /api/login`: 用户登录
- `POST /api/logout`: 用户登出
- `GET/PUT /api/profile/<user_id>`: 获取/更新用户资料

### 文化资源

- `GET /api/resources`: 获取文化资源列表（支持分页、分类筛选）
- `POST /api/resources`: 创建文化资源
- `GET/PUT/DELETE /api/resources/<resource_id>`: 获取/更新/删除特定资源

### 社区功能

- `GET /api/posts`: 获取帖子列表（支持分页）
- `POST /api/posts`: 创建帖子
- `GET/PUT/DELETE /api/posts/<post_id>`: 获取/更新/删除特定帖子
- `GET /api/comments?post_id=<post_id>`: 获取评论列表
- `POST /api/comments`: 创建评论

### 点赞和浏览量

- `POST /api/posts/<post_id>/like`: 为帖子点赞
- `GET /api/posts/<post_id>/liked`: 检查是否已点赞

### 管理员功能

- `GET /api/admin/users`: 获取所有用户列表（仅管理员）

## 功能特性

### 用户权限管理
- JWT认证机制，保障API安全
- 用户角色区分（普通用户/管理员）
- 细粒度权限控制（用户只能修改自己的资源）

### 数据模型
- 用户模型：存储用户信息和权限
- 文化资源模型：管理湖湘文化相关资源
- 帖子模型：支持社区功能
- 评论模型：实现互动交流
- 点赞模型：支持用户互动

### 分页功能
- 支持资源和帖子的分页浏览
- 标准化分页响应格式

### 日志记录
- 记录用户操作和系统事件
- 错误日志便于调试和监控

## 项目结构

```
backend_setup/
├── app.py              # 主应用文件，包含所有路由和模型
├── requirements.txt    # 项目依赖
├── .env               # 环境变量配置
├── config.py          # 应用配置
├── init_db.py         # 数据库初始化脚本
├── logging_config.py  # 日志配置
├── instance/          # 数据库实例存储目录
├── logs/              # 日志文件目录
└── README.md          # 项目说明
```

## 前后端联调

前端项目默认运行在 `http://localhost:5173`，后端运行在 `http://localhost:5000`，通过CORS配置实现跨域访问。

## 部署说明

生产环境建议使用Gunicorn作为WSGI服务器：

```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```