from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, get_jwt
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime, timedelta
import re
import logging
from logging.handlers import RotatingFileHandler


# 数据库实例
db = SQLAlchemy()


# 黑名单令牌存储（简单实现，实际应用中建议使用Redis）
blacklisted_tokens = set()


# 检查令牌是否在黑名单中
def is_token_blacklisted(jti):
    return jti in blacklisted_tokens


# 将令牌加入黑名单
def blacklist_token(jti):
    blacklisted_tokens.add(jti)


# 用户模型
class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    avatar = db.Column(db.String(255))  # 头像URL
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'is_admin': self.is_admin,
            'created_at': self.created_at.isoformat(),
            'avatar': self.avatar
        }


# 文化资源模型
class CulturalResource(db.Model):
    __tablename__ = 'cultural_resources'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(100), nullable=False)  # 分类
    image_url = db.Column(db.String(255))  # 图片URL
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    tags = db.Column(db.String(255))  # 标签
    
    author = db.relationship('User', backref=db.backref('resources', lazy=True))
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'category': self.category,
            'image_url': self.image_url,
            'created_date': self.created_date.isoformat(),
            'author': self.author.to_dict(),
            'tags': self.tags.split(',') if self.tags else []
        }


# 社区帖子模型
class Post(db.Model):
    __tablename__ = 'posts'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    likes_count = db.Column(db.Integer, default=0)
    views = db.Column(db.Integer, default=0)  # 添加浏览量字段
    category = db.Column(db.String(100), default='文化讨论')  # 添加分类字段
    
    author = db.relationship('User', backref=db.backref('posts', lazy=True))
    
    def to_dict(self):
        try:
            # 计算评论数量
            comments_count = Comment.query.filter_by(post_id=self.id).count()
            # 获取分类值，安全处理可能缺失的列
            category_value = getattr(self, 'category', '文化讨论') or '文化讨论'
            # 获取浏览量，安全处理可能缺失的列
            views_value = getattr(self, 'views', 0) or 0
            return {
                'id': self.id,
                'title': self.title,
                'content': self.content,
                'created_at': self.created_at.isoformat(),
                'author': self.author.to_dict() if self.author else {'id': self.author_id, 'username': '未知用户', 'email': '', 'is_admin': False, 'created_at': ''},
                'likes_count': self.likes_count,
                'comments_count': comments_count,
                'views': views_value,
                'category': category_value
            }
        except Exception as e:
            app.logger.error(f'帖子 {self.id} 转换为字典时出错: {str(e)}')
            # 返回一个安全的字典，不包含可能出错的author信息
            return {
                'id': self.id,
                'title': self.title,
                'content': self.content,
                'created_at': self.created_at.isoformat() if self.created_at else '',
                'author': {'id': self.author_id, 'username': '未知用户', 'email': '', 'is_admin': False, 'created_at': ''},
                'likes_count': getattr(self, 'likes_count', 0),
                'comments_count': 0,
                'views': getattr(self, 'views', 0) or 0,
                'category': getattr(self, 'category', '文化讨论') or '文化讨论'
            }


# 评论模型
class Comment(db.Model):
    __tablename__ = 'comments'
    
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    
    author = db.relationship('User', backref=db.backref('comments', lazy=True))
    post = db.relationship('Post', backref=db.backref('comments', lazy=True))
    
    def to_dict(self):
        return {
            'id': self.id,
            'content': self.content,
            'created_at': self.created_at.isoformat(),
            'author': self.author.to_dict(),
            'post_id': self.post_id
        }


# 点赞记录模型
class Like(db.Model):
    __tablename__ = 'likes'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 设置复合唯一约束，防止同一用户重复点赞同一帖子
    __table_args__ = (db.UniqueConstraint('user_id', 'post_id', name='unique_user_post_like'),)


# 初始化应用
def create_app(config_name=None):
    app = Flask(__name__)
    
    # 加载配置
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    from config import config as config_obj
    app.config.from_object(config_obj[config_name])
    
    # 配置CORS，允许跨域请求
    CORS(app, supports_credentials=True, origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000", "http://localhost:5174"], resources={
        r"/api/*": {
            "origins": ["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000", "http://localhost:5174"],
            "allow_headers": ["Content-Type", "Authorization", "Accept", "X-Requested-With", "Access-Control-Request-Headers", "Access-Control-Request-Method"],
            "expose_headers": ["Authorization"],  # 显式暴露Authorization头部
            "supports_credentials": True,
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "max_age": 3600  # 预检请求缓存时间
        }
    })
    
    # 初始化扩展
    db.init_app(app)
    migrate = Migrate(app, db)
    jwt = JWTManager(app)
    
    # JWT额外声明处理
    @jwt.additional_claims_loader
    def add_claims_to_jwt(identity):
        user = User.query.filter_by(id=identity).first()
        return {
            'username': user.username,
            'is_admin': user.is_admin
        }
    
    # JWT过期处理
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({'error': '令牌已过期', 'message': '请重新登录'}), 401
    
    # JWT无效处理
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({'error': '无效的令牌', 'message': '令牌无效'}), 401
    
    # JWT未提供处理
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({'error': '未提供访问令牌', 'message': '需要提供访问令牌'}), 401
    
    # JWT黑名单处理
    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        jti = jwt_payload['jti']
        return is_token_blacklisted(jti)
    
    # 添加JWT刷新时间配置
    app.config['JWT_REFRESH_DELTA'] = timedelta(minutes=15)
    
    # 根路径健康检查
    @app.route('/')
    def index():
        return jsonify({
            'status': 'success',
            'message': '湖湘文化数字化平台API服务运行正常',
            'version': '1.0.0',
            'timestamp': datetime.now().isoformat()
        })

    # 错误处理
    @app.errorhandler(404)
    def not_found(error):
        app.logger.error(f'资源未找到: {request.url}')
        return jsonify({'error': '资源未找到'}), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        app.logger.error(f'服务器内部错误: {str(error)}')
        return jsonify({'error': '服务器内部错误'}), 500
    
    # API路由 - 用户认证
    @app.route('/api/register', methods=['POST'])
    def register():
        data = request.get_json()
        
        # 验证输入数据
        if not data or not data.get('username') or not data.get('email') or not data.get('password'):
            app.logger.warning('注册时缺少必要参数')
            return jsonify({'error': '缺少必要参数'}), 400
        
        username = data['username']
        email = data['email']
        password = data['password']
        
        # 验证邮箱格式
        if not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
            return jsonify({'error': '邮箱格式不正确'}), 400
        
        # 检查用户名或邮箱是否已存在
        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            app.logger.info(f'尝试使用已存在的用户名或邮箱注册: {username}')
            return jsonify({'error': '用户名或邮箱已被注册'}), 409
        
        # 创建新用户
        user = User(username=username, email=email)
        user.set_password(password)
        user.is_admin = False  # 默认非管理员
        
        db.session.add(user)
        db.session.commit()
        
        app.logger.info(f'新用户注册成功: {username}')
        
        return jsonify({
            'success': True,
            'message': '注册成功',
            'user': user.to_dict()
        }), 201


    @app.route('/api/login', methods=['POST'])
    def login():
        data = request.get_json()
        
        if not data or not data.get('username') or not data.get('password'):
            return jsonify({'error': '缺少用户名或密码'}), 400
        
        username_or_email = data['username']
        password = data['password']
        
        # 查找用户（支持用户名或邮箱登录）
        user = User.query.filter(
            (User.username == username_or_email) | (User.email == username_or_email)
        ).first()
        
        if not user or not user.check_password(password):
            app.logger.warning(f'登录失败，用户名或密码错误: {username_or_email}')
            return jsonify({'error': '用户名或密码错误'}), 401
        
        # 登录成功，生成JWT令牌
        access_token = create_access_token(identity=user.id)
        app.logger.info(f'用户登录成功: {user.username}')
        
        return jsonify({
            'success': True,
            'access_token': access_token,
            'user': user.to_dict(),
            'message': '登录成功'
        }), 200


    @app.route('/api/logout', methods=['POST'])
    @jwt_required()
    def logout():
        jti = get_jwt()['jti']
        blacklist_token(jti)
        app.logger.info(f'用户登出: {get_jwt_identity()}')
        return jsonify({'success': True, 'message': '登出成功'}), 200


    @app.route('/api/profile/<int:user_id>', methods=['GET', 'PUT'])
    @jwt_required()
    def profile(user_id):
        current_user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': '用户不存在'}), 404

        # 检查权限：只能修改自己的资料，或管理员可以修改任意用户资料
        current_user = User.query.get(current_user_id)
        if current_user_id != user_id and not current_user.is_admin:
            app.logger.warning(f'用户 {current_user_id} 尝试访问无权限的用户资料 {user_id}')
            return jsonify({'error': '无权访问此资源'}), 403

        if request.method == 'GET':
            app.logger.info(f'用户 {current_user_id} 访问用户 {user_id} 的资料')
            return jsonify({'user': user.to_dict()})

        elif request.method == 'PUT':
            data = request.get_json()

            # 检查用户名是否被其他用户占用
            if 'username' in data:
                username = data['username']
                existing_user = User.query.filter(User.username == username).first()
                if existing_user and existing_user.id != user.id:
                    return jsonify({'error': '用户名已被使用'}), 409

                user.username = username

            if 'avatar' in data:
                user.avatar = data['avatar']

            db.session.commit()

            app.logger.info(f'用户 {current_user_id} 更新了用户 {user_id} 的资料')

            return jsonify({
                'success': True,
                'message': '个人资料更新成功',
                'user': user.to_dict()
            })


    # API路由 - 文化资源
    @app.route('/api/resources', methods=['GET', 'POST'])
    def resources():
        if request.method == 'GET':
            # 获取文化资源列表
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 10, type=int)
            category = request.args.get('category')
            tag = request.args.get('tag')
            
            query = CulturalResource.query
            
            if category:
                query = query.filter(CulturalResource.category == category)
            
            if tag:
                query = query.filter(CulturalResource.tags.like(f'%{tag}%'))
            
            resources = query.paginate(
                page=page, per_page=per_page, error_out=False
            )
            
            app.logger.info(f'用户请求文化资源列表，页码: {page}, 每页数量: {per_page}')
            
            return jsonify({
                'resources': [res.to_dict() for res in resources.items],
                'total': resources.total,
                'pages': resources.pages,
                'current_page': page
            })
        
        elif request.method == 'POST':
            # 需要登录才能创建资源
            try:
                current_user_id = get_jwt_identity()
            except:
                return jsonify({'error': '需要登录'}), 401
            
            data = request.get_json()
            
            if not data or not data.get('title') or not data.get('description'):
                return jsonify({'error': '缺少必要参数'}), 400
            
            resource = CulturalResource(
                title=data['title'],
                description=data['description'],
                category=data.get('category', '未分类'),
                image_url=data.get('image_url'),
                author_id=current_user_id,
                tags=','.join(data.get('tags', []))
            )
            
            db.session.add(resource)
            db.session.commit()
            
            app.logger.info(f'用户 {current_user_id} 创建了新的文化资源: {resource.title}')
            
            return jsonify({
                'success': True,
                'message': '文化资源创建成功',
                'resource': resource.to_dict()
            }), 201


    @app.route('/api/resources/<int:resource_id>', methods=['GET', 'PUT', 'DELETE'])
    @jwt_required()
    def resource_detail(resource_id):
        resource = CulturalResource.query.get(resource_id)
        if not resource:
            return jsonify({'error': '资源不存在'}), 404
                
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if request.method == 'GET':
            app.logger.info(f'用户 {current_user_id} 访问了资源: {resource_id}')
            return jsonify({'resource': resource.to_dict()})
        
        # 检查权限：只能修改/删除自己创建的资源，或管理员可以修改任意资源
        if resource.author_id != current_user_id and not current_user.is_admin:
            app.logger.warning(f'用户 {current_user_id} 尝试访问无权限的资源: {resource_id}')
            return jsonify({'error': '无权访问此资源'}), 403
        
        elif request.method == 'PUT':
            data = request.get_json()
            
            if 'title' in data:
                resource.title = data['title']
            if 'description' in data:
                resource.description = data['description']
            if 'category' in data:
                resource.category = data['category']
            if 'image_url' in data:
                resource.image_url = data['image_url']
            if 'tags' in data:
                resource.tags = ','.join(data['tags'])
            
            db.session.commit()
            
            app.logger.info(f'用户 {current_user_id} 更新了资源: {resource_id}')
            
            return jsonify({
                'success': True,
                'message': '文化资源更新成功',
                'resource': resource.to_dict()
            })
        
        elif request.method == 'DELETE':
            app.logger.info(f'用户 {current_user_id} 删除了资源: {resource_id}')
            db.session.delete(resource)
            db.session.commit()
            
            app.logger.info(f'用户 {current_user_id} 删除了资源: {resource_id}')
            
            return jsonify({
                'success': True,
                'message': '文化资源删除成功'
            })


    # API路由 - 社区功能
    @app.route('/api/posts', methods=['GET', 'POST'])
    @jwt_required()
    def posts():
        if request.method == 'GET':
            try:
                page = request.args.get('page', 1, type=int)
                per_page = request.args.get('per_page', 10, type=int)
                
                posts_pagination = Post.query.order_by(Post.created_at.desc()).paginate(
                    page=page, per_page=per_page, error_out=False
                )
                
                app.logger.info(f'用户请求帖子列表，页码: {page}, 每页数量: {per_page}')
                
                return jsonify({
                    'success': True,
                    'posts': [post.to_dict() for post in posts_pagination.items],
                    'total': posts_pagination.total,
                    'pages': posts_pagination.pages,
                    'current_page': page
                })
            except Exception as e:
                app.logger.error(f'获取帖子列表时发生错误: {str(e)}')
                return jsonify({
                    'success': False,
                    'error': '获取帖子列表失败',
                    'message': str(e)
                }), 500
        
        elif request.method == 'POST':
            # 获取当前用户的ID（已由jwt_required保证）
            current_user_id = get_jwt_identity()
            
            try:
                data = request.get_json()
                
                # 验证请求体
                if not data:
                    return jsonify({'error': '无效的请求数据', 'message': '请求数据格式不正确'}), 400
                
                if not data.get('title') or not data.get('content'):
                    return jsonify({'error': '缺少必要参数', 'message': '标题和内容不能为空'}), 400
                
                # 确保标题和内容长度符合要求
                if len(data['title']) > 200:
                    return jsonify({'error': '标题过长', 'message': '标题不能超过200个字符'}), 400
                
                if len(data['content']) > 5000:
                    return jsonify({'error': '内容过长', 'message': '内容不能超过5000个字符'}), 400
                
                # 获取分类，默认为'文化讨论'
                category = data.get('category', '文化讨论')
                
                post = Post(
                    title=data['title'],
                    content=data['content'],
                    author_id=current_user_id,
                    category=category
                )
                
                db.session.add(post)
                db.session.commit()
                
                app.logger.info(f'用户 {current_user_id} 发布了新帖子: {post.title}')
                
                return jsonify({
                    'success': True,
                    'message': '帖子创建成功',
                    'post': post.to_dict()
                }), 201
            except Exception as e:
                db.session.rollback()  # 确保在出错时回滚事务
                app.logger.error(f'创建帖子时发生错误: {str(e)}')
                return jsonify({'error': '创建帖子失败', 'details': str(e)}), 500


    @app.route('/api/posts/<int:post_id>', methods=['GET', 'PUT', 'DELETE'])
    @jwt_required()
    def post_detail(post_id):
        try:
            # 首先尝试查询帖子
            post = db.session.query(Post).filter(Post.id == post_id).first()
            if not post:
                return jsonify({'error': '帖子不存在', 'code': 404}), 404
                
            current_user_id = get_jwt_identity()
            current_user_obj = User.query.get(current_user_id)
            if not current_user_obj:
                return jsonify({'error': '用户不存在', 'code': 404}), 404
            
            if request.method == 'GET':
                app.logger.info(f'用户 {current_user_id} 访问了帖子: {post_id}')
                
                # 增加浏览量（排除作者自己和管理员）
                if post.author_id != current_user_id and not current_user_obj.is_admin:
                    post.views = post.views + 1
                    try:
                        db.session.commit()
                        app.logger.info(f'帖子 {post_id} 浏览量增加到: {post.views}')
                    except Exception as e:
                        db.session.rollback()
                        app.logger.error(f'更新帖子浏览量时出错: {str(e)}')
                
                return jsonify({'post': post.to_dict()})
            
            # 检查权限：只能修改/删除自己创建的帖子，或管理员可以修改任意帖子
            if post.author_id != current_user_id and not current_user_obj.is_admin:
                app.logger.warning(f'用户 {current_user_id} 尝试访问无权限的帖子: {post_id}')
                return jsonify({'error': '无权访问此资源', 'code': 403}), 403
            
            elif request.method == 'PUT':
                data = request.get_json()
                
                if 'title' in data:
                    post.title = data['title']
                if 'content' in data:
                    post.content = data['content']
                if 'category' in data:
                    post.category = data['category']
                
                try:
                    db.session.commit()
                    app.logger.info(f'用户 {current_user_id} 更新了帖子: {post_id}')
                    
                    return jsonify({
                        'success': True,
                        'message': '帖子更新成功',
                        'post': post.to_dict()
                    })
                except Exception as e:
                    db.session.rollback()
                    app.logger.error(f'更新帖子时发生错误: {str(e)}')
                    return jsonify({'error': '更新帖子失败', 'message': str(e)}), 500
            
            elif request.method == 'DELETE':
                try:
                    db.session.delete(post)
                    db.session.commit()
                    app.logger.info(f'用户 {current_user_id} 删除了帖子: {post_id}')
                    
                    return jsonify({
                        'success': True,
                        'message': '帖子删除成功'
                    })
                except Exception as e:
                    db.session.rollback()
                    app.logger.error(f'删除帖子时发生错误: {str(e)}')
                    return jsonify({'error': '删除帖子失败', 'message': str(e)}), 500
                    
        except Exception as e:
            app.logger.error(f'处理帖子详情请求时发生错误: {str(e)}')
            return jsonify({'error': '服务器内部错误', 'message': str(e)}), 500


    # 点赞帖子API
    @app.route('/api/posts/<int:post_id>/like', methods=['POST'])
    @jwt_required()
    def like_post(post_id):
        try:
            current_user_id = get_jwt_identity()
            app.logger.info(f'用户 {current_user_id} 尝试点赞帖子 {post_id}')
            
            post = Post.query.get(post_id)
            if not post:
                app.logger.warning(f'帖子 {post_id} 不存在')
                return jsonify({'error': '帖子不存在', 'code': 404}), 404
            
            # 检查用户是否已经点赞过
            existing_like = Like.query.filter_by(user_id=current_user_id, post_id=post_id).first()
            if existing_like:
                app.logger.info(f'用户 {current_user_id} 已经给帖子 {post_id} 点过赞')
                return jsonify({'success': False, 'message': '您已经点过赞了', 'likes_count': post.likes_count}), 200
            
            # 创建点赞记录
            new_like = Like(user_id=current_user_id, post_id=post_id)
            db.session.add(new_like)
            
            # 增加点赞数
            old_likes = post.likes_count
            post.likes_count = post.likes_count + 1
            
            try:
                db.session.commit()
                app.logger.info(f'用户 {current_user_id} 成功点赞帖子 {post_id}，点赞数从 {old_likes} 更新为 {post.likes_count}')
                
                return jsonify({
                    'success': True,
                    'message': '点赞成功',
                    'likes_count': post.likes_count
                })
            except Exception as e:
                db.session.rollback()
                app.logger.error(f'更新帖子点赞数时出错: {str(e)}')
                return jsonify({'error': '更新点赞数失败', 'message': str(e)}), 500
        except Exception as e:
            app.logger.error(f'点赞帖子时发生错误: {str(e)}')
            return jsonify({'error': '点赞失败', 'message': str(e)}), 500


    # API路由 - 评论功能
    @app.route('/api/comments', methods=['GET', 'POST'])
    @jwt_required()
    def comments():
        try:
            current_user_id = get_jwt_identity()
            
            if request.method == 'GET':
                post_id = request.args.get('post_id', type=int)
                
                query = Comment.query
                
                if post_id:
                    query = query.filter(Comment.post_id == post_id)
                
                comments = query.all()
                
                app.logger.info(f'用户 {current_user_id} 请求评论列表，帖子ID: {post_id}')
                
                return jsonify({
                    'comments': [comment.to_dict() for comment in comments]
                })
            
            elif request.method == 'POST':
                data = request.get_json()
                
                if not data or not data.get('content') or not data.get('post_id'):
                    return jsonify({'error': '缺少必要参数'}), 400
                
                comment = Comment(
                    content=data['content'],
                    author_id=current_user_id,
                    post_id=data['post_id']
                )
                
                db.session.add(comment)
                db.session.commit()
                
                app.logger.info(f'用户 {current_user_id} 对帖子 {data["post_id"]} 发表了评论')
                
                return jsonify({
                    'success': True,
                    'message': '评论创建成功',
                    'comment': comment.to_dict()
                }), 201
        except Exception as e:
            app.logger.error(f'评论操作时发生错误: {str(e)}')
            return jsonify({'error': '服务器内部错误', 'message': str(e)}), 500


    # 管理员API路由
    @app.route('/api/admin/users', methods=['GET'])
    @jwt_required()
    def get_all_users():
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if not current_user.is_admin:
            app.logger.warning(f'用户 {current_user_id} 尝试访问管理员功能')
            return jsonify({'error': '需要管理员权限'}), 403
        
        users = User.query.all()
        app.logger.info(f'管理员 {current_user_id} 请求了所有用户列表')
        
        return jsonify({
            'users': [user.to_dict() for user in users]
        })


    return app


# 添加日志
def setup_logging(app):
    """
    设置应用的日志配置
    """
    # 确保logs目录存在
    if not os.path.exists('logs'):
        os.mkdir('logs')
    
    # 设置日志格式
    formatter = logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    )
    
    # 创建一个轮转文件处理器，最大10MB，保留3个备份
    file_handler = RotatingFileHandler(
        'logs/huxiang.log',
        maxBytes=10240000,
        backupCount=3
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    
    # 添加处理器到应用日志
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('胡湘文化平台启动')

# 创建应用实例
app = create_app()

# 添加日志
setup_logging(app)


# 全局错误处理，捕获所有未处理的异常
@app.errorhandler(Exception)
def handle_exception(e):
    # 记录异常
    app.logger.error(f'未处理的异常: {str(e)}', exc_info=True)
    
    # 如果是HTTPException，交给默认处理程序
    if hasattr(e, 'code') and e.code is not None:
        return jsonify({'error': str(e), 'code': e.code}), e.code
    
    # 对于其他异常，返回JSON格式的错误信息
    return jsonify({'error': '服务器内部错误', 'message': '服务器发生了未预期的错误'}), 500


# 错误处理
@app.errorhandler(404)
def not_found(error):
    app.logger.error(f'资源未找到: {request.url}')
    return jsonify({'error': '资源未找到'}), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    app.logger.error(f'服务器内部错误: {str(error)}')
    return jsonify({'error': '服务器内部错误'}), 500

# 运行应用
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)

# 在其他模块导入时确保创建表
else:
    with app.app_context():
        db.create_all()
