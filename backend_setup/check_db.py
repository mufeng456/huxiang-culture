"""检查数据库中的帖子数据"""
import sqlite3
import json
from datetime import datetime

def check_posts():
    """检查SQLite数据库中的帖子"""
    db_path = './instance/huxiang_culture_dev.db'
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查posts表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print("数据库中存在的表:", [table[0] for table in tables])
        
        if 'posts' in [table[0] for table in tables]:
            # 查询所有帖子
            cursor.execute("SELECT * FROM posts ORDER BY created_at DESC;")
            posts = cursor.fetchall()
            
            print(f"\nposts表中共有 {len(posts)} 个帖子:")
            for post in posts:
                print(f"- ID: {post[0]}, 标题: {post[1][:30]}...")
                print(f"  内容: {post[2][:50]}...")
                print(f"  作者ID: {post[3]}, 创建时间: {post[4]}")
                print()
        else:
            print("\nposts 表不存在!")
        
        # 检查users表
        if 'users' in [table[0] for table in tables]:
            cursor.execute("SELECT * FROM users;")
            users = cursor.fetchall()
            print(f"users表中有 {len(users)} 个用户:")
            for user in users:
                print(f"- ID: {user[0]}, 用户名: {user[1]}, 邮箱: {user[2]}")
        
        conn.close()
        
    except Exception as e:
        print(f"数据库连接错误: {e}")

if __name__ == '__main__':
    check_posts()