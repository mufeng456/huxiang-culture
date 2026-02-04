"""
修复数据库结构，确保posts表包含category列
"""
import os
import sys
import sqlite3

def fix_database():
    """修复数据库结构"""
    db_path = './instance/huxiang_culture_dev.db'
    
    # 确保instance目录存在
    os.makedirs('./instance', exist_ok=True)
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查posts表结构
        cursor.execute("PRAGMA table_info(posts);")
        columns = [col[1] for col in cursor.fetchall()]
        print(f"当前posts表列: {columns}")
        
        # 如果category列不存在，则添加
        if 'category' not in columns:
            print("正在添加category列...")
            
            # 创建新表结构
            cursor.execute("""
                ALTER TABLE posts ADD COLUMN category VARCHAR(100) DEFAULT '文化讨论';
            """)
            
            conn.commit()
            print("category列添加成功！")
        else:
            print("category列已存在")
        
        # 验证修改
        cursor.execute("PRAGMA table_info(posts);")
        updated_cols = [col[1] for col in cursor.fetchall()]
        print(f"更新后posts表列: {updated_cols}")
        
        # 验证数据
        cursor.execute("SELECT COUNT(*) FROM posts;")
        count = cursor.fetchone()[0]
        print(f"posts表中总计: {count} 条记录")
        
        conn.close()
        print("数据库修复完成！")
        
    except Exception as e:
        print(f"数据库修复过程中出错: {e}")
        # 如果ALTER TABLE失败，尝试完整的重建方案
        recreate_table_with_category(db_path)

def recreate_table_with_category(db_path):
    """通过重建表来添加category列"""
    print("尝试通过重建表来修复数据库...")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 获取现有数据
        cursor.execute("SELECT id, title, content, created_at, author_id, likes_count FROM posts;")
        existing_data = cursor.fetchall()
        
        # 删除原表
        cursor.execute("DROP TABLE posts;")
        
        # 创建新表，包含category列
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
        
        # 插入原有数据
        for row in existing_data:
            cursor.execute("""
                INSERT INTO posts (id, title, content, created_at, author_id, likes_count, category)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (row[0], row[1], row[2], row[3], row[4], row[5], '文化讨论'))
        
        conn.commit()
        conn.close()
        
        print("表重建完成！")
    except Exception as e:
        print(f"表重建失败: {e}")

if __name__ == '__main__':
    fix_database()