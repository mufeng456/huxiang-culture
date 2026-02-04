<template>
  <div class="edit-resource-page">
    <div class="container">
      <div class="edit-resource-header">
        <h1>编辑文化资源</h1>
        <p>修改湖湘文化资源内容</p>
      </div>
      
      <form @submit.prevent="handleSubmit" class="edit-resource-form">
        <div class="form-group">
          <label for="resourceTitle">标题 *</label>
          <input
            type="text"
            id="resourceTitle"
            v-model="resource.title"
            placeholder="请输入资源标题"
            required
            maxlength="200"
          />
        </div>
        
        <div class="form-group">
          <label for="resourceDescription">描述 *</label>
          <textarea
            id="resourceDescription"
            v-model="resource.description"
            placeholder="请输入资源详细描述"
            required
            rows="6"
            maxlength="2000"
          ></textarea>
        </div>
        
        <div class="form-group">
          <label for="resourceCategory">分类</label>
          <select id="resourceCategory" v-model="resource.category">
            <option value="">请选择分类</option>
            <option value="历史遗迹">历史遗迹</option>
            <option value="传统艺术">传统艺术</option>
            <option value="文学作品">文学作品</option>
            <option value="饮食文化">饮食文化</option>
            <option value="民俗风情">民俗风情</option>
            <option value="名人典故">名人典故</option>
            <option value="其他">其他</option>
          </select>
        </div>
        
        <div class="form-group">
          <label for="resourceImageUrl">图片链接</label>
          <input
            type="url"
            id="resourceImageUrl"
            v-model="resource.image_url"
            placeholder="请输入图片链接"
          />
        </div>
        
        <div class="form-group">
          <label for="resourceTags">标签</label>
          <input
            type="text"
            id="resourceTags"
            v-model="tagsInput"
            placeholder="请输入标签，用逗号分隔，例如：湖湘文化,长沙,历史"
          />
        </div>
        
        <div class="form-actions">
          <button type="button" @click="cancel" class="btn-cancel">取消</button>
          <button type="submit" class="btn-submit" :disabled="isSubmitting">
            {{ isSubmitting ? '更新中...' : '更新资源' }}
          </button>
        </div>
        
        <div v-if="error" class="error-message">{{ error }}</div>
        <div v-if="successMessage" class="success-message">{{ successMessage }}</div>
      </form>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { request } from '../services/api.js'

export default {
  name: 'EditResourcePage',
  setup() {
    const router = useRouter()
    const route = useRoute()
    
    const resource = ref({
      title: '',
      description: '',
      category: '',
      image_url: '',
      tags: []
    })
    
    const tagsInput = ref('')
    const resourceId = parseInt(route.params.id)
    
    // 使用计算属性处理标签输入
    const tagsArray = computed({
      get: () => tagsInput.value,
      set: (value) => {
        tagsInput.value = value
        resource.value.tags = value.split(',').map(tag => tag.trim()).filter(tag => tag)
      }
    })
    
    const isSubmitting = ref(false)
    const error = ref('')
    const successMessage = ref('')
    
    // 获取资源详情
    const fetchResourceDetail = async () => {
      try {
        const response = await request(`/resources/${resourceId}`, 'GET')
        
        if (response.success) {
          resource.value = {
            title: response.resource.title,
            description: response.resource.description,
            category: response.resource.category,
            image_url: response.resource.image_url,
            tags: response.resource.tags ? response.resource.tags.split(',') : []
          }
          // 设置标签输入框的值
          tagsInput.value = resource.value.tags.join(', ')
        } else {
          throw new Error(response.message || '获取资源详情失败')
        }
      } catch (err) {
        console.error('获取资源详情错误:', err)
        error.value = err.message || '获取资源详情失败'
        // 如果获取失败，返回文化资源页面
        setTimeout(() => {
          router.push('/cultural-resources')
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
          error.value = '请先登录后再更新资源'
          return
        }
        
        // 调用API更新文化资源
        const response = await request(`/resources/${resourceId}`, 'PUT', {
          title: resource.value.title,
          description: resource.value.description,
          category: resource.value.category || '未分类',
          image_url: resource.value.image_url,
          tags: resource.value.tags
        })
        
        if (response.success) {
          successMessage.value = '文化资源更新成功！'
          
          // 2秒后跳转到资源详情页面
          setTimeout(() => {
            router.push(`/resource-detail/${resourceId}`)
          }, 2000)
        } else {
          error.value = response.message || '更新资源失败'
        }
      } catch (err) {
        console.error('更新资源错误:', err)
        error.value = err.message || '更新资源失败，请稍后重试'
      } finally {
        isSubmitting.value = false
      }
    }
    
    const cancel = () => {
      router.go(-1) // 返回上一页
    }
    
    onMounted(() => {
      fetchResourceDetail()
    })
    
    return {
      resource,
      tagsInput,
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
.edit-resource-page {
  padding: 2rem 0;
  min-height: calc(100vh - 200px);
}

.container {
  max-width: 800px;
  margin: 0 auto;
  padding: 0 1rem;
}

.edit-resource-header {
  text-align: center;
  margin-bottom: 2rem;
}

.edit-resource-header h1 {
  font-size: 2rem;
  color: #333;
  margin-bottom: 0.5rem;
}

.edit-resource-header p {
  color: #666;
  font-size: 1.1rem;
}

.edit-resource-form {
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
.form-group textarea,
.form-group select {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-family: inherit;
  font-size: 1rem;
  resize: vertical;
}

.form-group input:focus,
.form-group textarea:focus,
.form-group select:focus {
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