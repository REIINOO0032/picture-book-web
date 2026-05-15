<template>
  <div class="edit-page">
    <h2>✏️ 编辑绘本</h2>

    <div class="title-input">
      <label>绘本标题：</label>
      <input v-model="bookTitle" @blur="saveTitle" />
    </div>

    <div class="pages-list" v-if="pages.length > 0">
      <div class="page-item" v-for="(page, idx) in pages" :key="idx">
        <h4>第{{ idx + 1 }}页</h4>
        <textarea v-model="page.content" rows="3" @blur="savePageText(page)"></textarea>

        <div class="img-preview">
          <img :src="page.image_url" alt="插画" />
          <div class="img-text">{{ page.content }}</div>
        </div>

        <button @click="refreshImage(page)" :disabled="refreshing">
          {{ refreshing ? "生成中..." : "🔄 刷新图片" }}
        </button>
      </div>
    </div>

    <div class="button-group">
      <button class="back-btn" @click="goBack">📚 返回书库</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'

const route = useRoute()
const router = useRouter()

const bookId = ref('')
const bookTitle = ref('')
const pages = ref([])
const refreshing = ref(false)

// 从数据库加载绘本
const loadBook = async () => {
  if (route.params.id) {
    bookId.value = route.params.id
  } else if (route.query.bookId) {
    bookId.value = route.query.bookId
  } else {
    alert('缺少绘本ID')
    router.back()
    return
  }

  try {
    const res = await axios.get(`http://127.0.0.1:8000/book/${bookId.value}`)
    bookTitle.value = res.data.title
    pages.value = res.data.pages || []
  } catch (err) {
    alert('加载失败：' + (err.response?.data?.detail || err.message))
    router.back()
  }
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

// 保存单页文字
const savePageText = async (page) => {
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

// 刷新图片
const refreshImage = async (page) => {
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

const goBack = () => {
  router.push('/profile')
}

onMounted(() => {
  loadBook()
})
</script>

<style scoped>
.edit-page {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
  padding-bottom: 80px;
  background: #fdfbf6;
  min-height: 100vh;
}
h2 {
  text-align: center;
  color: #444;
}
.title-input {
  margin-bottom: 20px;
}
.title-input input {
  width: 100%;
  padding: 10px;
  border: 1px solid #ffd48f;
  border-radius: 12px;
  background: #fffef8;
  box-sizing: border-box;
}
.page-item {
  background: white;
  border: 1px solid #eee;
  padding: 15px;
  margin-bottom: 15px;
  border-radius: 12px;
}
.page-item textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid #ffd48f;
  border-radius: 8px;
  font-family: inherit;
  resize: vertical;
  box-sizing: border-box;
}
.img-preview {
  position: relative;
  width: fit-content;
  margin: 10px 0;
}
.img-preview img {
  max-width: 200px;
  border-radius: 8px;
}
.img-text {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: rgba(0, 0, 0, 0.6);
  color: white;
  text-align: center;
  padding: 6px;
  font-size: 12px;
  border-bottom-left-radius: 8px;
  border-bottom-right-radius: 8px;
}
.page-item button {
  background: #ffb74d;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 20px;
  cursor: pointer;
}
.button-group {
  position: fixed;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
}
.back-btn {
  background: #ffb74d;
  color: white;
  border: none;
  padding: 12px 30px;
  border-radius: 30px;
  cursor: pointer;
}
</style>