<template>
  <div class="create-post-page">
    <div class="container">
      <div class="create-post-header">
        <h1>发布新主题</h1>
        <p>分享您的想法，与社区成员交流湖湘文化</p>
      </div>
      
      <form @submit.prevent="handleSubmit" class="create-post-form">
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
          <label for="postCategory">分类 *</label>
          <select
            id="postCategory"
            v-model="post.category"
            required
          >
            <option value="" disabled>请选择分类</option>
            <option value="文化讨论">文化讨论</option>
            <option value="历史探索">历史探索</option>
            <option value="传统艺术">传统艺术</option>
            <option value="民俗风情">民俗风情</option>
            <option value="学术研究">学术研究</option>
            <option value="旅游攻略">旅游攻略</option>
            <option value="其他">其他</option>
          </select>
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
            {{ isSubmitting ? '发布中...' : '发布帖子' }}
          </button>
        </div>
        
        <div v-if="error" class="error-message">{{ error }}</div>
        <div v-if="successMessage" class="success-message">{{ successMessage }}</div>
      </form>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { request } from '../services/api.js'

export default {
  name: 'CreatePostPage',
  setup() {
    const router = useRouter()
    
    const post = ref({
      title: '',
      content: '',
      category: '文化讨论'  // 默认分类
    })
    
    const isSubmitting = ref(false)
    const error = ref('')
    const successMessage = ref('')
    
    const handleSubmit = async () => {
      try {
        error.value = ''
        isSubmitting.value = true
        
        // 检查用户是否已登录
        const token = localStorage.getItem('access_token')
        if (!token) {
          error.value = '请先登录后再发布帖子'
          return
        }
        
        // 使用全局API服务
        const response = await request('/posts', 'POST', {
          title: post.value.title,
          content: post.value.content,
          category: post.value.category  // 添加分类
        })
        
        if (response.success) {
          successMessage.value = '帖子发布成功！'
          
          // 触发帖子更新事件，通知社区页面刷新
          console.log('触发postCreated事件:', response.post);
          window.dispatchEvent(new CustomEvent('postCreated', { detail: response.post }));
          
          // 重置表单
          post.value = {
            title: '',
            content: '',
            category: '文化讨论'
          }
          
          // 3秒后跳转到社区页面
          setTimeout(() => {
            router.push('/community')
          }, 3000)
        } else {
          error.value = response.message || '发布帖子失败'
        }
      } catch (err) {
        console.error('发布帖子错误:', err)
        // 特别处理认证相关的错误
        if (err.message.includes('认证错误') || err.message.includes('需要登录') || 
            err.message.includes('401') || err.message.includes('未登录') || 
            err.message.toLowerCase().includes('token') || 
            err.message.toLowerCase().includes('unauthorized')) {
          error.value = '登录状态已失效，请重新登录'
          // 跳转到登录页面
          setTimeout(() => {
            router.push('/login')
          }, 2000)
        } else if (err.message.includes('网络连接失败')) {
          error.value = '无法连接到服务器，请确保后端服务正在运行'
        } else {
          // 更具体地处理错误消息
          error.value = err.message || '发布帖子失败，请稍后重试'
        }
      } finally {
        isSubmitting.value = false
      }
    }
    
    const cancel = () => {
      router.go(-1) // 返回上一页
    }
    
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
.create-post-page {
  padding: 2rem 0;
  min-height: calc(100vh - 200px);
}

.container {
  max-width: 800px;
  margin: 0 auto;
  padding: 0 1rem;
}

.create-post-header {
  text-align: center;
  margin-bottom: 2rem;
}

.create-post-header h1 {
  font-size: 2rem;
  color: #333;
  margin-bottom: 0.5rem;
}

.create-post-header p {
  color: #666;
  font-size: 1.1rem;
}

.create-post-form {
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