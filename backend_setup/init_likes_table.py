"""
初始化点赞表
"""
from app import create_app, db
from app import Like  # 导入Like模型以确保表被创建

def init_likes_table():
    """初始化点赞表"""
    app = create_app()
    
    with app.app_context():
        # 创建所有未创建的表
        db.create_all()
        print("数据库表初始化完成！")

if __name__ == '__main__':
    init_likes_table()