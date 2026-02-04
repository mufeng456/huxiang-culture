<template>
  <div class="comments-section">
    <div class="comments-header">
      <h3>评论 ({{ comments.length }})</h3>
    </div>
    
    <div class="comment-form">
      <textarea
        v-model="newComment"
        placeholder="写下你的评论..."
        rows="4"
        maxlength="500"
      ></textarea>
      <div class="comment-actions">
        <button @click="submitComment" :disabled="!newComment.trim()" class="submit-btn">
          发表评论
        </button>
      </div>
    </div>
    
    <div v-if="loading" class="loading">加载评论中...</div>
    
    <div v-else-if="comments.length === 0" class="no-comments">
      暂无评论，快来发表第一个评论吧！
    </div>
    
    <div v-else class="comments-list">
      <div v-for="comment in comments" :key="comment.id" class="comment-item">
        <div class="comment-author">
          <img :src="comment.author.avatar || '/api/placeholder/40/40'" alt="头像" class="avatar" />
          <div class="author-info">
            <div class="author-name">{{ comment.author.username }}</div>
            <div class="comment-date">{{ formatDate(comment.created_at) }}</div>
          </div>
        </div>
        <div class="comment-content">{{ comment.content }}</div>
      </div>
    </div>
    
    <div v-if="error" class="error-message">{{ error }}</div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { request } from '../services/api.js'

export default {
  name: 'CommentsSection',
  props: {
    postId: {
      type: Number,
      required: true
    }
  },
  setup(props) {
    const comments = ref([])
    const newComment = ref('')
    const loading = ref(false)
    const error = ref('')
    
    const fetchComments = async () => {
      try {
        loading.value = true
        error.value = ''
        
        const response = await request(`/comments?post_id=${props.postId}`, 'GET')
        comments.value = response.comments || []
      } catch (err) {
        console.error('获取评论失败:', err)
        error.value = err.message || '获取评论失败'
      } finally {
        loading.value = false
      }
    }
    
    const submitComment = async () => {
      if (!newComment.value.trim()) return
      
      try {
        const token = localStorage.getItem('access_token')
        if (!token) {
          error.value = '请先登录后再发表评论'
          return
        }
        
        // 检查令牌是否有效
        if (!isTokenValid(token)) {
          error.value = '登录已过期，请重新登录'
          // 触发登出事件
          window.dispatchEvent(new Event('logout'));
          return
        }
        
        const response = await request('/comments', 'POST', {
          content: newComment.value.trim(),
          post_id: props.postId
        })
        
        if (response.success) {
          // 添加新评论到列表顶部
          comments.value.unshift(response.comment)
          newComment.value = '' // 清空输入框
          error.value = '' // 清除错误消息
        } else {
          error.value = response.message || '发表评论失败'
        }
      } catch (err) {
        console.error('发表评论失败:', err)
        // 更精确地检查错误是否与认证有关
        const errorMessage = err.message.toLowerCase();
        const isAuthError = errorMessage.includes('401') || 
                           errorMessage.includes('认证') || 
                           errorMessage.includes('登录') || 
                           errorMessage.includes('token') || 
                           errorMessage.includes('unauthorized') ||
                           errorMessage.includes('过期') ||
                           errorMessage.includes('expired') ||
                           errorMessage.includes('need login') ||
                           errorMessage.includes('missing') ||
                           errorMessage.includes('invalid');
        
        if (isAuthError) {
          error.value = '登录状态已失效，请重新登录'
          // 触发登出事件
          window.dispatchEvent(new Event('logout'));
        } else {
          error.value = err.message || '发表评论失败'
        }
      }
    }
    
    // 验证JWT令牌是否有效
    const isTokenValid = (token) => {
      if (!token) return false;
      
      try {
        // 解析JWT令牌，检查是否过期
        const payload = JSON.parse(atob(token.split('.')[1]));
        const now = Math.floor(Date.now() / 1000);
        // 提前1分钟提醒过期，避免时间差问题
        return payload.exp > (now + 60);
      } catch (e) {
        console.error('令牌验证错误:', e);
        return false;
      }
    }
    
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
    
    onMounted(() => {
      fetchComments()
    })
    
    return {
      comments,
      newComment,
      loading,
      error,
      submitComment,
      formatDate
    }
  }
}
</script>

<style scoped>
.comments-section {
  margin-top: 2rem;
}

.comments-header {
  border-bottom: 2px solid #eee;
  padding-bottom: 0.5rem;
  margin-bottom: 1.5rem;
}

.comments-header h3 {
  color: #333;
  font-size: 1.3rem;
}

.comment-form {
  margin-bottom: 2rem;
}

.comment-form textarea {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-family: inherit;
  font-size: 1rem;
  resize: vertical;
  margin-bottom: 0.5rem;
}

.comment-form textarea:focus {
  outline: none;
  border-color: #4a90e2;
  box-shadow: 0 0 0 2px rgba(74, 144, 226, 0.2);
}

.comment-actions {
  text-align: right;
}

.submit-btn {
  padding: 0.5rem 1rem;
  background: #4a90e2;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.submit-btn:disabled {
  background: #cccccc;
  cursor: not-allowed;
}

.loading {
  text-align: center;
  padding: 1rem;
  color: #666;
}

.no-comments {
  text-align: center;
  padding: 2rem;
  color: #999;
  font-style: italic;
}

.comments-list {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.comment-item {
  padding: 1rem;
  border: 1px solid #eee;
  border-radius: 6px;
  background: #fafafa;
}

.comment-author {
  display: flex;
  align-items: center;
  margin-bottom: 0.5rem;
}

.avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  margin-right: 0.75rem;
  background: #ddd;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
}

.author-info {
  flex: 1;
}

.author-name {
  font-weight: bold;
  color: #333;
}

.comment-date {
  font-size: 0.85rem;
  color: #999;
}

.comment-content {
  color: #555;
  line-height: 1.6;
}

.error-message {
  margin-top: 1rem;
  padding: 0.75rem;
  background: #ffebee;
  color: #d32f2f;
  border-radius: 4px;
  border-left: 4px solid #d32f2f;
}
</style>