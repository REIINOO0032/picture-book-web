<template>
  <div class="home-container" style="max-width: 900px; margin: 0 auto; padding: 20px;">
    <h2 style="margin-bottom: 20px; font-size: 22px;">📚 绘本推荐</h2>

    <div class="book-grid">
      <div
        v-for="book in bookList"
        :key="book.id"
        class="book-item"
        @click="goRead(book.id)"
      >
        <img :src="book.cover" class="book-cover" />
        <div class="book-title">{{ book.title }}</div>
        <el-tag
          size="small"
          style="margin-top: 6px;"
          :type="book.vipOnly ? 'success' : 'info'"
        >
          {{ book.vipOnly ? '👑 会员专享' : '免费阅读' }}
        </el-tag>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
const router = useRouter()

// 绘本列表
const bookList = [
  {
    id: 1,
    title: '小兔子的一天',
    cover: 'https://picsum.photos/300/400?random=1',
    vipOnly: false
  },
  {
    id: 2,
    title: '小松鼠的朋友',
    cover: 'https://picsum.photos/300/400?random=2',
    vipOnly: false
  },
  {
    id: 3,
    title: '森林里的冒险',
    cover: 'https://picsum.photos/300/400?random=3',
    vipOnly: true
  },
  {
    id: 4,
    title: '晚安，月亮',
    cover: 'https://picsum.photos/300/400?random=4',
    vipOnly: false
  }
]

// 点击进入阅读页
const goRead = (bookId) => {
  router.push('/read/' + bookId)
}
</script>

<style scoped>
.book-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.book-item {
  cursor: pointer;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
  transition: 0.2s;
  padding: 10px;
}

.book-item:hover {
  transform: translateY(-4px);
}

.book-cover {
  width: 100%;
  height: 220px;
  object-fit: cover;
  border-radius: 8px;
}

.book-title {
  margin-top: 10px;
  font-weight: bold;
  font-size: 15px;
  text-align: center;
}
</style>