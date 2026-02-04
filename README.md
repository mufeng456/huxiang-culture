# 湖湘文化数字化平台

## 项目概述

湖湘文化数字化平台是一个致力于通过数字化手段展示、传播和传承湖湘文化精髓的综合性Web应用。该项目旨在利用现代信息技术，将湖湘地区丰富的历史文化遗产、民俗风情、传统艺术等资源进行数字化呈现，促进文化的保护与传承，同时为用户提供便捷的文化资源获取和互动交流平台。

## 项目结构

项目采用前后端分离的架构设计，分为两个主要部分：

1. **HuXiang_github**：基于Vue 3的前端项目
2. **HX_project**（位于backend_setup目录）：基于Flask的后端项目

## 技术栈

### 前端技术栈

| 技术/框架 | 版本 | 用途 |
|---------|------|------|
| Vue.js | 3.5.21 | 前端框架，用于构建用户界面和组件化开发 |
| Vue Router | 4.5.1 | 前端路由管理，实现页面间的导航和参数传递 |
| Vite | 7.1.7 | 现代化前端构建工具，提供快速的开发体验和优化的构建输出 |
| Font Awesome | 7.0.1 | 图标库，提供丰富的图标资源用于界面设计 |
| 原生CSS | - | 样式设计，实现响应式布局和界面美化 |
| Unity WebGL | - | 3D内容展示，用于数字化展示部分 |

### 后端技术栈

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

## 功能模块

### 1. 首页模块

作为平台的门户，展示平台的核心功能入口和最新文化资源推荐，提供全局导航和搜索功能。

### 2. 文化资源库模块

集中展示湖湘地区的各类文化资源，包括历史遗迹、传统艺术、文学作品、民俗风情、饮食文化、建筑风格、宗教文化、历史伟人事迹等。支持按分类浏览、关键词搜索和分页展示功能。

资源数据结构：
- 标题、描述、分类、图片URL、创建日期

### 3. 互动社区模块

提供用户交流互动的平台，支持用户发布、浏览和评论文化相关的帖子和讨论。该模块需要用户登录才能访问。

### 4. 数字化展示模块

利用Unity WebGL技术实现文化资源的3D展示和互动体验，为用户提供沉浸式的文化体验。

### 5. 知识图谱模块

可视化展示湖湘文化元素之间的关联关系，帮助用户更好地理解和探索湖湘文化的内在联系。

### 6. 用户认证与管理模块

- **登录/注册**：支持用户通过用户名/邮箱和密码进行登录和注册
- **个人资料**：用户可以查看和管理个人信息
- **权限控制**：区分普通用户和管理员权限

### 7. 管理员模块

提供后台管理功能，支持管理员对文化资源、用户和社区内容进行管理和维护

## 开发环境配置

### 前端环境配置

1. 确保已安装Node.js 14.18+ 或 16+版本
2. 克隆项目仓库到本地
3. 进入项目根目录，安装依赖：
   ```bash
   npm install
   ```
4. 启动前端开发服务器：
   ```bash
   npm run dev
   ```
   前端服务将在 `http://localhost:5173` 上运行

### 后端环境配置

1. 确保已安装Python 3.8+
2. 进入 `backend_setup` 目录
3. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```
4. 配置数据库连接信息，在 `.env` 文件中设置：
   ```env
   DATABASE_URL=mysql+pymysql://username:password@localhost/huxiang_culture
   DEV_DATABASE_URL=sqlite:///instance/huxiang_culture_dev.db
   SECRET_KEY=your-secret-key-here
   JWT_SECRET_KEY=your-jwt-secret-key-here
   ```
5. 初始化数据库：
   ```bash
   python init_db.py
   ```
6. 启动后端服务：
   ```bash
   python app.py
   ```
   后端服务将在 `http://localhost:5000` 上运行

## 前后端集成

前端通过API与后端进行数据交互，默认情况下：
- 前端运行在 `http://localhost:5173`
- 后端API运行在 `http://localhost:5000`
- 通过CORS配置实现跨域访问

## API接口说明

### 用户认证接口

- `POST /api/register` - 用户注册
- `POST /api/login` - 用户登录
- `POST /api/logout` - 用户登出
- `GET/PUT /api/profile/:userId` - 获取/更新用户资料

### 文化资源接口

- `GET /api/resources` - 获取文化资源列表（支持分页、分类筛选）
- `POST /api/resources` - 创建文化资源
- `GET/PUT/DELETE /api/resources/:id` - 获取/更新/删除特定资源

### 社区功能接口

- `GET /api/posts` - 获取帖子列表（支持分页）
- `POST /api/posts` - 创建帖子
- `GET/PUT/DELETE /api/posts/:id` - 获取/更新/删除特定帖子
- `GET /api/comments` - 获取评论列表
- `POST /api/comments` - 创建评论

### 点赞和浏览量接口

- `POST /api/posts/:postId/like` - 为帖子点赞
- `GET /api/posts/:postId/liked` - 检查是否已点赞

### 管理员接口

- `GET /api/admin/users` - 获取所有用户列表（仅管理员）

## 项目构建与部署

### 前端构建

在项目根目录执行以下命令构建生产版本：
```bash
npm run build
```
构建产物将生成在 `dist` 目录中

### 后端部署

后端服务可以通过多种方式进行部署，推荐使用Gunicorn作为WSGI服务器：
```bash
cd backend_setup
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## 前端项目结构

```
src/
├── assets/         # 静态资源文件
│   ├── css/        # 样式文件
│   └── imgs/       # 图片文件
├── components/     # Vue组件
│   ├── CommentsSection.vue  # 评论组件
│   └── Navbar.vue           # 导航栏组件
├── views/          # 页面组件
├── router/         # 路由配置
├── services/       # API服务
├── App.vue         # 根组件
└── main.js         # 应用入口
```

## 后端项目结构

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

## 初始账户

- 管理员账号：用户名 `admin`，密码 `admin123`

## 注意事项

1. 确保前后端服务都正常运行后才能正常使用平台功能
2. 数据库初始化是必要的步骤，确保所有表结构和初始数据正确创建
3. 在生产环境中，请务必更改默认的密钥配置
4. 前端开发时，Vite会自动代理API请求到后端服务，无需担心跨域问题

## 贡献指南

如果您希望为项目做出贡献，请遵循以下步骤：

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/FeatureName`)
3. 提交更改 (`git commit -m 'Add some FeatureName'`)
4. 推送到分支 (`git push origin feature/FeatureName`)
5. 创建 Pull Request

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](./LICENSE) 文件