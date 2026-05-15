<template>
  <div class="home-container">
    <h2>📚 绘本推荐</h2>

    <!-- 加载中 -->
    <div v-if="loading" class="loading-state">
      <div class="loading-spinner"></div>
      <p>加载中...</p>
    </div>

    <div v-else>
      <!-- 最新绘本（大图展示） -->
      <div v-if="latestBook" class="featured-section">
        <div class="section-title">✨ 最新绘本</div>
        <div class="featured-book" @click="goRead(latestBook.book_id)">
          <img :src="latestBook.cover_url || 'https://picsum.photos/400/300'" class="featured-cover" />
          <div class="featured-info">
            <h3>{{ latestBook.title }}</h3>
            <p>👤 {{ latestBook.author }}</p>
            <el-tag size="small" type="info">📅 {{ formatDate(latestBook.create_time) }}</el-tag>
          </div>
        </div>
      </div>

      <!-- 热门推荐 -->
      <div v-if="topBooks.length > 0" class="hot-section">
        <div class="section-title">🔥 热门推荐</div>
        <div class="book-grid">
          <div
            v-for="book in topBooks"
            :key="book.book_id"
            class="book-item"
            @click="goRead(book.book_id)"
          >
            <img :src="book.cover_url || 'https://picsum.photos/300/400'" class="book-cover" />
            <div class="book-title">{{ book.title }}</div>
            <div class="book-author">👤 {{ book.author }}</div>
            <div class="book-stats">🔥 {{ book.click_count || 0 }} 人阅读</div>
          </div>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-if="!latestBook && topBooks.length === 0" class="empty-state">
        <p>📖 暂无绘本，快去创作第一本吧！</p>
        <button class="create-btn" @click="$router.push('/creation')">✨ 开始创作</button>
      </div>
    </div>

    <!-- 底部导航 -->
    <div class="bottom-nav">
      <div class="nav-item" @click="$router.push('/')"><span class="icon">🏠</span><div>首页</div></div>
      <div class="nav-item" @click="$router.push('/search')"><span class="icon">🔍</span><div>搜索</div></div>
      <div class="nav-item" @click="$router.push('/creation')"><span class="icon">✏️</span><div>创作</div></div>
      <div class="nav-item" @click="$router.push('/profile')"><span class="icon">👤</span><div>我的</div></div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const router = useRouter()
const loading = ref(true)
const topBooks = ref([])
const latestBook = ref(null)

// 获取推荐绘本
const fetchRecommendBooks = async () => {
  loading.value = true
  try {
    const userId = localStorage.getItem('userId') || ''
    const res = await axios.get('http://127.0.0.1:8000/books/recommend', {
      params: { userId: userId }
    })
    topBooks.value = res.data.top_books || []
    latestBook.value = res.data.latest_book
  } catch (err) {
    console.error('加载失败', err)
  } finally {
    loading.value = false
  }
}

// 跳转阅读（同时增加点击量）
const goRead = async (bookId) => {
  try {
    const res = await axios.post(`http://127.0.0.1:8000/book/click/${bookId}`)
    if (res.data.converted_to_vip) {
      ElMessage.info('该绘本已达10次阅读，已转为会员专享')
    }
  } catch (err) {
    console.error('统计失败', err)
  }
  const userId = localStorage.getItem('userId') || ''
  router.push(`/read/${bookId}?userId=${userId}`)
}

// 格式化日期
const formatDate = (dateStr) => {
  if (!dateStr) return '未知'
  const date = new Date(dateStr)
  return `${date.getMonth() + 1}/${date.getDate()}`
}

onMounted(() => {
  fetchRecommendBooks()
})
</script>

<style scoped>
.home-container {
  max-width: 900px;
  margin: 0 auto;
  padding: 20px;
  padding-bottom: 80px;
  background: #fdfbf6;
  min-height: 100vh;
}

h2 {
  margin-bottom: 20px;
  font-size: 22px;
  color: #444;
}

/* 章节标题 */
.section-title {
  font-size: 18px;
  font-weight: bold;
  color: #ffb74d;
  margin-bottom: 15px;
  padding-left: 10px;
  border-left: 4px solid #ffb74d;
}

/* 最新绘本区域 */
.featured-section {
  margin-bottom: 30px;
}

.featured-book {
  display: flex;
  gap: 15px;
  background: white;
  border-radius: 16px;
  padding: 15px;
  cursor: pointer;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
  transition: transform 0.2s;
}

.featured-book:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.12);
}

.featured-cover {
  width: 120px;
  height: 120px;
  object-fit: cover;
  border-radius: 12px;
}

.featured-info {
  flex: 1;
}

.featured-info h3 {
  margin: 0 0 8px 0;
  font-size: 16px;
  color: #333;
}

.featured-info p {
  margin: 5px 0;
  font-size: 13px;
  color: #888;
}

/* 热门推荐网格 */
.hot-section {
  margin-bottom: 30px;
}

.book-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 15px;
}

.book-item {
  cursor: pointer;
  background: white;
  border-radius: 12px;
  padding: 10px;
  transition: all 0.2s;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.book-item:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.book-cover {
  width: 100%;
  height: 150px;
  object-fit: cover;
  border-radius: 8px;
  background: #f0f0f0;
}

.book-title {
  margin-top: 8px;
  font-weight: bold;
  font-size: 13px;
  color: #333;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.book-author {
  font-size: 11px;
  color: #999;
  margin-top: 3px;
}

.book-stats {
  font-size: 10px;
  color: #ffb74d;
  margin-top: 4px;
}

/* 加载状态 */
.loading-state {
  text-align: center;
  padding: 50px;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  margin: 0 auto 15px;
  border: 3px solid #ffd48f;
  border-top-color: #ffb74d;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 空状态 */
.empty-state {
  text-align: center;
  padding: 50px;
  color: #999;
}

.create-btn {
  background: #ffb74d;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 25px;
  margin-top: 15px;
  cursor: pointer;
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
</style>