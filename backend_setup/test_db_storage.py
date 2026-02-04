"""
测试数据库存储功能
验证帖子是否正确保存到数据库
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db, Post, User

def test_db_storage():
    """测试数据库存储功能"""
    app = create_app()
    
    with app.app_context():
        # 获取所有帖子
        all_posts = Post.query.all()
        print(f"数据库中帖子总数: {len(all_posts)}")
        
        if all_posts:
            print("\n所有帖子列表:")
            for post in all_posts:
                print(f"- ID: {post.id}, 标题: {post.title}")
                print(f"  作者ID: {post.author_id}")
                print(f"  内容预览: {post.content[:50]}...")
                print(f"  创建时间: {post.created_at}")
                print(f"  点赞数: {post.likes_count}")
                
                # 尝试获取作者信息
                author = User.query.get(post.author_id)
                if author:
                    print(f"  作者用户名: {author.username}")
                else:
                    print(f"  作者信息: 未找到 (ID: {post.author_id})")
                print("-" * 50)
        else:
            print("数据库中没有帖子")
        
        # 测试创建一个新帖子
        print("\n测试创建新帖子...")
        try:
            # 获取第一个用户作为作者
            first_user = User.query.first()
            if first_user:
                print(f"使用用户: {first_user.username} (ID: {first_user.id}) 创建帖子")
                
                new_post = Post(
                    title="测试帖子",
                    content="这是一个用于测试的帖子，验证数据库存储功能。",
                    author_id=first_user.id
                )
                
                db.session.add(new_post)
                db.session.commit()
                
                print(f"帖子创建成功，ID: {new_post.id}")
                
                # 立即查询刚创建的帖子
                saved_post = Post.query.get(new_post.id)
                if saved_post:
                    print(f"验证帖子已保存: {saved_post.title}")
                else:
                    print("错误: 帖子未正确保存到数据库")
                    
            else:
                print("错误: 数据库中没有可用用户")
                
        except Exception as e:
            print(f"创建帖子时出错: {str(e)}")
            db.session.rollback()

if __name__ == '__main__':
    test_db_storage()