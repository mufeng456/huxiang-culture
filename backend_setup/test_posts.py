"""测试数据库中的帖子数据"""
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db, Post

def test_posts():
    """测试帖子数据"""
    app = create_app()
    
    with app.app_context():
        # 查询所有帖子
        posts = Post.query.all()
        print(f"数据库中共有 {len(posts)} 个帖子:")
        
        for post in posts:
            print(f"- ID: {post.id}, 标题: {post.title}, 作者ID: {post.author_id}")
            print(f"  内容: {post.content[:50]}...")
            print(f"  创建时间: {post.created_at}")
            print()

if __name__ == '__main__':
    test_posts()