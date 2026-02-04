"""
为posts表添加views列
"""
import os
import sys
import sqlite3

def add_views_column():
    """为posts表添加views列"""
    db_path = './instance/huxiang_culture_dev.db'
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查views列是否已存在
        cursor.execute("PRAGMA table_info(posts);")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'views' not in columns:
            print("正在为posts表添加views列...")
            
            # 添加views列
            cursor.execute("""
                ALTER TABLE posts ADD COLUMN views INTEGER DEFAULT 0;
            """)
            
            conn.commit()
            print("views列添加成功！")
        else:
            print("views列已存在")
        
        # 验证修改
        cursor.execute("PRAGMA table_info(posts);")
        updated_cols = [col[1] for col in cursor.fetchall()]
        print(f"更新后posts表列: {updated_cols}")
        
        conn.close()
        print("数据库更新完成！")
        
    except Exception as e:
        print(f"数据库更新过程中出错: {e}")

if __name__ == '__main__':
    add_views_column()