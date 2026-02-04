import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import db, User, CulturalResource, Post, Comment, create_app
from werkzeug.security import generate_password_hash

def init_database():
    """初始化数据库并添加示例数据"""
    # 创建应用实例
    app = create_app()
    
    with app.app_context():
        # 创建所有表
        db.create_all()
        
        # 检查是否已有管理员账户
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            # 创建管理员用户
            admin = User(
                username='admin',
                email='admin@example.com',
                is_admin=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
            print("管理员账户已创建: admin / admin123")
        
        # 创建一些示例用户
        sample_users_data = [
            {'username': 'user1', 'email': 'user1@example.com', 'password': 'password1'},
            {'username': 'user2', 'email': 'user2@example.com', 'password': 'password2'},
            {'username': 'huxiang_fan', 'email': 'fan@example.com', 'password': 'huxiang123'}
        ]
        
        for user_data in sample_users_data:
            existing_user = User.query.filter_by(username=user_data['username']).first()
            if not existing_user:
                user = User(
                    username=user_data['username'],
                    email=user_data['email'],
                    is_admin=False
                )
                user.set_password(user_data['password'])
                db.session.add(user)
        
        db.session.commit()
        
        # 创建一些示例文化资源
        sample_resources = [
            {
                'title': '湖南花鼓戏',
                'description': '湖南花鼓戏是中国湖南省的地方戏曲剧种之一，起源于民间歌舞小戏，具有浓郁的乡土气息。',
                'category': '传统艺术',
                'tags': ['戏曲', '湖南', '民间艺术']
            },
            {
                'title': '岳麓书院',
                'description': '岳麓书院位于湖南省长沙市湘江西岸的岳麓山脚下，是中国古代四大书院之一。',
                'category': '历史文化',
                'tags': ['书院', '教育', '古建筑']
            },
            {
                'title': '湘菜文化',
                'description': '湘菜，又称湖南菜，是中国历史悠久的八大菜系之一，以辣味著称。',
                'category': '饮食文化',
                'tags': ['美食', '湖南', '烹饪']
            }
        ]
        
        # 获取创建的用户
        admin_user = User.query.filter_by(username='admin').first()
        sample_user = User.query.filter_by(username='user1').first()
        
        for idx, resource_data in enumerate(sample_resources):
            existing_resource = CulturalResource.query.filter_by(title=resource_data['title']).first()
            if not existing_resource:
                resource = CulturalResource(
                    title=resource_data['title'],
                    description=resource_data['description'],
                    category=resource_data['category'],
                    tags=','.join(resource_data['tags']),
                    author_id=admin_user.id if idx % 2 == 0 else sample_user.id
                )
                db.session.add(resource)
        
        db.session.commit()
        
        # 创建一些示例帖子
        sample_posts = [
            {
                'title': '分享我对湖湘文化的理解',
                'content': '湖湘文化源远流长，有着深厚的历史底蕴。从屈原到曾国藩，再到毛泽东，无数湖湘儿女为中华文化做出了杰出贡献。'
            },
            {
                'title': '岳麓书院游记',
                'content': '上周末参观了岳麓书院，感受到了浓厚的文化氛围。千年学府名不虚传，希望更多人能够了解和传承我们的文化瑰宝。'
            }
        ]
        
        for idx, post_data in enumerate(sample_posts):
            existing_post = Post.query.filter_by(title=post_data['title']).first()
            if not existing_post:
                post = Post(
                    title=post_data['title'],
                    content=post_data['content'],
                    author_id=sample_user.id
                )
                db.session.add(post)
        
        db.session.commit()
        
        print("示例数据已添加到数据库")

if __name__ == '__main__':
    init_database()