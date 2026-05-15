<template>
  <div class="read-page">
    <!-- 加载中 -->
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <p>加载中...</p>
    </div>

    <!-- 绘本内容 -->
    <div v-else class="book-container">
      <!-- 标题栏 -->
      <div class="title-bar">
        <input v-model="bookTitle" class="title-input" placeholder="绘本标题" @blur="saveTitle" />
      </div>

      <!-- 图片区域 -->
      <div class="image-area">
        <img :src="currentPage.image_url" :alt="`第${currentIndex + 1}页`" />
      </div>

      <!-- 文字区域（可编辑文本框） -->
      <div class="text-area">
        <textarea 
          v-model="currentPage.content" 
          rows="4"
          placeholder="在这里编辑故事文字..."
          @blur="saveCurrentText"
        ></textarea>
      </div>

      <!-- 操作按钮行 -->
      <div class="action-row">
        <button class="refresh-btn" @click="refreshCurrentImage" :disabled="refreshing">
          {{ refreshing ? "生成中..." : "🖼️ 重新生成图片" }}
        </button>
      </div>

      <!-- 翻页控制区 -->
      <div class="nav-area">
        <button 
          class="nav-btn prev-btn" 
          @click="prevPage" 
          :disabled="currentIndex === 0"
        >
          ◀ 上一页
        </button>
        
        <span class="page-info">
          第 {{ currentIndex + 1 }} / {{ totalPages }} 页
        </span>
        
        <button 
          class="nav-btn next-btn" 
          @click="nextPage" 
          :disabled="currentIndex === totalPages - 1"
        >
          下一页 ▶
        </button>
      </div>
    </div>

    <!-- 底部操作栏 -->
    <div class="action-bar">
        <button class="action-btn" @click="goBack">📚 返回书库</button>
        <button v-if="!isVip" class="vip-btn" @click="goToVip">👑 开通会员</button>
    </div>

    <!-- 底部导航 -->
    <div class="bottom-nav">
      <div class="nav-item" @click="$router.push('/')">
        <span class="icon">🏠</span>
        <div>首页</div>
      </div>
      <div class="nav-item" @click="$router.push('/search')">
        <span class="icon">🔍</span>
        <div>搜索</div>
      </div>
      <div class="nav-item" @click="$router.push('/creation')">
        <span class="icon">✏️</span>
        <div>创作</div>
      </div>
      <div class="nav-item" @click="$router.push('/profile')">
        <span class="icon">👤</span>
        <div>我的</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'

const route = useRoute()
const router = useRouter()

// 状态
const loading = ref(true)
const refreshing = ref(false)
const bookId = ref('')
const bookTitle = ref('')
const pages = ref([])
const currentIndex = ref(0)
const isVip = ref(false)  // 新增：会员状态

// 计算属性
const totalPages = computed(() => pages.value.length)
const currentPage = computed(() => pages.value[currentIndex.value] || {})

// 从数据库加载绘本
const loadBook = async (userId) => {
  if (route.params.id) {
    bookId.value = route.params.id
  } else if (route.query.bookId) {
    bookId.value = route.query.bookId
  } else {
    alert('缺少绘本ID')
    router.push('/profile')
    return
  }

  loading.value = true
  try {
    const res = await axios.get(`http://127.0.0.1:8000/book/${bookId.value}`, {
      params: { userId: userId }
    })
    const data = res.data
    bookTitle.value = data.title
    pages.value = data.pages || []
  } catch (err) {
    if (err.response?.status === 403) {
      alert('会员专享绘本，请开通会员后阅读')
      router.push('/vip')
    } else {
      alert('加载绘本失败：' + (err.response?.data?.detail || err.message))
      router.push('/profile')
    }
  } finally {
    loading.value = false
  }
}

// 检查会员状态
const checkVipStatus = () => {
  const vip = localStorage.getItem('isVip')
  isVip.value = vip === 'true'
}

// 跳转会员页（带上绘本ID）
const goToVip = () => {
  router.push(`/vip?from_book_id=${bookId.value}`)
}

// 保存标题
const saveTitle = async () => {
  if (!bookId.value) return
  try {
    await axios.post('http://127.0.0.1:8000/book/update-title', {
      bookId: bookId.value,
      title: bookTitle.value
    })
  } catch (err) {
    console.error('保存标题失败', err)
  }
}

// 保存当前页的文字
const saveCurrentText = async () => {
  const page = currentPage.value
  if (!page.page_id) return
  try {
    await axios.post('http://127.0.0.1:8000/book/update-page', {
      pageId: page.page_id,
      text: page.content
    })
  } catch (err) {
    console.error('保存文字失败', err)
  }
}

// 刷新当前页的图片
const refreshCurrentImage = async () => {
  const page = currentPage.value
  if (!page.page_id) return
  refreshing.value = true
  try {
    const res = await axios.post('http://127.0.0.1:8000/refresh-image', {
      pageId: page.page_id,
      text: page.content
    })
    page.image_url = res.data.image
  } catch (err) {
    alert('刷新图片失败')
  } finally {
    refreshing.value = false
  }
}

// 翻页
const prevPage = () => {
  if (currentIndex.value > 0) currentIndex.value--
}
const nextPage = () => {
  if (currentIndex.value < totalPages.value - 1) currentIndex.value++
}

// 返回书库
const goBack = () => {
  router.push('/profile')
}

// 初始化
onMounted(() => {
  const userId = route.query.userId || localStorage.getItem('userId') || ''
  checkVipStatus()
  loadBook(userId)
})
</script>

<style scoped>
.read-page {
  background: #fdfbf6;
  min-height: 100vh;
  padding: 20px 20px 80px;
}

.loading-container {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 60vh;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #ffd48f;
  border-top-color: #ffb74d;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.book-container {
  max-width: 600px;
  margin: 0 auto;
  background: white;
  border-radius: 24px;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

/* 标题栏 */
.title-bar {
  padding: 16px 20px;
  background: white;
  border-bottom: 1px solid #eee;
}

.title-input {
  width: 100%;
  padding: 8px 12px;
  font-size: 18px;
  font-weight: bold;
  border: 1px solid #ffd48f;
  border-radius: 12px;
  background: #fffef8;
  box-sizing: border-box;
}

.title-input:focus {
  outline: none;
  border-color: #ffb74d;
}

/* 图片区域 */
.image-area {
  width: 100%;
  background: #f5f0e8;
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 400px;
}

.image-area img {
  width: 100%;
  max-height: 500px;
  object-fit: contain;
  display: block;
}

/* 文字区域 */
.text-area {
  padding: 20px;
  border-top: 1px solid #eee;
  border-bottom: 1px solid #eee;
}

.text-area textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid #ffd48f;
  border-radius: 12px;
  font-size: 16px;
  line-height: 1.6;
  font-family: inherit;
  resize: vertical;
  box-sizing: border-box;
  background: #fffef8;
}

.text-area textarea:focus {
  outline: none;
  border-color: #ffb74d;
  box-shadow: 0 0 0 2px rgba(255, 183, 77, 0.2);
}

/* 操作按钮行 */
.action-row {
  padding: 12px 20px;
  border-bottom: 1px solid #eee;
}

.refresh-btn {
  width: 100%;
  background: #ffb74d;
  color: white;
  border: none;
  padding: 10px;
  border-radius: 30px;
  font-size: 14px;
  cursor: pointer;
}

.refresh-btn:hover:not(:disabled) {
  background: #ffa01e;
}

.refresh-btn:disabled {
  background: #ffd48f;
  cursor: not-allowed;
}

/* 翻页控制区 */
.nav-area {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: white;
}

.nav-btn {
  background: #ffb74d;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 30px;
  font-size: 14px;
  cursor: pointer;
}

.nav-btn:hover:not(:disabled) {
  background: #ffa01e;
}

.nav-btn:disabled {
  background: #ffd48f;
  cursor: not-allowed;
  opacity: 0.6;
}

.page-info {
  font-size: 14px;
  color: #888;
  background: #f5f5f5;
  padding: 8px 16px;
  border-radius: 20px;
}

/* 底部操作栏 */
.action-bar {
  max-width: 600px;
  margin: 20px auto 0;
  display: flex;
  gap: 12px;
  padding: 0 20px;
}

.action-btn {
  flex: 1;
  background: #ffb74d;
  color: white;
  border: none;
  padding: 12px;
  border-radius: 30px;
  font-size: 14px;
  cursor: pointer;
}

.action-btn:hover {
  background: #ffa01e;
}

/* 底部导航 */
.bottom-nav {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: white;
  display: flex;
  justify-content: space-around;
  padding: 10px 0;
  border-top: 1px solid #eeeeee;
}

.nav-item {
  text-align: center;
  font-size: 12px;
  color: #777777;
  cursor: pointer;
}

.icon {
  font-size: 20px;
  display: block;
}
/* 会员按钮 */
.vip-btn {
  background: #ff9800;
  color: white;
  border: none;
  padding: 12px;
  border-radius: 30px;
  font-size: 14px;
  cursor: pointer;
}

.vip-btn:hover {
  background: #e68900;
}
</style>