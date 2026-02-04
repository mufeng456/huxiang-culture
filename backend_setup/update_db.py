"""
更新数据库结构，为posts表添加category列
"""
import os
import sys
import sqlite3

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db

def update_database_schema():
    """更新数据库结构"""
    app = create_app()
    
    with app.app_context():
        # 获取当前数据库路径
        db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
        
        # 连接到SQLite数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查posts表结构
        cursor.execute("PRAGMA table_info(posts);")
        columns = [column[1] for column in cursor.fetchall()]
        print(f"当前posts表的列: {columns}")
        
        # 如果category列不存在，则添加它
        if 'category' not in columns:
            print("正在为posts表添加category列...")
            
            # 由于SQLite不支持直接添加带默认值的列，我们需要重建表
            # 首先备份现有数据
            cursor.execute("""
                CREATE TABLE posts_backup AS 
                SELECT id, title, content, created_at, author_id, likes_count 
                FROM posts;
            """)
            
            # 删除原posts表
            cursor.execute("DROP TABLE posts;")
            
            # 重新创建posts表，包含category列
            cursor.execute("""
                CREATE TABLE posts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title VARCHAR(200) NOT NULL,
                    content TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    author_id INTEGER NOT NULL,
                    likes_count INTEGER DEFAULT 0,
                    category VARCHAR(100) DEFAULT '文化讨论',
                    FOREIGN KEY(author_id) REFERENCES users (id)
                );
            """)
            
            # 将数据从备份表迁移回来
            cursor.execute("""
                INSERT INTO posts (id, title, content, created_at, author_id, likes_count)
                SELECT id, title, content, created_at, author_id, likes_count 
                FROM posts_backup;
            """)
            
            # 更新category列的默认值
            cursor.execute("UPDATE posts SET category = '文化讨论' WHERE category IS NULL;")
            
            # 删除备份表
            cursor.execute("DROP TABLE posts_backup;")
            
            conn.commit()
            print("数据库结构更新完成！")
        else:
            print("category列已存在，无需更新。")
        
        # 验证更新
        cursor.execute("PRAGMA table_info(posts);")
        updated_columns = [column[1] for column in cursor.fetchall()]
        print(f"更新后posts表的列: {updated_columns}")
        
        conn.close()

if __name__ == '__main__':
    update_database_schema()