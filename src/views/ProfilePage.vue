<template>
  <div class="profile-container">
    <div class="profile-box">
      <div class="profile-header">
        <h2>个人中心</h2>
        <p>管理您的账户信息</p>
      </div>
      
      <!-- 加载状态 -->
      <div v-if="loading" class="loading-state">
        <p>正在加载用户信息...</p>
      </div>
      
      <!-- 错误状态 -->
      <div v-else-if="error" class="error-state">
        <p>{{ error }}</p>
        <button @click="fetchUserProfile" class="retry-button">重试</button>
      </div>
      
      <!-- 用户信息内容 -->
      <div v-else class="profile-content">
        <!-- 头像上传区域 -->
        <div class="avatar-section">
          <div class="avatar-upload">
            <div class="avatar-preview" :style="{ backgroundImage: `url(${user?.avatar || '/api/placeholder/120/120'})` }">
              <input type="file" ref="avatarInput" class="avatar-input" accept="image/*" @change="handleAvatarChange">
            </div>
            <label for="avatar-upload-btn" class="avatar-upload-label">
              更换头像
            </label>
            <button id="avatar-upload-btn" type="button" class="avatar-upload-button" @click="triggerAvatarUpload">
              选择图片
            </button>
          </div>
        </div>
        
        <!-- 用户信息表单 -->
        <form @submit.prevent="handleUpdateProfile" class="profile-form">
          <div class="form-group">
            <label for="username">昵称</label>
            <input
              type="text"
              id="username"
              v-model="editForm.username"
              placeholder="请输入您的昵称"
              required
            />
          </div>
          
          <div class="form-group">
            <label for="email">邮箱</label>
            <input
              type="email"
              id="email"
              :value="user?.email || '加载中...'"
              placeholder="请输入您的邮箱"
              required
              readonly
            />
            <small class="form-hint">邮箱不可修改</small>
          </div>
          
          <div v-if="error" class="error-message">{{ error }}</div>
          <div v-if="uploadMessage" class="success-message">{{ uploadMessage }}</div>
          
          <button type="submit" class="save-button">保存修改</button>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { request } from '../services/api.js'

export default {
  name: 'ProfilePage',
  setup() {
    const user = ref(null)
    const loading = ref(true)
    const error = ref('')
    const isEditing = ref(false)
    const editForm = ref({
      username: '',
      avatar: ''
    })
    const uploadMessage = ref('')
    
    // 获取当前用户信息
    const fetchUserProfile = async () => {
      try {
        loading.value = true
        error.value = ''
        
        // 从localStorage获取用户ID
        const storedUser = localStorage.getItem('user')
        if (!storedUser) {
          throw new Error('请先登录')
        }
        
        const userData = JSON.parse(storedUser)
        const response = await request(`/profile/${userData.id}`, 'GET')
        
        user.value = response.user
        editForm.value.username = response.user.username
        editForm.value.avatar = response.user.avatar || ''
      } catch (err) {
        console.error('获取用户信息错误:', err)
        error.value = err.message || '获取用户信息失败'
      } finally {
        loading.value = false
      }
    }
    
    // 更新用户资料
    const handleUpdateProfile = async () => {
      try {
        const storedUser = localStorage.getItem('user')
        if (!storedUser) {
          throw new Error('请先登录')
        }
        
        const userData = JSON.parse(storedUser)
        
        const response = await request(`/profile/${userData.id}`, 'PUT', {
          username: editForm.value.username
        })
        
        if (response.success) {
          // 更新本地存储的用户信息
          user.value = response.user
          localStorage.setItem('user', JSON.stringify(response.user))
          
          uploadMessage.value = '资料更新成功！'
          
          setTimeout(() => {
            uploadMessage.value = ''
          }, 3000)
        } else {
          throw new Error(response.message || '更新失败')
        }
      } catch (err) {
        console.error('更新用户资料错误:', err)
        uploadMessage.value = err.message || '更新资料失败'
      }
    }
    
    // 触发头像上传
    const triggerAvatarUpload = () => {
      document.querySelector('.avatar-input').click()
    }
    
    // 处理头像选择
    const handleAvatarChange = async (event) => {
      const file = event.target.files[0]
      if (!file) return
      
      // 验证文件类型
      if (!file.type.startsWith('image/')) {
        uploadMessage.value = '请选择有效的图片文件'
        return
      }
      
      // 这里应该上传头像到服务器，但现在我们先简单地将其转换为base64
      const reader = new FileReader()
      reader.onload = async (e) => {
        try {
          // 保存头像到用户资料
          const storedUser = localStorage.getItem('user')
          if (!storedUser) {
            throw new Error('请先登录')
          }
          
          const userData = JSON.parse(storedUser)
          
          const response = await request(`/profile/${userData.id}`, 'PUT', {
            username: editForm.value.username,
            avatar: e.target.result
          })
          
          if (response.success) {
            user.value = response.user
            localStorage.setItem('user', JSON.stringify(response.user))
            uploadMessage.value = '头像更新成功！'
            
            setTimeout(() => {
              uploadMessage.value = ''
            }, 3000)
          } else {
            throw new Error(response.message || '更新头像失败')
          }
        } catch (err) {
          console.error('更新头像错误:', err)
          uploadMessage.value = err.message || '更新头像失败'
        }
      }
      reader.readAsDataURL(file)
    }
    
    onMounted(() => {
      fetchUserProfile()
    })
    
    return {
      user,
      loading,
      error,
      isEditing,
      editForm,
      uploadMessage,
      fetchUserProfile,
      handleUpdateProfile,
      triggerAvatarUpload,
      handleAvatarChange
    }
  }
}
</script>

<style scoped>
/* 个人中心容器 - PC优先设计 */
.profile-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 2rem;
  background: linear-gradient(135deg, #C8102E 0%, #8B0000 100%);
  position: relative;
  overflow: hidden;
}

/* 背景装饰元素 */
.profile-container::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0) 70%);
  z-index: 0;
}

/* 个人中心框 - PC优先设计 */
.profile-box {
  background: white;
  border-radius: 16px;
  padding: 3rem;
  box-shadow: 0 15px 40px rgba(0, 0, 0, 0.15);
  width: 100%;
  max-width: 600px;
  margin-bottom: 2rem;
  position: relative;
  z-index: 1;
  transition: transform 0.3s ease;
}

.profile-box:hover {
  transform: translateY(-5px);
}

/* 个人中心头部 */
.profile-header {
  text-align: center;
  margin-bottom: 2.5rem;
}

.profile-header h2 {
  color: #2c3e50;
  font-size: 2.4rem;
  margin-bottom: 0.5rem;
  font-weight: bold;
}

.profile-header p {
  color: #7f8c8d;
  font-size: 1.1rem;
  margin: 0;
}

/* 头像上传区域 */
.avatar-section {
  display: flex;
  justify-content: center;
  margin-bottom: 2.5rem;
}

.avatar-upload {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.avatar-preview {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  border: 4px solid #ecf0f1;
  position: relative;
  cursor: pointer;
  transition: all 0.3s ease;
}

.avatar-preview:hover {
  border-color: #C8102E;
  transform: scale(1.05);
}

.avatar-input {
  opacity: 0;
  position: absolute;
  width: 100%;
  height: 100%;
  cursor: pointer;
}

.avatar-upload-label {
  color: #7f8c8d;
  font-size: 0.95rem;
  margin-bottom: 0.5rem;
}

.avatar-upload-button {
  background: #ecf0f1;
  color: #34495e;
  border: none;
  padding: 0.6rem 1.2rem;
  border-radius: 6px;
  font-size: 0.95rem;
  cursor: pointer;
  transition: background-color 0.3s;
}

.avatar-upload-button:hover {
  background: #bdc3c7;
}

/* 个人资料表单 */
.profile-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

/* 表单组 */
.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  color: #34495e;
  font-weight: 600;
  font-size: 1rem;
}

.form-group input {
  padding: 1rem 1.2rem;
  border: 2px solid #ecf0f1;
  border-radius: 8px;
  font-size: 1rem;
  transition: border-color 0.3s, box-shadow 0.3s;
}

.form-group input:focus {
  outline: none;
  border-color: #C8102E;
  box-shadow: 0 0 0 3px rgba(200, 16, 46, 0.1);
}

.form-group input[readonly] {
  background-color: #f8f9fa;
  cursor: not-allowed;
}

.form-hint {
  color: #95a5a6;
  font-size: 0.85rem;
  margin-top: 0.2rem;
}

/* 错误和成功消息 */
.error-message {
  background-color: #fee;
  color: #e74c3c;
  padding: 0.8rem 1rem;
  border-radius: 8px;
  text-align: center;
  font-size: 0.95rem;
  border-left: 4px solid #e74c3c;
}

.success-message {
  background-color: #e6f7e6;
  color: #27ae60;
  padding: 0.8rem 1rem;
  border-radius: 8px;
  text-align: center;
  font-size: 0.95rem;
  border-left: 4px solid #27ae60;
}

/* 保存按钮 */
.save-button {
  background: linear-gradient(135deg, #C8102E 0%, #8B0000 100%);
  color: white;
  border: none;
  padding: 1.1rem;
  border-radius: 8px;
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.3s;
  margin-top: 1rem;
}

.save-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(200, 16, 46, 0.4);
}

.save-button:active {
  transform: translateY(0);
}

/* 响应式设计 - 增强多端适配 */

/* 大屏幕桌面（1400px及以上） */
@media (min-width: 1400px) {
  .profile-box {
    max-width: 650px;
    padding: 3.5rem;
  }
  
  .profile-header h2 {
    font-size: 2.6rem;
  }
}

/* 小屏幕桌面（992px-1199px） */
@media (max-width: 1199px) {
  .profile-box {
    max-width: 580px;
  }
  
  .profile-header h2 {
    font-size: 2.2rem;
  }
}

/* 平板设备（768px-991px） */
@media (max-width: 991px) {
  .profile-box {
    padding: 2.5rem;
    max-width: 550px;
  }
  
  .profile-header {
    margin-bottom: 2rem;
  }
  
  .profile-header h2 {
    font-size: 2rem;
  }
  
  .profile-form {
    gap: 1.2rem;
  }
}

/* 小平板/大屏手机（576px-767px） */
@media (max-width: 767px) {
  .profile-container {
    padding: 1.5rem;
  }
  
  .profile-box {
    padding: 2rem;
    border-radius: 12px;
  }
  
  .profile-header h2 {
    font-size: 1.8rem;
  }
  
  .profile-header p {
    font-size: 1rem;
  }
  
  .form-group input {
    padding: 0.9rem 1rem;
  }
  
  .save-button {
    padding: 1rem;
    font-size: 1rem;
  }
}

/* 手机设备（小于576px） */
@media (max-width: 575px) {
  .profile-container {
    padding: 1rem;
    justify-content: flex-start;
    padding-top: 3rem;
  }
  
  .profile-box {
    padding: 1.5rem;
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
  }
  
  .profile-header h2 {
    font-size: 1.6rem;
  }
  
  .avatar-preview {
    width: 100px;
    height: 100px;
  }
  
  .form-group {
    gap: 0.4rem;
  }
  
  .form-group label {
    font-size: 0.95rem;
  }
  
  .form-group input {
    padding: 0.8rem 0.9rem;
    font-size: 0.95rem;
  }
  
  .save-button {
    padding: 0.9rem;
  }
}
</style>