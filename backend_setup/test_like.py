"""
测试点赞功能
"""
import requests
import json

# 测试配置
BASE_URL = "http://localhost:5000/api"

def test_like_function():
    """
    测试点赞功能
    """
    # 首先需要登录获取token
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        # 登录获取token
        login_response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
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
            
        # 选择第一个帖子进行点赞测试
        post_id = posts[0]['id']
        post_title = posts[0]['title']
        initial_likes = posts[0]['likes_count']
        
        print(f"选择帖子进行点赞测试: ID {post_id}, 标题: {post_title}, 当前点赞数: {initial_likes}")
        
        # 点赞
        like_response = requests.post(f"{BASE_URL}/posts/{post_id}/like", headers=headers)
        print(f"点赞请求状态: {like_response.status_code}")
        print(f"点赞响应内容: {like_response.text}")
        
        if like_response.status_code == 200:
            like_result = like_response.json()
            if like_result.get('success'):
                print(f"点赞成功！新的点赞数: {like_result.get('likes_count')}")
            else:
                print(f"点赞失败: {like_result.get('message', '未知错误')}")
        else:
            print(f"点赞请求失败: {like_response.status_code}")
        
        # 再次获取帖子详情，验证点赞数是否真的增加了
        post_detail_response = requests.get(f"{BASE_URL}/posts/{post_id}", headers=headers)
        if post_detail_response.status_code == 200:
            post_detail = post_detail_response.json()
            final_likes = post_detail['post']['likes_count']
            print(f"点赞后帖子实际点赞数: {final_likes}")
            
            if final_likes > initial_likes:
                print("✓ 点赞功能工作正常")
            else:
                print("✗ 点赞功能可能存在问题")
        else:
            print(f"获取帖子详情失败: {post_detail_response.status_code}")
    
    except Exception as e:
        print(f"测试过程中发生错误: {e}")

if __name__ == "__main__":
    test_like_function()