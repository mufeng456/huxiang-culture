<template>
  <div class="community-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="container">
        <h1>互动社区</h1>
        <p>加入我们的社区，分享您对湖湘文化的见解与热情</p>
      </div>
    </div>

    <!-- 主要内容 -->
    <div class="container">
      <!-- 社区导航 -->
      <div class="community-nav">
        <button 
          class="nav-tab" 
          :class="{ active: activeTab === 'forum' }" 
          @click="switchTab('forum')"
        >
          <i class="fas fa-comments"></i> 文化论坛
        </button>
        <button 
          class="nav-tab" 
          :class="{ active: activeTab === 'activities' }" 
          @click="switchTab('activities')"
        >
          <i class="fas fa-calendar-alt"></i> 文化活动
        </button>
        <button 
          class="nav-tab" 
          :class="{ active: activeTab === 'contributions' }" 
          @click="switchTab('contributions')"
        >
          <i class="fas fa-hand-holding-heart"></i> 内容贡献
        </button>
        <button 
          class="nav-tab" 
          :class="{ active: activeTab === 'feedback' }" 
          @click="switchTab('feedback')"
        >
          <i class="fas fa-comment-dots"></i> 意见反馈
        </button>
        <button 
          class="nav-tab" 
          :class="{ active: activeTab === 'my-posts' }" 
          @click="switchTab('my-posts')"
          v-if="isLoggedIn"
        >
          <i class="fas fa-user"></i> 我的帖子
        </button>
      </div>

      <!-- 论坛内容 -->
      <div v-if="activeTab === 'forum'" class="forum-content">
        <!-- 发帖按钮 -->
        <div class="forum-actions">
          <button class="create-post-btn" @click="createNewPost">
            <i class="fas fa-plus-circle"></i> 发布新主题
          </button>
          
          <!-- 排序选项 -->
          <div class="sort-options">
            <select v-model="forumSortBy" @change="sortForumPosts" class="sort-select">
              <option value="latest">最新发布</option>
              <option value="popular">最受欢迎</option>
              <option value="comments">评论最多</option>
            </select>
          </div>
        </div>

        <!-- 加载状态 -->
        <div v-if="loading" class="loading-posts">
          <p>正在加载帖子...</p>
        </div>

        <!-- 帖子列表 -->
        <div v-else class="posts-list">
          <div 
            v-for="post in displayedPosts" 
            :key="post.id" 
            class="post-item"
            @click="viewPostDetails(post.id)"
          >
            <div class="post-card">
              <div class="post-header">
                <div class="post-author">
                  <img :src="post.author?.avatar || '/api/placeholder/40/40'" :alt="post.author?.username" class="author-avatar" loading="lazy" />
                  <div class="author-info">
                    <span class="author-name">{{ post.author?.username }}</span>
                    <span class="post-date">{{ formatDate(post.created_at) }}</span>
                  </div>
                </div>
                <div class="post-stats">
                  <span class="stat-item"><i class="far fa-eye"></i> {{ post.views || 0 }}</span>
                  <span class="stat-item"><i class="far fa-comment"></i> {{ post.comments_count || 0 }}</span>
                  <span class="stat-item"><i class="far fa-thumbs-up"></i> {{ post.likes_count || 0 }}</span>
                </div>
              </div>
              <div class="post-body">
                <div class="post-tags">
                  <span class="post-category">{{ post.category || '文化讨论' }}</span>
                </div>
                <h3 class="post-title">{{ post.title }}</h3>
                <p class="post-excerpt">{{ truncateText(post.content, 150) }}</p>
              </div>
              
              <!-- 添加操作按钮，仅对帖子作者显示 -->
              <div class="post-actions" v-if="isPostOwner(post)">
                <button class="action-btn edit-btn" @click.stop="editPost(post.id)">
                  <i class="fas fa-edit"></i> 编辑
                </button>
                <button class="action-btn delete-btn" @click.stop="confirmDeletePost(post.id, post.title)">
                  <i class="fas fa-trash"></i> 删除
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- 分页 -->
        <div v-if="!loading && totalPages > 1" class="pagination">
          <button 
            @click="goToPage(currentPage - 1)" 
            :disabled="currentPage === 1"
            class="pagination-btn"
          >
            上一页
          </button>
          
          <span 
            v-for="page in getPageNumbers()" 
            :key="page"
            @click="goToPage(page)"
            :class="['page-number', { active: page === currentPage }]"
          >
            {{ page }}
          </span>
          
          <button 
            @click="goToPage(currentPage + 1)" 
            :disabled="currentPage === totalPages"
            class="pagination-btn"
          >
            下一页
          </button>
        </div>
      </div>

      <!-- 我的帖子内容 -->
      <div v-if="activeTab === 'my-posts'" class="my-posts-content">
        <!-- 发帖按钮 -->
        <div class="forum-actions">
          <button class="create-post-btn" @click="createNewPost">
            <i class="fas fa-plus-circle"></i> 发布新主题
          </button>
        </div>

        <!-- 加载状态 -->
        <div v-if="myPostsLoading" class="loading-posts">
          <p>正在加载我的帖子...</p>
        </div>

        <!-- 我的帖子列表 -->
        <div v-else class="posts-list">
          <div 
            v-for="post in myPosts" 
            :key="post.id" 
            class="post-item"
          >
            <div class="post-card">
              <div class="post-header">
                <div class="post-author">
                  <img :src="post.author?.avatar || '/api/placeholder/40/40'" :alt="post.author?.username" class="author-avatar" loading="lazy" />
                  <div class="author-info">
                    <span class="author-name">{{ post.author?.username }}</span>
                    <span class="post-date">{{ formatDate(post.created_at) }}</span>
                  </div>
                </div>
                <div class="post-stats">
                  <span class="stat-item"><i class="far fa-eye"></i> {{ post.views || 0 }}</span>
                  <span class="stat-item"><i class="far fa-comment"></i> {{ post.comments_count || 0 }}</span>
                  <span class="stat-item"><i class="far fa-thumbs-up"></i> {{ post.likes_count || 0 }}</span>
                </div>
              </div>
              <div class="post-body">
                <div class="post-tags">
                  <span class="post-category">{{ post.category || '文化讨论' }}</span>
                </div>
                <h3 class="post-title">{{ post.title }}</h3>
                <p class="post-excerpt">{{ truncateText(post.content, 150) }}</p>
              </div>
              <!-- 我的帖子操作按钮 -->
              <div class="post-actions">
                <button class="action-btn edit-btn" @click.stop="editMyPost(post.id)">
                  <i class="fas fa-edit"></i> 编辑
                </button>
                <button class="action-btn delete-btn" @click.stop="deleteMyPost(post.id, post.title)">
                  <i class="fas fa-trash"></i> 删除
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- 分页 -->
        <div v-if="!myPostsLoading && myTotalPages > 1" class="pagination">
          <button 
            @click="goToMyPage(myCurrentPage - 1)" 
            :disabled="myCurrentPage === 1"
            class="pagination-btn"
          >
            上一页
          </button>
          
          <span 
            v-for="page in getMyPageNumbers()" 
            :key="page"
            @click="goToMyPage(page)"
            :class="['page-number', { active: page === myCurrentPage }]"
          >
            {{ page }}
          </span>
          
          <button 
            @click="goToMyPage(myCurrentPage + 1)" 
            :disabled="myCurrentPage === myTotalPages"
            class="pagination-btn"
          >
            下一页
          </button>
        </div>
        
        <!-- 空状态 -->
        <div v-if="!myPostsLoading && myPosts.length === 0" class="empty-state">
          <p>您还没有发布任何帖子，<a href="#" @click.prevent="createNewPost">立即发布第一篇帖子</a></p>
        </div>
      </div>

      <!-- 文化活动 -->
      <div v-if="activeTab === 'activities'" class="activities-content">
        <div class="activities-grid">
          <div v-for="activity in activities" :key="activity.id" class="activity-card">
            <div class="activity-image">
              <img :src="activity.imageUrl" :alt="activity.title" />
              <div class="activity-date">
                {{ formatActivityDate(activity.startDate) }}
              </div>
            </div>
            <div class="activity-info">
              <h3 class="activity-title">{{ activity.title }}</h3>
              <p class="activity-location"><i class="fas fa-map-marker-alt"></i> {{ activity.location }}</p>
              <p class="activity-description">{{ activity.description }}</p>
              <div class="activity-footer">
                <button class="activity-btn" @click="joinActivity(activity.id)">
                  {{ activity.isJoined ? '已报名' : '我要报名' }}
                </button>
                <span class="participants-count">{{ activity.participants }} 人已报名</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 内容贡献 -->
      <div v-if="activeTab === 'contributions'" class="contributions-content">
        <div class="contribution-form">
          <h2>贡献您的文化资源</h2>
          <form @submit.prevent="submitContribution">
            <div class="form-group">
              <label for="contribution-title">标题</label>
              <input type="text" id="contribution-title" v-model="contribution.title" required placeholder="请输入资源标题" />
            </div>
            <div class="form-group">
              <label for="contribution-category">分类</label>
              <select id="contribution-category" v-model="contribution.category" required>
                <option value="">请选择分类</option>
                <option value="历史遗迹">历史遗迹</option>
                <option value="传统艺术">传统艺术</option>
                <option value="文学作品">文学作品</option>
                <option value="民俗风情">民俗风情</option>
                <option value="饮食文化">饮食文化</option>
                <option value="建筑风格">建筑风格</option>
              </select>
            </div>
            <div class="form-group">
              <label for="contribution-description">描述</label>
              <textarea id="contribution-description" v-model="contribution.description" required rows="4" placeholder="请详细描述您要分享的文化资源"></textarea>
            </div>
            <div class="form-group">
              <label for="contribution-image">上传图片 (可选)</label>
              <input type="file" id="contribution-image" accept="image/*" @change="handleImageUpload" />
            </div>
            <button type="submit" class="submit-btn">提交贡献</button>
          </form>
        </div>
        
        <div class="contribution-guidelines">
          <h3>贡献指南</h3>
          <ul>
            <li>请确保您分享的内容与湖湘文化相关</li>
            <li>请勿上传侵犯他人版权的内容</li>
            <li>内容将经过审核后才会发布到平台上</li>
            <li>优质贡献者将获得平台颁发的荣誉证书</li>
          </ul>
        </div>
      </div>

      <!-- 意见反馈 -->
      <div v-if="activeTab === 'feedback'" class="feedback-content">
        <div class="feedback-form">
          <h2>给我们留言</h2>
          <form @submit.prevent="submitFeedback">
            <div class="form-group">
              <label for="feedback-type">反馈类型</label>
              <select id="feedback-type" v-model="feedback.type" required>
                <option value="">请选择反馈类型</option>
                <option value="建议">功能建议</option>
                <option value="bug">问题反馈</option>
                <option value="compliment">表扬鼓励</option>
                <option value="other">其他</option>
              </select>
            </div>
            <div class="form-group">
              <label for="feedback-content">反馈内容</label>
              <textarea id="feedback-content" v-model="feedback.content" required rows="5" placeholder="请详细描述您的反馈内容"></textarea>
            </div>
            <div class="form-group">
              <label for="feedback-contact">联系方式 (可选)</label>
              <input type="text" id="feedback-contact" v-model="feedback.contact" placeholder="邮箱或电话，方便我们回复您" />
            </div>
            <button type="submit" class="submit-btn">提交反馈</button>
          </form>
        </div>
        
        <div class="recent-feedback" v-if="recentFeedback.length > 0">
          <h3>近期反馈回复</h3>
          <div v-for="item in recentFeedback" :key="item.id" class="feedback-item">
            <div class="feedback-header">
              <span class="feedback-type">{{ item.type }}</span>
              <span class="feedback-date">{{ formatDate(item.date) }}</span>
            </div>
            <p class="feedback-question">{{ item.question }}</p>
            <div class="feedback-reply" v-if="item.reply">
              <p><strong>管理员回复:</strong> {{ item.reply }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { request } from '../services/api.js'

export default {
  name: 'CommunityPage',
  props: {
    showAlert: {
      type: Function,
      default: null
    }
  },
  setup(props) {
    const router = useRouter()
    
    // 状态管理
    const activeTab = ref('forum')
    const currentPage = ref(1)
    const forumSortBy = ref('latest')
    const forumPages = ref(1)
    const totalPages = ref(1)
    const totalPosts = ref(0)
    const loading = ref(false)
    
    // 我的帖子相关状态
    const myPosts = ref([])
    const myCurrentPage = ref(1)
    const myTotalPages = ref(1)
    const myPostsLoading = ref(false)
    
    // 论坛帖子数据
    const forumPosts = ref([]) // 论坛帖子列表

    // 获取我的帖子数据
    const fetchMyPosts = async () => {
      try {
        myPostsLoading.value = true
        
        // 获取当前用户信息
        const storedUser = localStorage.getItem('user')
        if (!storedUser) {
          throw new Error('请先登录')
        }
        
        const user = JSON.parse(storedUser)
        const response = await request(`/posts?page=${myCurrentPage.value}&per_page=10`, 'GET')
        
        if (response && response.success) {
          // 过滤出当前用户发布的帖子
          const userPosts = (response.posts || []).filter(post => post.author.id === user.id)
          myPosts.value = userPosts
          myTotalPages.value = response.pages || 1
        } else {
          console.error('API响应错误:', response);
          throw new Error(response.message || response.error || '获取我的帖子失败')
        }
      } catch (error) {
        console.error('获取我的帖子失败:', error)
        if (props.showAlert) {
          props.showAlert(error.message || '获取我的帖子失败', 'error')
        }
        myPosts.value = []
      } finally {
        myPostsLoading.value = false
      }
    }
    
    // 获取帖子数据
    const fetchForumPosts = async () => {
      try {
        loading.value = true
        
        const response = await request(`/posts?page=${currentPage.value}&per_page=5`, 'GET')
        
        console.log('API响应数据:', response); // 添加调试信息
        
        if (response && response.success) {
          forumPosts.value = response.posts || []
          totalPages.value = response.pages || 1
          totalPosts.value = response.total || 0
          
          console.log(`获取到 ${forumPosts.value.length} 个帖子`); // 添加调试信息
        } else {
          console.error('API响应错误:', response);
          throw new Error(response.message || response.error || '获取帖子失败')
        }
      } catch (error) {
        console.error('获取帖子失败:', error)
        if (props.showAlert) {
          props.showAlert(error.message || '获取帖子失败', 'error')
        }
        forumPosts.value = []
      } finally {
        loading.value = false
      }
    }
    
    // 删除我的帖子
    const deleteMyPost = async (postId, postTitle) => {
      if (!confirm(`确定要删除帖子《${postTitle}》吗？此操作不可撤销。`)) {
        return
      }
      
      try {
        const response = await request(`/posts/${postId}`, 'DELETE')
        
        if (response.success) {
          // 从本地数组中移除该帖子
          myPosts.value = myPosts.value.filter(post => post.id !== postId)
          if (props.showAlert) {
            props.showAlert('帖子删除成功', 'success')
          }
        } else {
          throw new Error(response.message || '删除帖子失败')
        }
      } catch (error) {
        console.error('删除帖子失败:', error)
        if (props.showAlert) {
          props.showAlert(error.message || '删除帖子失败', 'error')
        }
      }
    }
    
    // 编辑我的帖子
    const editMyPost = (postId) => {
      router.push(`/edit-post/${postId}`)
    }
    
    // 跳转到我的帖子指定页
    const goToMyPage = (page) => {
      if (page >= 1 && page <= myTotalPages.value && page !== myCurrentPage.value) {
        myCurrentPage.value = page
        fetchMyPosts()
      }
    }
    
    // 获取我的帖子页码
    const getMyPageNumbers = () => {
      const delta = 2
      const range = []
      const start = Math.max(1, myCurrentPage.value - delta)
      const end = Math.min(myTotalPages.value, myCurrentPage.value + delta)
      
      if (start > 1) {
        range.push(1)
        if (start > 2) range.push('...')
      }
      
      for (let i = start; i <= end; i++) {
        range.push(i)
      }
      
      if (end < myTotalPages.value) {
        if (end < myTotalPages.value - 1) range.push('...')
        range.push(myTotalPages.value)
      }
      
      return range
    }
    
    // 计算当前页显示的帖子
    const displayedPosts = computed(() => {
      console.log(`计算显示的帖子数: ${forumPosts.value.length}`); // 添加调试信息
      return forumPosts.value
    })
    
    // 获取当前用户是否已登录
    const isLoggedIn = computed(() => {
      const storedUser = localStorage.getItem('user')
      return !!storedUser
    })
    
    // 检查当前用户是否为帖子作者
    const isPostOwner = (post) => {
      if (!isLoggedIn.value || !post.author) return false
      
      const currentUser = JSON.parse(localStorage.getItem('user') || '{}')
      return post.author.id === currentUser.id
    }
    
    // 编辑帖子
    const editPost = (postId) => {
      // 再次确认用户有权限编辑此帖子
      const token = localStorage.getItem('access_token');
      if (!token) {
        alert('请先登录后再编辑帖子');
        router.push('/login');
        return;
      }
      
      router.push(`/edit-post/${postId}`);
    }
    
    // 确认删除帖子
    const confirmDeletePost = async (postId, postTitle) => {
      if (!confirm(`确定要删除帖子《${postTitle}》吗？此操作不可撤销。`)) {
        return
      }
      
      try {
        const response = await request(`/posts/${postId}`, 'DELETE')
        
        if (response.success) {
          // 从列表中移除该帖子
          forumPosts.value = forumPosts.value.filter(post => post.id !== postId)
          if (props.showAlert) {
            props.showAlert('帖子删除成功', 'success')
          }
        } else {
          throw new Error(response.message || '删除帖子失败')
        }
      } catch (error) {
        console.error('删除帖子失败:', error)
        if (props.showAlert) {
          props.showAlert(error.message || '删除帖子失败', 'error')
        }
      }
    }
    
    // 分页相关计算
    const getPageNumbers = () => {
      const delta = 2
      const range = []
      const start = Math.max(1, currentPage.value - delta)
      const end = Math.min(totalPages.value, currentPage.value + delta)
      
      if (start > 1) {
        range.push(1)
        if (start > 2) range.push('...')
      }
      
      for (let i = start; i <= end; i++) {
        range.push(i)
      }
      
      if (end < totalPages.value) {
        if (end < totalPages.value - 1) range.push('...')
        range.push(totalPages.value)
      }
      
      return range
    }
    
    // 跳转到指定页
    const goToPage = (page) => {
      if (page === '...') return
      
      if (page >= 1 && page <= totalPages.value && page !== currentPage.value) {
        currentPage.value = page
        fetchForumPosts() // 获取新页面的数据
      }
    }
    
    // 切换标签
    const switchTab = (tab) => {
      activeTab.value = tab
      
      // 根据当前标签加载相应内容
      if (tab === 'forum') {
        // 总是获取最新数据
        currentPage.value = 1; // 重置到第一页
        fetchForumPosts()
      } else if (tab === 'my-posts' && isLoggedIn.value) {
        // 获取当前用户自己的帖子
        myCurrentPage.value = 1; // 重置到第一页
        fetchMyPosts()
      } else if (tab === 'activities') {
        fetchActivities()
      }
    }
    
    // 监听帖子创建事件
    const handlePostCreated = (event) => {
      console.log('收到帖子创建事件:', event.detail); // 添加调试信息
      // 如果当前在论坛标签页，刷新帖子列表
      if (activeTab.value === 'forum') {
        console.log('正在刷新帖子列表...');
        fetchForumPosts();
      }
    }
    
    // 组件挂载后初始化
    onMounted(() => {
      console.log('社区页面挂载');
      // 默认显示论坛
      switchTab('forum')
      
      // 监听帖子创建事件
      window.addEventListener('postCreated', handlePostCreated)
    })
    
    // 组件卸载前清理事件监听器
    onUnmounted(() => {
      console.log('移除社区页面事件监听器');
      window.removeEventListener('postCreated', handlePostCreated)
    })
    
    // 方法：创建新帖子
    const createNewPost = () => {
      router.push('/create-post')
    }
    
    // 方法：查看帖子详情
    const viewPostDetails = (postId) => {
      router.push(`/post-detail/${postId}`)
    }
    
    // 方法：论坛帖子排序
    const sortForumPosts = () => {
      // 根据选择的排序方式对帖子进行排序
      if (forumSortBy.value === 'latest') {
        forumPosts.value.sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
      } else if (forumSortBy.value === 'popular') {
        forumPosts.value.sort((a, b) => (b.views || 0) - (a.views || 0))
      } else if (forumSortBy.value === 'comments') {
        forumPosts.value.sort((a, b) => (b.comments_count || 0) - (a.comments_count || 0))
      }
    }
    
    // 方法：截断文本
    const truncateText = (text, maxLength) => {
      if (!text) return ''
      return text.length > maxLength ? text.substring(0, maxLength) + '...' : text
    }
    
    // 方法：格式化日期
    const formatDate = (dateString) => {
      const date = new Date(dateString)
      return date.toLocaleDateString('zh-CN', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      })
    }

    // 文化活动数据
    const activities = ref([])
    
    // 获取文化活动数据
    const fetchActivities = async () => {
      try {
        // 尝试从API获取真实活动数据
        const response = await request('/activities', 'GET')
        if (response.success) {
          activities.value = response.activities || []
        } else {
          // 如果API没有活动数据或API调用失败，使用模拟数据作为后备
          loadMockActivities()
        }
      } catch (error) {
        console.warn('获取真实活动数据失败，加载模拟数据:', error)
        // API调用失败时使用模拟数据
        loadMockActivities()
      }
    }
    
    // 加载模拟活动数据
    const loadMockActivities = () => {
      activities.value = [
        {
          id: '1',
          title: '湖湘文化艺术节',
          description: '一场集音乐、舞蹈、戏剧、美术于一体的综合性文化艺术盛宴，展示湖湘文化的独特魅力。',
          imageUrl: 'https://picsum.photos/seed/artfestival/400/300',
          startDate: '2023-07-15',
          endDate: '2023-07-20',
          location: '长沙市湖南大剧院',
          participants: 356,
          isJoined: false
        },
        {
          id: '2',
          title: '岳麓书院文化讲堂',
          description: '邀请知名学者讲解湖湘文化的历史渊源和当代价值，欢迎广大文化爱好者参与。',
          imageUrl: 'https://picsum.photos/seed/culturelecture/400/300',
          startDate: '2023-07-22',
          endDate: '2023-07-22',
          location: '长沙市岳麓书院',
          participants: 189,
          isJoined: false
        },
        {
          id: '3',
          title: '湘绣技艺体验工作坊',
          description: '由资深湘绣艺人亲自指导，让参与者亲身体验湘绣的制作过程，感受传统工艺的魅力。',
          imageUrl: 'https://picsum.photos/seed/xiangxiu/400/300',
          startDate: '2023-08-05',
          endDate: '2023-08-05',
          location: '湖南省博物馆',
          participants: 120,
          isJoined: false
        }
      ]
    }

    // 内容贡献数据
    const contribution = ref({
      title: '',
      category: '',
      description: '',
      image: null
    })

    // 意见反馈数据
    const feedback = ref({
      type: '',
      content: '',
      contact: ''
    })

    // 近期反馈
    const recentFeedback = ref([
      {
        id: '1',
        type: '功能建议',
        question: '能否增加一个收藏功能，方便用户保存感兴趣的文章？',
        reply: '感谢您的建议！收藏功能已经在开发计划中，预计下个月上线。',
        date: '2023-06-10'
      },
      {
        id: '2',
        type: '问题反馈',
        question: '移动端浏览时图片加载较慢，希望能够优化',
        reply: '您好，我们已经注意到这个问题，技术团队正在进行图片加载优化，预计下周完成。',
        date: '2023-06-08'
      }
    ])

    // 方法：报名活动
    const joinActivity = (activityId) => {
      const activity = activities.value.find(a => a.id === activityId)
      if (activity) {
        if (activity.isJoined) {
          if (props.showAlert) {
            props.showAlert('您已取消报名该活动', 'success')
          }
          activity.isJoined = false
          activity.participants--
        } else {
          if (props.showAlert) {
            props.showAlert('报名成功！我们将通过站内信通知您活动详情', 'success')
          }
          activity.isJoined = true
          activity.participants++
        }
      }
    }

    // 方法：提交内容贡献
    const submitContribution = () => {
      if (props.showAlert) {
        props.showAlert('感谢您的贡献！我们将尽快审核您提交的内容', 'success')
      }
      // 重置表单
      contribution.value = {
        title: '',
        category: '',
        description: '',
        image: null
      }
    }

    // 方法：处理图片上传
    const handleImageUpload = (event) => {
      const file = event.target.files[0]
      if (file) {
        contribution.value.image = file
      }
    }

    // 方法：提交反馈
    const submitFeedback = () => {
      if (props.showAlert) {
        props.showAlert('感谢您的反馈！我们会认真对待每一条建议', 'success')
      }
      // 重置表单
      feedback.value = {
        type: '',
        content: '',
        contact: ''
      }
    }

    // 方法：格式化活动日期
    const formatActivityDate = (dateString) => {
      const date = new Date(dateString)
      const month = date.getMonth() + 1
      const day = date.getDate()
      return `${month}月${day}日`
    }

    // 初始化时加载帖子和活动
    onMounted(() => {
      fetchForumPosts()
      fetchActivities()  // 添加这一行以获取活动数据
    })

    return {
      activeTab,
      currentPage,
      forumSortBy,
      forumPages,
      forumPosts,
      displayedPosts,
      activities,
      contribution,
      feedback,
      recentFeedback,
      totalPages,
      loading,
      myPosts,
      myCurrentPage,
      myTotalPages,
      myPostsLoading,
      isLoggedIn,
      isPostOwner,
      switchTab,
      createNewPost,
      viewPostDetails,
      sortForumPosts,
      goToPage,
      getPageNumbers,
      deleteMyPost,
      editMyPost,
      goToMyPage,
      getMyPageNumbers,
      fetchMyPosts,
      editPost,
      confirmDeletePost,
      joinActivity,
      submitContribution,
      handleImageUpload,
      submitFeedback,
      formatDate,
      formatActivityDate,
      truncateText
    }
  }
}
</script>

<style scoped>
.community-page {
  padding: 2rem 0;
}

.page-header {
  background-size: cover;
  background-position: center;
  color: white;
  padding: 2rem 0;
  text-align: center;
  margin-top: 20px;
}

.page-header h1 {
  color: black;
  font-size: 2.5rem;
  margin-bottom: 1rem;
}

.page-header p {
  color: black;
  font-size: 1.2rem;
  max-width: 800px;
  margin: 0 auto;
}

.community-nav {
  display: flex;
  margin: 2rem 0;
  background-color: #f8f9fa;
  border-radius: 8px;
  overflow: hidden;
}

.nav-tab {
  flex: 1;
  background-color: transparent;
  border: none;
  padding: 1rem;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
  gap: 0.5rem;
}

.nav-tab:hover {
  background-color: #e9ecef;
}

.nav-tab.active {
  background-color: var(--primary-color);
  color: white;
}

/* 论坛样式 */
.forum-content,
.my-posts-content {
  background: #f8f9fa;
  padding: 1.5rem;
  border-radius: 12px;
  min-height: 500px;
}

.forum-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.create-post-btn {
  background-color: var(--primary-color);
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  cursor: pointer;
  border-radius: 4px;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: background-color 0.3s;
}

.create-post-btn:hover {
  background-color: var(--primary-dark);
}

.forum-filters select {
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  background-color: white;
}

.posts-list {
  margin-top: 1rem;
}

.post-item {
  margin-bottom: 0;
}

.post-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
  padding: 1.5rem;
  margin-bottom: 1.5rem;
  transition: all 0.3s ease;
  cursor: pointer;
  border: 1px solid #eee;
}

.post-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
  border-color: #4a90e2;
}

.post-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid #eee;
}

.post-author {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.author-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  object-fit: cover;
}

.author-info {
  display: flex;
  flex-direction: column;
}

.author-name {
  font-weight: bold;
  color: #333;
  font-size: 0.95rem;
}

.post-date {
  font-size: 0.8rem;
  color: #999;
}

.post-stats {
  display: flex;
  gap: 1.25rem;
  align-items: center;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 0.3rem;
  font-size: 0.85rem;
  color: #666;
}

.post-tags {
  margin-bottom: 0.75rem;
}

.post-category {
  background-color: #e3f2fd;
  color: #1976d2;
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 500;
}

.post-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #333;
  margin: 0.5rem 0 0.75rem;
}

.post-excerpt {
  color: #666;
  line-height: 1.6;
}

.loading-posts {
  text-align: center;
  padding: 2rem;
  color: #666;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 0.5rem;
  margin-top: 2rem;
}

.pagination-btn {
  padding: 0.5rem 1rem;
  border: 1px solid #ddd;
  background: white;
  cursor: pointer;
  border-radius: 4px;
  transition: all 0.3s;
}

.pagination-btn:hover:not(:disabled) {
  background: #f0f0f0;
}

.pagination-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-number {
  padding: 0.5rem 0.75rem;
  border: 1px solid #ddd;
  background: white;
  cursor: pointer;
  border-radius: 4px;
  transition: all 0.3s;
}

.page-number:hover {
  background: #f0f0f0;
}

.page-number.active {
  background: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
}

.empty-state {
  text-align: center;
  padding: 3rem;
  color: #999;
}

.post-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #eee;
}

.action-btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.3s;
}

.edit-btn {
  background-color: #ffc107;
  color: #212529;
}

.edit-btn:hover {
  background-color: #e0a800;
}

.delete-btn {
  background-color: #dc3545;
  color: white;
}

.delete-btn:hover {
  background-color: #bd2130;
}

/* 活动和贡献部分的样式 */
.activities-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1.5rem;
  margin-top: 1.5rem;
}

.activity-card {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
  transition: transform 0.3s;
}

.activity-card:hover {
  transform: translateY(-5px);
}

.activity-image {
  position: relative;
  height: 200px;
  overflow: hidden;
}

.activity-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.activity-date {
  position: absolute;
  top: 1rem;
  right: 1rem;
  background: var(--primary-color);
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  font-weight: bold;
}

.activity-info {
  padding: 1.5rem;
}

.activity-title {
  font-size: 1.25rem;
  font-weight: 600;
  margin: 0 0 0.75rem;
  color: #333;
}

.activity-location {
  color: #666;
  margin: 0.5rem 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.activity-description {
  color: #666;
  line-height: 1.6;
  margin: 1rem 0;
}

.activity-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 1rem;
}

.activity-btn {
  background: var(--primary-color);
  color: white;
  border: none;
  padding: 0.5rem 1.5rem;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.activity-btn:hover {
  background: var(--primary-dark);
}

.participants-count {
  color: #666;
  font-size: 0.9rem;
}

.contribution-form,
.feedback-form {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  margin-bottom: 2rem;
}

.contribution-guidelines {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
}

.contribution-guidelines h3 {
  margin-top: 0;
  margin-bottom: 1rem;
  color: #333;
}

.contribution-guidelines ul {
  padding-left: 1.5rem;
  color: #666;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #333;
}

.form-group input,
.form-group textarea,
.form-group select {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
  transition: border-color 0.3s;
}

.form-group input:focus,
.form-group textarea:focus,
.form-group select:focus {
  outline: none;
  border-color: var(--primary-color);
}

.submit-btn {
  background: var(--primary-color);
  color: white;
  border: none;
  padding: 0.75rem 2rem;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.submit-btn:hover {
  background: var(--primary-dark);
}

.recent-feedback {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  margin-top: 1.5rem;
}

.feedback-item {
  padding: 1rem 0;
  border-bottom: 1px solid #eee;
}

.feedback-item:last-child {
  border-bottom: none;
}

.feedback-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
}

.feedback-type {
  background: #e3f2fd;
  color: #1976d2;
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.8rem;
}

.feedback-date {
  color: #999;
  font-size: 0.8rem;
}

.feedback-question {
  margin: 0 0 0.5rem;
  color: #666;
}

.feedback-reply {
  padding: 0.75rem;
  background: #f8f9fa;
  border-radius: 4px;
  border-left: 3px solid var(--primary-color);
}

/* 响应式设计 */
@media (max-width: 992px) {
  .contributions-content,
  .feedback-content {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .container {
    padding: 0 0.5rem;
  }
  
  .community-nav {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .nav-tab {
    text-align: center;
  }
  
  .forum-actions {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }
  
  .post-item {
    padding: 1rem;
  }
  
  .post-header {
    flex-direction: column;
    gap: 1rem;
    align-items: flex-start;
  }
  
  .post-stats {
    align-self: flex-end;
  }
  
  .pagination {
    gap: 0.25rem;
  }
  
  .pagination-btn {
    padding: 0.25rem 0.75rem;
    font-size: 0.9rem;
  }
}
</style>