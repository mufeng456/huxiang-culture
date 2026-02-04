"""
为数据库添加likes表
"""
import os
import sys
import sqlite3

def add_likes_table():
    """为数据库添加likes表"""
    db_path = './instance/huxiang_culture_dev.db'
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查likes表是否已存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='likes';")
        table_exists = cursor.fetchone()
        
        if not table_exists:
            print("正在创建likes表...")
            
            # 创建likes表
            cursor.execute("""
                CREATE TABLE likes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    post_id INTEGER NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(user_id, post_id)
                );
            """)
            
            conn.commit()
            print("likes表创建成功！")
        else:
            print("likes表已存在")
        
        # 验证创建
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"数据库中所有表: {tables}")
        
        conn.close()
        print("数据库更新完成！")
        
    except Exception as e:
        print(f"数据库更新过程中出错: {e}")

if __name__ == '__main__':
    add_likes_table()