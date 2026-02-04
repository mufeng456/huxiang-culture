"""
验证数据库结构和数据
"""
import os
import sys
import sqlite3

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def verify_db_structure():
    """验证数据库结构"""
    db_path = './instance/huxiang_culture_dev.db'
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查posts表结构
        cursor.execute("PRAGMA table_info(posts);")
        columns = cursor.fetchall()
        print("posts表结构:")
        for col in columns:
            print(f"  {col[1]} - {col[2]} - 默认值: {col[4]}")
        
        print("\nposts表中的所有帖子:")
        cursor.execute("SELECT id, title, content, author_id, category FROM posts ORDER BY id;")
        posts = cursor.fetchall()
        for post in posts:
            print(f"  ID: {post[0]}, 分类: {post[4]}, 标题: {post[1][:30]}...")
        
        conn.close()
        print("\n数据库结构验证完成")
        
    except Exception as e:
        print(f"数据库连接错误: {e}")

if __name__ == '__main__':
    verify_db_structure()