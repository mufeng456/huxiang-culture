# 湖湘文化数字化平台后端

## 项目简介

这是湖湘文化数字化平台的后端项目，基于Flask框架构建，为前端提供API服务。

## 技术栈

- Flask: Python Web框架
- Flask-SQLAlchemy: ORM框架
- PyMySQL: MySQL数据库驱动
- Flask-CORS: 处理跨域请求

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
DATABASE_URL=mysql+pymysql://username:password@localhost/database_name
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

- `GET /api/resources`: 获取文化资源列表
- `POST /api/resources`: 创建文化资源
- `GET/PUT/DELETE /api/resources/<resource_id>`: 获取/更新/删除特定资源

### 社区功能

- `GET /api/posts`: 获取帖子列表
- `POST /api/posts`: 创建帖子
- `GET/PUT/DELETE /api/posts/<post_id>`: 获取/更新/删除特定帖子

- `GET /api/comments`: 获取评论列表
- `POST /api/comments`: 创建评论

## 项目结构

```
HX_project/
├── app.py           # 主应用文件
├── requirements.txt # 项目依赖
├── .env            # 环境变量配置
├── init_db.py      # 数据库初始化脚本
└── README.md       # 项目说明
```

## 前后端联调

前端项目默认运行在 `http://localhost:5173`，后端运行在 `http://localhost:5000`，通过CORS配置实现跨域访问。