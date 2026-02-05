<template>
  <div class="post-detail-page">
    <!-- 返回按钮 -->
    <div class="back-button-container">
      <button class="back-button" @click="goBack">
        <i class="fas fa-arrow-left"></i> 返回社区
      </button>
    </div>

    <!-- 主要内容 -->
    <div class="container">
      <!-- 帖子详情 -->
      <div class="post-detail" v-if="!loading && currentPost">
        <!-- 帖子头部 -->
        <div class="post-header">
          <div class="post-author">
            <img :src="currentPost?.author?.avatar || '/api/placeholder/40/40'" alt="Author avatar" class="author-avatar" loading="lazy" />
            <div class="author-info">
              <span class="author-name">{{ currentPost?.author?.username }}</span>
              <span class="post-date">{{ formatDate(currentPost?.created_at) }}</span>
            </div>
          </div>
          <div class="post-stats">
            <span class="stat-item"><i class="far fa-eye"></i> {{ currentPost?.views || 0 }} 浏览</span>
            <span class="stat-item"><i class="far fa-comment"></i> <i class="comment-count-loading" v-if="commentsLoading">加载中...</i><span class="comment-count" v-else>{{ commentCount }}</span></span>
            <button @click="toggleLike" class="like-btn" :class="{ liked: isLiked }">
              <i class="far fa-thumbs-up" :class="{ 'fas': isLiked }"></i>
              <span>{{ currentPost?.likes_count || 0 }} 点赞</span>
            </button>
          </div>
        </div>
        
        <!-- 帖子内容 -->
        <div class="post-content">
          <div class="post-meta">
            <span class="post-category">{{ currentPost?.category || '文化讨论' }}</span>
          </div>
          <h1 class="post-title">{{ currentPost?.title }}</h1>
          <div class="post-body" v-html="formatPostContent(currentPost?.content)"></div>
          <div class="post-actions" v-if="canEditDelete">
            <button class="action-btn" @click="editPost">
              <i class="far fa-edit"></i>
              <span>编辑</span>
            </button>
            <button class="action-btn delete-btn" @click="deletePost">
              <i class="far fa-trash-alt"></i>
              <span>删除</span>
            </button>
          </div>
        </div>
        
        <!-- 评论区 -->
        <CommentsSection :post-id="postId" />
      </div>
      
      <!-- 加载状态 -->
      <div v-else-if="loading" class="loading">
        正在加载帖子详情...
      </div>
      
      <!-- 错误状态 -->
      <div v-else-if="error" class="error">
        {{ error }}
      </div>
      
      <!-- 空数据状态 -->
      <div v-else class="empty-state">
        找不到帖子信息
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import CommentsSection from '../components/CommentsSection.vue'
import { request } from '../services/api.js'

export default {
  name: 'PostDetailPage',
  components: {
    CommentsSection
  },
  setup() {
    const router = useRouter()
    const route = useRoute()
    
    const currentPost = ref(null)
    const loading = ref(true)
    const error = ref('')
    const postId = parseInt(route.params.id)
    const commentCount = ref(0)
    const commentsLoading = ref(false)
    const isLiked = ref(false)  // 新增：记录是否已点赞
    
    // 检查当前用户是否已点赞此帖子
    const checkIfLiked = () => {
      const likedPosts = JSON.parse(localStorage.getItem('liked_posts') || '[]');
      return likedPosts.includes(postId);
    }
    
    // 更新点赞状态
    const updateLikeStatus = () => {
      isLiked.value = checkIfLiked();
    }
    
    // 监听storage变化，以便在其他标签页中点赞后能同步状态
    const handleStorageChange = () => {
      updateLikeStatus();
    };
    
    // 初始化时检查是否已点赞
    onMounted(() => {
      fetchPostDetail()
      // 添加延时确保数据加载完成后再检查点赞状态
      setTimeout(updateLikeStatus, 100);
      
      // 监听storage变化
      window.addEventListener('storage', handleStorageChange);
    });
    
    // 组件卸载时移除事件监听
    onUnmounted(() => {
      window.removeEventListener('storage', handleStorageChange);
    });
    
    // 检查当前用户是否为帖子作者或管理员
    const canEditDelete = computed(() => {
      if (!currentPost.value || !localStorage.getItem('user')) return false
      
      const currentUser = JSON.parse(localStorage.getItem('user'))
      return (
        currentPost.value.author_id === currentUser.id || 
        currentUser.is_admin
      )
    })
    
    // 点赞/取消点赞帖子
    const toggleLike = async () => {
      if (!localStorage.getItem('access_token')) {
        alert('请先登录后再点赞')
        return
      }
      
      if (isLiked.value) {
        alert('您已经点过赞了')
        return
      }
      
      try {
        console.log('开始发送点赞请求...')
        const response = await request(`/posts/${postId}/like`, 'POST')
        console.log('点赞API响应:', response)
        
        if (response.success) {
          // 更新点赞数
          if (currentPost.value) {
            currentPost.value.likes_count = response.likes_count
            console.log('更新后的点赞数:', response.likes_count)
          }
          isLiked.value = true
          
          // 存储已点赞的帖子ID
          const likedPosts = JSON.parse(localStorage.getItem('liked_posts') || '[]');
          likedPosts.push(postId);
          localStorage.setItem('liked_posts', JSON.stringify(likedPosts))
          
          // 更新点赞按钮的状态
          const likeBtn = document.querySelector('.like-btn');
          if (likeBtn) {
            likeBtn.classList.add('liked');
          }
          
          // 显示成功消息
          alert('点赞成功！');
        } else {
          console.error('点赞失败:', response.message)
          if(response.message === '您已经点过赞了') {
            alert(response.message)
            isLiked.value = true; // 确保状态更新
          } else {
            alert(response.message || '点赞失败')
          }
        }
      } catch (error) {
        console.error('点赞请求失败:', error)
        if (error.message.includes('401') || error.message.includes('认证') || error.message.includes('登录')) {
          alert('登录已过期，请重新登录')
          // 触发登出事件
          window.dispatchEvent(new Event('logout'));
        } else {
          alert(error.message || '点赞失败')
        }
      }
    }
    
    // 获取帖子详情
    const fetchPostDetail = async () => {
      try {
        error.value = ''
        
        // 检查用户是否已登录
        const token = localStorage.getItem('access_token')
        if (!token) {
          error.value = '请先登录后再查看帖子详情'
          return
        }
        
        console.log(`尝试获取帖子详情，ID: ${postId}`); // 添加调试信息
        
        const response = await request(`/posts/${postId}`, 'GET')
        
        console.log(`API响应:`, response); // 添加调试信息
        
        if (response && response.post) {
          currentPost.value = response.post
          console.log(`成功获取帖子:`, response.post.title) // 添加调试信息
        } else {
          // 检查是否是认证相关错误
          if (response && response.error && (response.error.includes('认证') || response.error.includes('令牌') || response.error.includes('token') || response.error.includes('401') || response.error.includes('Unauthorized'))) {
            error.value = '登录已过期，请重新登录'
            // 清除过期的令牌
            localStorage.removeItem('access_token')
            localStorage.removeItem('user')
          } else {
            throw new Error(response?.message || response?.error || '获取帖子详情失败')
          }
        }
      } catch (err) {
        console.error('获取帖子详情错误:', err)
        // 检查错误是否与认证有关
        if (err.message.includes('401') || err.message.toLowerCase().includes('unauthorized') || err.message.includes('认证') || err.message.includes('令牌') || err.message.includes('token')) {
          error.value = '登录已过期，请重新登录'
          // 清除过期的令牌
          localStorage.removeItem('access_token')
          localStorage.removeItem('user')
        } else if (err.message.includes('404')) {
          error.value = '帖子不存在'
        } else {
          error.value = err.message || '获取帖子详情失败'
        }
      } finally {
        loading.value = false
      }
    }
    
    // 获取评论数量
    const fetchCommentCount = async () => {
      try {
        commentsLoading.value = true
        const response = await request(`/comments?post_id=${postId}`, 'GET')
        
        if (response.comments) {
          commentCount.value = response.comments.length
        }
      } catch (err) {
        console.error('获取评论数错误:', err)
        commentCount.value = 0
      } finally {
        commentsLoading.value = false
      }
    }
    
    // 编辑帖子
    const editPost = () => {
      router.push(`/edit-post/${postId}`)
    }
    
    // 删除帖子
    const deletePost = async () => {
      if (!confirm('确定要删除这个帖子吗？此操作不可撤销。')) {
        return
      }
      
      try {
        const token = localStorage.getItem('access_token')
        if (!token) {
          error.value = '请先登录'
          return
        }

        // 获取当前用户信息用于调试
        const currentUser = JSON.parse(localStorage.getItem('user') || '{}');
        console.log('当前用户信息:', currentUser);
        console.log('当前帖子作者ID:', currentPost.value?.author_id);
        console.log('是否为管理员:', currentUser.is_admin);

        const response = await request(`/posts/${postId}`, 'DELETE')  // 这里的路径是正确的，因为request函数会自动添加/api前缀
        
        console.log('删除帖子响应:', response);
        
        if (response.success) {
          alert('帖子删除成功')
          router.push('/community')
        } else {
          throw new Error(response.message || '删除帖子失败')
        }
      } catch (err) {
        console.error('删除帖子错误:', err)
        alert(err.message || '删除帖子失败')
      }
    }
    
    // 格式化日期
    const formatDate = (dateString) => {
      const date = new Date(dateString)
      return date.toLocaleDateString('zh-CN', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    }
    
    // 格式化帖子内容
    const formatPostContent = (content) => {
      if (!content) return ''
      // 简单的内容格式化，换行转为<br>
      return content.replace(/\n/g, '<br>')
    }
    
    // 返回上一页
    const goBack = () => {
      router.go(-1)
    }
    
    onMounted(() => {
      fetchPostDetail()
      fetchCommentCount()
    })
    
    return {
      currentPost,
      loading,
      error,
      postId,
      commentCount,
      commentsLoading,
      canEditDelete,
      editPost,
      deletePost,
      formatDate,
      formatPostContent,
      goBack,
      toggleLike,  // 添加点赞功能到暴露的函数列表
      isLiked  // 添加点赞状态到暴露的变量列表
    }
  }
}
</script>

<style scoped>
.post-detail-page {
  padding: 2rem 0;
  min-height: calc(100vh - 200px);
}

.container {
  max-width: 1400px; /* 增加宽度 */
  margin: 0 auto;
  padding: 0 1rem;
}

.back-button-container {
  margin-bottom: 1rem;
}

.back-button {
  background: #f8f9fa;
  border: 1px solid #dee2e6;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}

.back-button:hover {
  background: #e9ecef;
}

.post-detail {
  background: white;
  border-radius: 8px;
  padding: 2rem;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.post-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 1rem;
  border-bottom: 1px solid #eee;
  margin-bottom: 1.5rem;
}

.post-author {
  display: flex;
  align-items: center;
}

.author-avatar {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  margin-right: 1rem;
  object-fit: cover;
}

.author-info {
  display: flex;
  flex-direction: column;
}

.author-name {
  font-weight: bold;
  color: #333;
  margin-bottom: 0.25rem;
}

.post-date {
  color: #666;
  font-size: 0.9rem;
}

.post-stats {
  display: flex;
  gap: 1.5rem;
  color: #666;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.post-content {
  margin-bottom: 2rem;
}

.post-title {
  font-size: 1.8rem;
  color: #333;
  margin-bottom: 1rem;
}

.post-body {
  color: #555;
  line-height: 1.8;
  margin-bottom: 1.5rem;
}

.post-actions {
  display: flex;
  gap: 1rem;
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid #eee;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border: 1px solid #ddd;
  background: white;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
}

.action-btn:hover {
  background: #f8f9fa;
}

.delete-btn {
  background: #f8d7da;
  color: #721c24;
  border-color: #f5c6cb;
}

.delete-btn:hover {
  background: #f5c6cb;
}

.post-stats-detail {
  display: flex;
  gap: 1.5rem;
  align-items: center;
  margin: 1rem 0;
  padding: 0.75rem;
  background: #f8f9fa;
  border-radius: 8px;
}

.like-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: none;
  border: none;
  color: #666;
  cursor: pointer;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  transition: all 0.3s;
}

.like-btn:hover {
  background: #e9ecef;
  color: #007bff;
}

.like-btn.liked {
  color: #007bff;
}

.loading {
  text-align: center;
  padding: 3rem;
  font-size: 1.2rem;
  color: #666;
}

.error {
  text-align: center;
  padding: 3rem;
  font-size: 1.2rem;
  color: #d32f2f;
  background: #ffebee;
  border-radius: 8px;
  margin: 1rem 0;
}

.post-meta {
  margin-bottom: 1rem;
}

.post-category {
  background: linear-gradient(135deg, #6a11cb 0%, #2575fc 100%);
  color: white;
  padding: 0.4rem 1rem;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 600;
  display: inline-block;
  box-shadow: 0 2px 8px rgba(106, 17, 203, 0.4);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  transition: all 0.3s ease;
}

.post-category:hover {
  transform: scale(1.05);
  box-shadow: 0 4px 12px rgba(106, 17, 203, 0.6);
}

.empty-state {
  text-align: center;
  padding: 3rem;
  font-size: 1.2rem;
  color: #666;
  background: #f8f9fa;
  border-radius: 8px;
  margin: 1rem 0;
}

.comment-count-loading {
  color: #666;
  font-style: italic;
}
</style>