<template>
  <div class="creator-page">
    <h2>📖 绘本创作者中心</h2>

    <div class="card">
      <h3>✨ 使用大模型生成绘本</h3>
      <input v-model="title" placeholder="请输入绘本标题" />
      <input v-model="topic" placeholder="请输入主题，例如：小红帽剧情" />
      <button @click="handleGenerate" :disabled="loading">
        {{ loading ? "生成中..." : "🚀 让AI生成故事" }}
      </button>
    </div>

    <div v-if="storyContent" class="card">
      <h3>✏️ 生成结果（可编辑）</h3>
      <textarea v-model="storyContent" rows="8"></textarea>
      <div class="btns">
        <button @click="handleSaveDraft">💾 保存草稿</button>
        <button @click="handleSubmitReview">✅ 提交审核</button>
      </div>
    </div>

    <div class="card">
      <h3>📋 我的作品</h3>
      <div v-for="item in myList" :key="item.id" class="item">
        <div>{{ item.title }}</div>
        <div>状态：
          <span v-if="item.status === 'draft'">草稿</span>
          <span v-if="item.status === 'pending'">审核中</span>
          <span v-if="item.status === 'pass'">已发布</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { generateStory, saveDraft, submitReview, getMyStories } from '@/api'

// 从本地存储读取【用户登录时输入的用户名】
const user = ref(JSON.parse(localStorage.getItem('user') || '{}'))
const title = ref('')
const topic = ref('')
const storyContent = ref('')
const loading = ref(false)
const myList = ref([])

// AI 生成故事（真正调用 LLM）
async function handleGenerate() {
  if (!topic.value) {
    alert("请输入故事主题")
    return
  }
  loading.value = true
  storyContent.value = ""
  try {
    const res = await generateStory(topic.value)
    storyContent.value = res.data.content
  } catch (err) {
    alert("生成失败，请确保后端已启动")
    console.error(err)
  } finally {
    loading.value = false
  }
}

// 保存草稿
async function handleSaveDraft() {
  if (!user.value.username) {
    alert("请先登录")
    return
  }
  await saveDraft({
    title: title.value,
    content: storyContent.value,
    author: user.value.username
  })
  alert("保存草稿成功")
  getMyListData()
}

// 提交审核
async function handleSubmitReview() {
  if (!user.value.username) {
    alert("请先登录")
    return
  }
  await saveDraft({
    title: title.value,
    content: storyContent.value,
    author: user.value.username
  })
  const res = await getMyStories(user.value.username)
  const latest = res.data.at(-1)
  await submitReview({ id: latest.id })
  alert("提交审核成功")
  getMyListData()
}

// 获取我的作品
async function getMyListData() {
  if (!user.value.username) return
  const res = await getMyStories(user.value.username)
  myList.value = res.data
}

onMounted(() => {
  getMyListData()
})
</script>

<style scoped>
.creator-page {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}
.btns {
  display: flex;
  gap: 10px;
  margin-top: 12px;
}
.item {
  padding: 10px 0;
  border-bottom: 1px solid var(--border-color);
}
</style>