<template>
  <div class="search-page">
    <div class="search-header">
      <h2>🔍 搜索绘本</h2>
      <div class="search-bar">
        <input 
          type="text" 
          v-model="keyword" 
          placeholder="输入绘本名称或关键词..."
          @keyup.enter="searchBooks"
          autofocus
        />
        <button @click="searchBooks" :disabled="loading">
          {{ loading ? "搜索中..." : "搜索" }}
        </button>
      </div>
    </div>

    <!-- 加载中 -->
    <div v-if="loading" class="loading-state">
      <div class="loading-spinner"></div>
      <p>搜索中...</p>
    </div>

    <!-- 搜索结果 -->
    <div v-else-if="searchResults.length > 0" class="search-results">
      <div class="result-header">
        <span>找到 {{ searchResults.length }} 本绘本</span>
        <span v-if="keyword">关键词：{{ keyword }}</span>
      </div>
      
      <div class="book-list">
        <div 
          v-for="book in searchResults" 
          :key="book.book_id" 
          class="book-item"
          @click="goToRead(book.book_id)"
        >
          <img :src="book.cover_url || 'https://picsum.photos/300/400'" class="book-cover" />
          <div class="book-info">
            <h4>{{ book.title }}</h4>
            <p>👤 {{ book.author || '匿名用户' }}</p>
            <div class="book-tags">
              <el-tag size="small" :type="book.is_vip_only ? 'warning' : 'info'">
                {{ book.is_vip_only ? '👑 会员专享' : '📖 免费' }}
              </el-tag>
              <span class="book-stats">🔥 {{ book.click_count || 0 }} 次阅读</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 无结果 -->
    <div v-else-if="searched && searchResults.length === 0" class="empty-state">
      <p>😢 没有找到与「{{ keyword }}」相关的绘本</p>
      <button @click="$router.push('/creation')">去创作一本吧</button>
    </div>

    <!-- 初始状态 -->
    <div v-else class="empty-state">
      <p>📚 输入关键词，搜索你喜欢的绘本</p>
      <div class="hot-keywords">
        <span>热门推荐：</span>
        <span v-for="hot in hotKeywords" :key="hot" @click="keyword = hot; searchBooks()">
          {{ hot }}
        </span>
      </div>
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
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const router = useRouter()
const keyword = ref('')
const loading = ref(false)
const searched = ref(false)
const searchResults = ref([])

const hotKeywords = ['小兔子', '小熊', '友谊', '魔法', '森林']

// 搜索绘本
const searchBooks = async () => {
  if (!keyword.value.trim()) {
    ElMessage.warning('请输入搜索关键词')
    return
  }
  
  loading.value = true
  searched.value = true
  
  try {
    const userId = localStorage.getItem('userId') || ''
    const res = await axios.get('http://127.0.0.1:8000/books/search', {
      params: {
        keyword: keyword.value,
        userId: userId
      }
    })
    searchResults.value = res.data || []
  } catch (err) {
    console.error('搜索失败', err)
    ElMessage.error('搜索失败')
    searchResults.value = []
  } finally {
    loading.value = false
  }
}

// 跳转阅读
const goToRead = (bookId) => {
  const userId = localStorage.getItem('userId') || ''
  router.push(`/read/${bookId}?userId=${userId}`)
}
</script>

<style scoped>
.search-page {
  background: #fdfbf6;
  min-height: 100vh;
  padding: 20px 20px 80px;
}

.search-header {
  text-align: center;
  margin-bottom: 30px;
}

.search-header h2 {
  color: #444;
  margin-bottom: 20px;
}

.search-bar {
  display: flex;
  max-width: 500px;
  margin: 0 auto;
  gap: 10px;
}

.search-bar input {
  flex: 1;
  padding: 12px 16px;
  border: 1px solid #ffd48f;
  border-radius: 30px;
  font-size: 16px;
  outline: none;
  background: white;
}

.search-bar input:focus {
  border-color: #ffb74d;
  box-shadow: 0 0 0 2px rgba(255, 183, 77, 0.2);
}

.search-bar button {
  padding: 12px 24px;
  background: #ffb74d;
  color: white;
  border: none;
  border-radius: 30px;
  cursor: pointer;
  font-size: 16px;
}

.search-bar button:hover {
  background: #ffa01e;
}

.search-bar button:disabled {
  background: #ffd48f;
  cursor: not-allowed;
}

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

.search-results {
  max-width: 600px;
  margin: 0 auto;
}

.result-header {
  display: flex;
  justify-content: space-between;
  padding: 10px 0;
  color: #888;
  font-size: 14px;
  border-bottom: 1px solid #eee;
  margin-bottom: 15px;
}

.book-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.book-item {
  display: flex;
  gap: 15px;
  background: white;
  border-radius: 16px;
  padding: 12px;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.book-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.book-cover {
  width: 80px;
  height: 100px;
  object-fit: cover;
  border-radius: 8px;
  background: #f0f0f0;
}

.book-info {
  flex: 1;
}

.book-info h4 {
  margin: 0 0 8px 0;
  font-size: 16px;
  color: #333;
}

.book-info p {
  margin: 5px 0;
  font-size: 13px;
  color: #888;
}

.book-tags {
  display: flex;
  gap: 10px;
  align-items: center;
  margin-top: 8px;
}

.book-stats {
  font-size: 12px;
  color: #ffb74d;
}

.empty-state {
  text-align: center;
  padding: 50px;
  color: #999;
}

.empty-state button {
  background: #ffb74d;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 25px;
  margin-top: 15px;
  cursor: pointer;
}

.hot-keywords {
  margin-top: 20px;
}

.hot-keywords span {
  display: inline-block;
  background: white;
  padding: 6px 14px;
  border-radius: 20px;
  margin: 5px;
  cursor: pointer;
  border: 1px solid #ffd48f;
  transition: all 0.2s;
}

.hot-keywords span:hover {
  background: #ffb74d;
  color: white;
}

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