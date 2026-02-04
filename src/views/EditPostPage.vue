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
        
        <div class="form-group">
          <label for="postCategory">分类</label>
          <select id="postCategory" v-model="post.category">
            <option value="文化讨论">文化讨论</option>
            <option value="历史探索">历史探索</option>
            <option value="艺术欣赏">艺术欣赏</option>
            <option value="民俗风情">民俗风情</option>
            <option value="饮食文化">饮食文化</option>
            <option value="建筑风格">建筑风格</option>
            <option value="文学作品">文学作品</option>
            <option value="传统工艺">传统工艺</option>
          </select>
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
      content: '',
      category: ''  // 添加分类字段
    })
    
    const postId = parseInt(route.params.id)
    const isSubmitting = ref(false)
    const error = ref('')
    const successMessage = ref('')
    
    // 获取帖子详情
    const fetchPostDetail = async () => {
      try {
        console.log('正在获取帖子详情，帖子ID:', postId);
        
        // 首先检查认证状态
        const token = localStorage.getItem('access_token');
        if (!token) {
          error.value = '请先登录后再编辑帖子';
          console.error('访问令牌不存在');
          setTimeout(() => {
            router.push('/login');
          }, 2000);
          return;
        }
        
        // 验证令牌是否有效
        try {
          const payload = JSON.parse(atob(token.split('.')[1]));
          const now = Math.floor(Date.now() / 1000);
          if (payload.exp < now) {
            error.value = '登录已过期，请重新登录';
            console.error('令牌已过期');
            localStorage.removeItem('access_token');
            localStorage.removeItem('user');
            setTimeout(() => {
              router.push('/login');
            }, 2000);
            return;
          }
          console.log('JWT令牌有效，剩余时间:', payload.exp - now, '秒');
        } catch (e) {
          console.error('令牌解析错误:', e);
          error.value = '登录凭证异常，请重新登录';
          localStorage.removeItem('access_token');
          localStorage.removeItem('user');
          setTimeout(() => {
            router.push('/login');
          }, 2000);
          return;
        }
        
        console.log('开始请求帖子详情，URL:', `/posts/${postId}`);
        // 在发送请求前添加额外的日志
        console.log('准备发送API请求到:', `/posts/${postId}`);
        console.log('使用的方法:', 'GET');
        console.log('当前token:', token.substring(0, 20) + '...');
        
        // 尝试直接调用API而不依赖封装的request函数，用于调试
        try {
          const response = await request(`/posts/${postId}`, 'GET');
          console.log('帖子详情响应:', response);
          
          if (response && typeof response === 'object') {
            if (response.success) {
              post.value = {
                title: response.post.title,
                content: response.post.content,
                category: response.post.category || '文化讨论'  // 添加分类字段
              }
              console.log('帖子详情已加载');
            } else {
              // 检查错误类型并给出相应提示
              if (response.code === 404) {
                error.value = '帖子不存在或已被删除';
              } else if (response.code === 403) {
                error.value = '您没有权限编辑此帖子';
              } else if (response.code === 401) {
                error.value = '登录已过期，请重新登录';
                // 清除本地认证信息并跳转到登录页面
                localStorage.removeItem('access_token');
                localStorage.removeItem('user');
                setTimeout(() => {
                  router.push('/login');
                }, 2000);
              } else {
                // 检查是否是错误响应
                if (response.error) {
                  error.value = response.error || '获取帖子详情失败';
                } else {
                  throw new Error(response.message || '获取帖子详情失败')
                }
              }
            }
          } else {
            // 如果响应不是期望的对象格式，则认为是错误
            error.value = '服务器响应格式错误';
          }
        } catch (innerErr) {
          console.error('在API调用过程中捕获到错误:', innerErr);
          throw innerErr; // 重新抛出错误，以便外层处理
        }
      } catch (err) {
        console.error('获取帖子详情错误:', err);
        console.error('错误详细信息:', err.message, err.stack);
        
        // 检查是否是网络错误
        if (err.message.includes('网络连接失败') || err.message.includes('fetch')) {
          error.value = '网络连接失败，请检查网络连接或后端服务是否正常运行';
        } else if (err.message.includes('登录已过期')) {
          error.value = '登录已过期，请重新登录';
        } else {
          error.value = err.message || '获取帖子详情失败';
        }
        
        // 不自动跳转，让用户可以看到错误信息
        // 如果需要，可以提供手动跳转选项
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
        
        console.log('开始更新帖子，帖子ID:', postId);
        console.log('请求数据:', {
          title: post.value.title,
          content: post.value.content.substring(0, 50) + '...' // 只记录内容开头部分
        });
        
        const response = await request(`/posts/${postId}`, 'PUT', {
          title: post.value.title,
          content: post.value.content,
          category: post.value.category  // 添加分类字段
        })
        
        console.log('更新帖子响应:', response);
        
        if (response.success) {
          successMessage.value = '帖子更新成功！'
          
          // 2秒后跳转到帖子详情页面
          setTimeout(() => {
            router.push(`/post-detail/${postId}`)
          }, 2000)
        } else {
          // 增强错误处理
          if (response.code === 400) {
            error.value = '标题或内容不能为空，且标题不能超过200字符，内容不能超过5000字符';
          } else if (response.code === 401) {
            error.value = '登录已过期，请重新登录';
            localStorage.removeItem('access_token');
            localStorage.removeItem('user');
            setTimeout(() => {
              router.push('/login');
            }, 2000);
          } else if (response.code === 403) {
            error.value = '您没有权限更新此帖子';
          } else if (response.code === 404) {
            error.value = '要更新的帖子不存在';
          } else {
            error.value = response.message || '更新帖子失败'
          }
        }
      } catch (err) {
        console.error('更新帖子错误:', err)
        console.error('错误堆栈:', err.stack);
        
        if (err.message.includes('网络连接失败') || err.message.includes('fetch')) {
          error.value = '网络连接失败，请检查网络连接或后端服务是否正常运行';
        } else if (err.message.includes('登录已过期')) {
          error.value = '登录已过期，请重新登录';
          localStorage.removeItem('access_token');
          localStorage.removeItem('user');
          setTimeout(() => {
            router.push('/login');
          }, 2000);
        } else {
          error.value = err.message || '更新帖子失败，请稍后重试'
        }
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