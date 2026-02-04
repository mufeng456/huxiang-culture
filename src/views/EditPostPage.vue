<template>
  <div class="edit-post-page">
    <div class="container">
      <div class="edit-post-header">
        <h1>编辑帖子</h1>
        <p>修改您的帖子内容</p>
      </div>
      
      <form @submit.prevent="handleSubmit" class="edit-post-form">
        <div class="form-group">
          <label for="postTitle">标题 *</label>
          <input
            type="text"
            id="postTitle"
            v-model="post.title"
            placeholder="请输入帖子标题"
            required
            maxlength="200"
          />
        </div>
        
        <div class="form-group">
          <label for="postContent">内容 *</label>
          <textarea
            id="postContent"
            v-model="post.content"
            placeholder="请输入帖子内容，分享您对湖湘文化的见解..."
            required
            rows="10"
            maxlength="5000"
          ></textarea>
        </div>
        
        <div class="form-actions">
          <button type="button" @click="cancel" class="btn-cancel">取消</button>
          <button type="submit" class="btn-submit" :disabled="isSubmitting">
            {{ isSubmitting ? '更新中...' : '更新帖子' }}
          </button>
        </div>
        
        <div v-if="error" class="error-message">{{ error }}</div>
        <div v-if="successMessage" class="success-message">{{ successMessage }}</div>
      </form>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { request } from '../services/api.js'

export default {
  name: 'EditPostPage',
  setup() {
    const router = useRouter()
    const route = useRoute()
    
    const post = ref({
      title: '',
      content: ''
    })
    
    const postId = parseInt(route.params.id)
    const isSubmitting = ref(false)
    const error = ref('')
    const successMessage = ref('')
    
    // 获取帖子详情
    const fetchPostDetail = async () => {
      try {
        const response = await request(`/posts/${postId}`, 'GET')
        
        if (response.success) {
          post.value = {
            title: response.post.title,
            content: response.post.content
          }
        } else {
          throw new Error(response.message || '获取帖子详情失败')
        }
      } catch (err) {
        console.error('获取帖子详情错误:', err)
        error.value = err.message || '获取帖子详情失败'
        // 如果获取失败，返回社区页面
        setTimeout(() => {
          router.push('/community')
        }, 2000)
      }
    }
    
    const handleSubmit = async () => {
      try {
        error.value = ''
        isSubmitting.value = true
        
        // 检查用户是否已登录
        const token = localStorage.getItem('access_token')
        if (!token) {
          error.value = '请先登录后再更新帖子'
          return
        }
        
        const response = await request(`/posts/${postId}`, 'PUT', {
          title: post.value.title,
          content: post.value.content
        })
        
        if (response.success) {
          successMessage.value = '帖子更新成功！'
          
          // 2秒后跳转到帖子详情页面
          setTimeout(() => {
            router.push(`/post-detail/${postId}`)
          }, 2000)
        } else {
          error.value = response.message || '更新帖子失败'
        }
      } catch (err) {
        console.error('更新帖子错误:', err)
        error.value = err.message || '更新帖子失败，请稍后重试'
      } finally {
        isSubmitting.value = false
      }
    }
    
    const cancel = () => {
      router.go(-1) // 返回上一页
    }
    
    onMounted(() => {
      fetchPostDetail()
    })
    
    return {
      post,
      isSubmitting,
      error,
      successMessage,
      handleSubmit,
      cancel
    }
  }
}
</script>

<style scoped>
.edit-post-page {
  padding: 2rem 0;
  min-height: calc(100vh - 200px);
}

.container {
  max-width: 800px;
  margin: 0 auto;
  padding: 0 1rem;
}

.edit-post-header {
  text-align: center;
  margin-bottom: 2rem;
}

.edit-post-header h1 {
  font-size: 2rem;
  color: #333;
  margin-bottom: 0.5rem;
}

.edit-post-header p {
  color: #666;
  font-size: 1.1rem;
}

.edit-post-form {
  background: white;
  border-radius: 8px;
  padding: 2rem;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: bold;
  color: #333;
}

.form-group input,
.form-group textarea {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-family: inherit;
  font-size: 1rem;
  resize: vertical;
}

.form-group input:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #4a90e2;
  box-shadow: 0 0 0 2px rgba(74, 144, 226, 0.2);
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 2rem;
}

.btn-cancel,
.btn-submit {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
}

.btn-cancel {
  background: #f0f0f0;
  color: #333;
}

.btn-cancel:hover {
  background: #e0e0e0;
}

.btn-submit {
  background: #4a90e2;
  color: white;
}

.btn-submit:hover:not(:disabled) {
  background: #3a7bc8;
}

.btn-submit:disabled {
  background: #cccccc;
  cursor: not-allowed;
}

.error-message {
  margin-top: 1rem;
  padding: 0.75rem;
  background: #ffebee;
  color: #d32f2f;
  border-radius: 4px;
  border-left: 4px solid #d32f2f;
}

.success-message {
  margin-top: 1rem;
  padding: 0.75rem;
  background: #e8f5e9;
  color: #388e3c;
  border-radius: 4px;
  border-left: 4px solid #388e3c;
}
</style>