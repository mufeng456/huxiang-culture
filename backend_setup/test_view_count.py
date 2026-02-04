"""
测试浏览量功能
"""
import requests
import json

# 测试配置
BASE_URL = "http://localhost:5000/api"

def test_view_count():
    """
    测试浏览量功能
    """
    # 首先需要登录获取token
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        # 登录获取token
        login_response = requests.post(f"{BASE_URL}/login", json=login_data)
        if login_response.status_code != 200:
            print(f"登录失败: {login_response.status_code}, {login_response.text}")
            return
        
        login_result = login_response.json()
        token = login_result.get('access_token')
        
        if not token:
            print("未能获取到访问令牌")
            return
            
        print(f"登录成功，获取到令牌: {token[:10]}...")
        
        # 获取帖子列表
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        posts_response = requests.get(f"{BASE_URL}/posts", headers=headers)
        if posts_response.status_code != 200:
            print(f"获取帖子列表失败: {posts_response.status_code}, {posts_response.text}")
            return
            
        posts_data = posts_response.json()
        posts = posts_data.get('posts', [])
        
        if not posts:
            print("没有找到帖子")
            return
            
        # 选择第一个帖子进行浏览量测试
        post_id = posts[0]['id']
        post_title = posts[0]['title']
        initial_views = posts[0].get('views', 0)  # 使用get方法安全获取views字段
        
        print(f"选择帖子进行浏览量测试: ID {post_id}, 标题: {post_title}, 当前浏览量: {initial_views}")
        
        # 访问帖子详情（注意：这会增加浏览量，但需要是不同用户或非管理员）
        post_detail_response = requests.get(f"{BASE_URL}/posts/{post_id}", headers=headers)
        print(f"访问帖子详情状态: {post_detail_response.status_code}")
        
        if post_detail_response.status_code == 200:
            # 再次获取帖子列表，检查浏览量是否增加
            posts_response_after = requests.get(f"{BASE_URL}/posts", headers=headers)
            if posts_response_after.status_code == 200:
                posts_data_after = posts_response_after.json()
                posts_after = posts_data_after.get('posts', [])
                
                # 查找相同的帖子
                target_post_after = next((p for p in posts_after if p['id'] == post_id), None)
                if target_post_after:
                    final_views = target_post_after.get('views', 0)
                    print(f"访问后帖子实际浏览量: {final_views}")
                    
                    if final_views > initial_views:
                        print("✓ 浏览量功能工作正常")
                    else:
                        print("✗ 浏览量功能可能存在问题（可能是作者访问，所以没有增加）")
                else:
                    print("无法找到对应的帖子进行比较")
            else:
                print(f"获取帖子列表失败: {posts_response_after.status_code}")
        else:
            print(f"访问帖子详情失败: {post_detail_response.status_code}")
    
    except Exception as e:
        print(f"测试过程中发生错误: {e}")

if __name__ == "__main__":
    test_view_count()