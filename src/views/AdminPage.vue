<template>
  <div class="admin-page">
    <div class="container">
      <header class="admin-header">
        <h1>管理中心</h1>
        <p>管理湖湘文化数字化平台的内容和用户</p>
      </header>

      <div class="admin-content">
        <!-- 用户管理区域 -->
        <section class="management-section">
          <div class="section-header">
            <h2>用户管理</h2>
            <div class="section-controls">
              <button @click="refreshUsers" class="refresh-btn">
                <i class="fas fa-sync-alt"></i> 刷新
              </button>
            </div>
          </div>
          
          <div class="users-table-container">
            <table class="users-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>用户名</th>
                  <th>邮箱</th>
                  <th>角色</th>
                  <th>注册时间</th>
                  <th>操作</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="user in users" :key="user.id">
                  <td>{{ user.id }}</td>
                  <td>{{ user.username }}</td>
                  <td>{{ user.email }}</td>
                  <td>
                    <span :class="['role-badge', user.is_admin ? 'admin' : 'normal']">
                      {{ user.is_admin ? '管理员' : '普通用户' }}
                    </span>
                  </td>
                  <td>{{ formatDate(user.created_at) }}</td>
                  <td>
                    <button 
                      @click="toggleUserRole(user)" 
                      :class="['role-toggle-btn', user.is_admin ? 'demote' : 'promote']"
                      :disabled="user.id === currentUserId"
                    >
                      {{ user.is_admin ? '降级为普通用户' : '提升为管理员' }}
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
            
            <div v-if="usersLoading" class="loading">加载用户数据中...</div>
            <div v-if="usersError" class="error">{{ usersError }}</div>
          </div>
        </section>

        <!-- 文化资源管理区域 -->
        <section class="management-section">
          <div class="section-header">
            <h2>文化资源管理</h2>
            <div class="section-controls">
              <button @click="addResource" class="primary-btn">
                <i class="fas fa-plus"></i> 添加资源
              </button>
            </div>
          </div>
          
          <div class="resources-grid">
            <div v-for="resource in resources" :key="resource.id" class="resource-card">
              <div class="resource-info">
                <h3>{{ resource.title }}</h3>
                <p class="resource-desc">{{ resource.description.substring(0, 100) }}...</p>
                <div class="resource-meta">
                  <span class="category">{{ resource.category }}</span>
                  <span class="author">作者: {{ resource.author?.username }}</span>
                </div>
              </div>
              <div class="resource-actions">
                <button @click="editResource(resource)" class="edit-btn">编辑</button>
                <button @click="deleteResource(resource)" class="delete-btn">删除</button>
              </div>
            </div>
          </div>
          
          <div v-if="resourcesLoading" class="loading">加载文化资源中...</div>
          <div v-if="resourcesError" class="error">{{ resourcesError }}</div>
        </section>

        <!-- 社区内容管理 -->
        <section class="management-section">
          <div class="section-header">
            <h2>社区内容管理</h2>
            <div class="section-controls">
              <button @click="addPost" class="primary-btn">
                <i class="fas fa-plus"></i> 发布帖子
              </button>
            </div>
          </div>
          
          <div class="posts-list">
            <div v-for="post in posts" :key="post.id" class="post-item">
              <div class="post-content">
                <h3>{{ post.title }}</h3>
                <p class="post-excerpt">{{ post.content.substring(0, 150) }}...</p>
                <div class="post-meta">
                  <span>作者: {{ post.author?.username }}</span>
                  <span>时间: {{ formatDate(post.created_at) }}</span>
                </div>
              </div>
              <div class="post-actions">
                <button @click="editPost(post)" class="edit-btn">编辑</button>
                <button @click="deletePost(post)" class="delete-btn">删除</button>
              </div>
            </div>
          </div>
          
          <div v-if="postsLoading" class="loading">加载帖子数据中...</div>
          <div v-if="postsError" class="error">{{ postsError }}</div>
        </section>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { request } from '../services/api.js'

export default {
  name: 'AdminPage',
  setup() {
    const router = useRouter()
    
    // 用户管理相关
    const users = ref([])
    const usersLoading = ref(false)
    const usersError = ref('')
    
    // 资源管理相关
    const resources = ref([])
    const resourcesLoading = ref(false)
    const resourcesError = ref('')
    
    // 帖子管理相关
    const posts = ref([])
    const postsLoading = ref(false)
    const postsError = ref('')
    
    // 当前用户信息
    const currentUser = JSON.parse(localStorage.getItem('user') || '{}')
    const currentUserId = currentUser.id
    
    // 获取所有用户
    const fetchUsers = async () => {
      try {
        usersLoading.value = true
        usersError.value = ''
        
        const response = await request('/admin/users', 'GET')
        users.value = response.users || []
      } catch (err) {
        console.error('获取用户列表错误:', err)
        usersError.value = err.message || '获取用户列表失败'
      } finally {
        usersLoading.value = false
      }
    }
    
    // 获取文化资源
    const fetchResources = async () => {
      try {
        resourcesLoading.value = true
        resourcesError.value = ''
        
        const response = await request('/resources', 'GET')
        resources.value = response.resources || []
      } catch (err) {
        console.error('获取文化资源错误:', err)
        resourcesError.value = err.message || '获取文化资源失败'
      } finally {
        resourcesLoading.value = false
      }
    }
    
    // 获取帖子
    const fetchPosts = async () => {
      try {
        postsLoading.value = true
        postsError.value = ''
        
        const response = await request('/posts', 'GET')
        posts.value = response.posts || []
      } catch (err) {
        console.error('获取帖子错误:', err)
        postsError.value = err.message || '获取帖子失败'
      } finally {
        postsLoading.value = false
      }
    }
    
    // 切换用户角色
    const toggleUserRole = async (user) => {
      if (user.id === currentUserId) {
        alert('不能修改自己的角色')
        return
      }
      
      const newRole = user.is_admin ? '普通用户' : '管理员'
      if (!confirm(`确定要将用户 "${user.username}" 变更为 ${newRole} 吗？`)) {
        return
      }
      
      try {
        // 这里后端并没有提供直接的角色修改API，我们暂时显示提示
        alert(`角色变更功能需要后端API支持，当前仅为演示`)
      } catch (err) {
        console.error('切换用户角色错误:', err)
        alert(err.message || '切换用户角色失败')
      }
    }
    
    // 刷新用户列表
    const refreshUsers = () => {
      fetchUsers()
    }
    
    // 添加资源
    const addResource = () => {
      router.push('/create-resource')
    }
    
    // 编辑资源
    const editResource = (resource) => {
      router.push(`/edit-resource/${resource.id}`)
    }
    
    // 删除资源
    const deleteResource = (resource) => {
      if (!confirm(`确定要删除文化资源 "${resource.title}" 吗？`)) {
        return
      }
      
      // 这里应该调用删除API，但为了演示，暂时只做跳转
      router.push(`/resource-detail/${resource.id}`)
    }
    
    // 添加帖子
    const addPost = () => {
      router.push('/create-post')
    }
    
    // 编辑帖子
    const editPost = (post) => {
      router.push(`/edit-post/${post.id}`)
    }
    
    // 删除帖子
    const deletePost = (post) => {
      if (!confirm(`确定要删除帖子 "${post.title}" 吗？`)) {
        return
      }
      
      // 这里应该调用删除API，但为了演示，暂时只做跳转
      router.push(`/post-detail/${post.id}`)
    }
    
    // 格式化日期
    const formatDate = (dateString) => {
      const date = new Date(dateString)
      return date.toLocaleDateString('zh-CN', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      })
    }
    
    onMounted(() => {
      fetchUsers()
      fetchResources()
      fetchPosts()
    })
    
    return {
      users,
      usersLoading,
      usersError,
      resources,
      resourcesLoading,
      resourcesError,
      posts,
      postsLoading,
      postsError,
      currentUserId,
      fetchUsers,
      fetchResources,
      fetchPosts,
      toggleUserRole,
      refreshUsers,
      addResource,
      editResource,
      deleteResource,
      addPost,
      editPost,
      deletePost,
      formatDate
    }
  }
}
</script>

<style scoped>
.admin-page {
  padding: 2rem 0;
  min-height: calc(100vh - 200px);
  background: #f8f9fa;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
}

.admin-header {
  text-align: center;
  margin-bottom: 2rem;
}

.admin-header h1 {
  font-size: 2.5rem;
  color: #333;
  margin-bottom: 0.5rem;
}

.admin-header p {
  color: #666;
  font-size: 1.1rem;
}

.admin-content {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.management-section {
  background: white;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid #eee;
}

.section-header h2 {
  color: #333;
  margin: 0;
}

.section-controls {
  display: flex;
  gap: 0.5rem;
}

.refresh-btn, .primary-btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  background: #4a90e2;
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.refresh-btn:hover, .primary-btn:hover {
  background: #3a7bc8;
}

.users-table-container {
  overflow-x: auto;
}

.users-table {
  width: 100%;
  border-collapse: collapse;
}

.users-table th,
.users-table td {
  padding: 0.75rem;
  text-align: left;
  border-bottom: 1px solid #eee;
}

.users-table th {
  background: #f8f9fa;
  font-weight: bold;
  color: #333;
}

.role-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.85rem;
}

.role-badge.admin {
  background: #e3f2fd;
  color: #1976d2;
}

.role-badge.normal {
  background: #e8f5e9;
  color: #388e3c;
}

.role-toggle-btn {
  padding: 0.25rem 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.85rem;
}

.role-toggle-btn.promote {
  background: #e3f2fd;
  color: #1976d2;
}

.role-toggle-btn.demote {
  background: #ffebee;
  color: #d32f2f;
}

.role-toggle-btn:disabled {
  background: #f5f5f5;
  color: #999;
  cursor: not-allowed;
}

.resources-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1rem;
}

.resource-card {
  border: 1px solid #eee;
  border-radius: 6px;
  padding: 1rem;
  display: flex;
  flex-direction: column;
}

.resource-info h3 {
  margin-top: 0;
  margin-bottom: 0.5rem;
  color: #333;
}

.resource-desc {
  color: #666;
  margin-bottom: 1rem;
  flex-grow: 1;
}

.resource-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  margin-bottom: 1rem;
}

.category {
  background: #e3f2fd;
  color: #1976d2;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.85rem;
}

.author {
  color: #666;
  font-size: 0.85rem;
}

.resource-actions {
  display: flex;
  gap: 0.5rem;
  margin-top: auto;
}

.edit-btn {
  padding: 0.5rem 1rem;
  border: 1px solid #4a90e2;
  background: white;
  color: #4a90e2;
  border-radius: 4px;
  cursor: pointer;
}

.edit-btn:hover {
  background: #e3f5ff;
}

.delete-btn {
  padding: 0.5rem 1rem;
  border: 1px solid #d32f2f;
  background: white;
  color: #d32f2f;
  border-radius: 4px;
  cursor: pointer;
}

.delete-btn:hover {
  background: #ffebee;
}

.posts-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.post-item {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  border: 1px solid #eee;
  border-radius: 6px;
  padding: 1rem;
}

.post-content {
  flex: 1;
  margin-right: 1rem;
}

.post-content h3 {
  margin-top: 0;
  margin-bottom: 0.5rem;
  color: #333;
}

.post-excerpt {
  color: #666;
  margin-bottom: 0.5rem;
}

.post-meta {
  display: flex;
  gap: 1rem;
  color: #666;
  font-size: 0.9rem;
}

.post-actions {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.loading {
  text-align: center;
  padding: 2rem;
  color: #666;
}

.error {
  padding: 1rem;
  background: #ffebee;
  color: #d32f2f;
  border-radius: 4px;
  border-left: 4px solid #d32f2f;
}
</style>