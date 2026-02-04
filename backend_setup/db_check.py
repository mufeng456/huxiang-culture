import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import db, User, create_app

def check_users():
    app = create_app()
    
    with app.app_context():
        # 查询所有用户
        users = User.query.all()
        
        print("数据库中存在的用户:")
        for user in users:
            print(f"- ID: {user.id}, Username: {user.username}, Email: {user.email}, Is Admin: {user.is_admin}")
        
        # 特别检查admin用户
        admin_user = User.query.filter_by(username='admin').first()
        if admin_user:
            print(f"\n找到管理员账户:")
            print(f"- Username: {admin_user.username}")
            print(f"- Email: {admin_user.email}")
            print(f"- Is Admin: {admin_user.is_admin}")
        else:
            print("\n警告: 未找到管理员账户 'admin'")
            
if __name__ == '__main__':
    check_users()