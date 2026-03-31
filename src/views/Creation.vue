<template>
  <div class="creation-page" style="padding: 20px; max-width: 900px; margin: 0 auto">
    <h2 style="text-align: center; margin-bottom: 20px">✏️ AI 儿童绘本创作</h2>

    <el-card style="margin-bottom: 15px">
      <div style="display: flex; justify-content: space-between; align-items: center">
        <div>
          <span v-if="userInfo.isVip">👑 会员用户</span>
          <span v-else>普通用户（每日免费 3 次）</span>
          <div style="margin-top: 5px">今日剩余次数：{{ userInfo.leftCount }}</div>
        </div>
        <el-button type="warning" v-if="!userInfo.isVip" @click="handleOpenVip">
          开通会员
        </el-button>
      </div>
    </el-card>

    <el-card shadow="hover" style="margin-bottom: 20px">
      <el-form label-width="100px">
        <el-form-item label="故事内容">
          <el-input
            v-model="storyText"
            type="textarea"
            :rows="6"
            placeholder="请输入适合幼儿的故事内容..."
          />
        </el-form-item>

        <el-form-item label="关键词" v-if="keywords.length > 0">
          <el-tag
            v-for="(kw, idx) in keywords"
            :key="idx"
            type="primary"
            style="margin-right: 6px"
          >{{ kw }}</el-tag>
        </el-form-item>

        <el-form-item label="绘本风格">
          <el-select v-model="style" style="width: 100%">
            <el-option label="卡通风" value="cartoon" />
            <el-option label="水彩风" value="watercolor" />
            <el-option label="简笔画风" value="simple" />
            <el-option label="童话风" value="fairytale" />
          </el-select>
        </el-form-item>

        <el-form-item label="适用年龄">
          <el-select v-model="age" style="width: 100%">
            <el-option label="3-6岁" value="3-6" />
            <el-option label="7-10岁" value="7-10" />
          </el-select>
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            block
            :loading="generating"
            @click="generateStory"
          >
            {{ generating ? '生成中...' : '🚀 开始生成绘本' }}
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card v-if="book.pages.length > 0" title="📖 绘本预览" shadow="hover">
      <div style="margin-bottom: 10px">
        审核状态：
        <el-tag v-if="auditStatus === 'pending'" type="warning">待审核</el-tag>
        <el-tag v-else-if="auditStatus === 'pass'" type="success">已通过（适合幼儿）</el-tag>
        <el-tag v-else type="danger">已驳回（内容不适宜）</el-tag>
      </div>

      <div style="text-align: center">
        <img
          :src="book.pages[currentPage].image"
          style="max-width: 100%; border-radius: 8px"
          alt="绘本页"
        />
        <div style="margin-top: 10px; font-size: 16px; line-height: 1.6">
          {{ book.pages[currentPage].text }}
        </div>
      </div>

      <div style="text-align: center; margin-top: 15px">
        <el-button @click="currentPage--" :disabled="currentPage === 0">上一页</el-button>
        <span style="margin: 0 10px">第 {{ currentPage + 1 }} / {{ book.pages.length }} 页</span>
        <el-button @click="currentPage++" :disabled="currentPage === book.pages.length - 1">下一页</el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import {
  checkContent,
  getUserInfo,
  addGenerateCount,
  openVip
} from '../utils/permission'

const storyText = ref('')
const style = ref('cartoon')
const age = ref('3-6')
const generating = ref(false)
const currentPage = ref(0)
const book = ref({ pages: [] })
const keywords = ref([])
const userInfo = ref({})
const auditStatus = ref('')

onMounted(() => {
  userInfo.value = getUserInfo()
})

watch(storyText, (val) => {
  if (!val || val.length < 10) {
    keywords.value = []
    return
  }
  const stopWords = ['的', '了', '在', '是', '和', '有', '我', '你', '他']
  let arr = val
    .split(/[，。！？；\s]/)
    .filter((w) => w.length >= 2 && !stopWords.includes(w))
  keywords.value = [...new Set(arr)].slice(0, 6)
})

const handleOpenVip = () => {
  openVip()
  userInfo.value = getUserInfo()
  ElMessage.success('已开通会员，无限创作')
}

const generateStory = () => {
  const ui = getUserInfo()
  if (ui.leftCount <= 0) {
    ElMessage.warning('今日次数已用完，可开通会员')
    return
  }
  if (!storyText.value.trim()) {
    ElMessage.warning('请输入故事内容')
    return
  }

  const check = checkContent(storyText.value)
  if (!check.pass) {
    auditStatus.value = 'reject'
    ElMessage.error(`内容违规：包含“${check.word}”，不适宜幼儿`)
    return
  }

  generating.value = true
  auditStatus.value = 'pending'

  setTimeout(() => {
    book.value = {
      title: 'AI 绘本',
      pages: [
        {
          image: 'https://picsum.photos/600/400?random=1',
          text: storyText.value.slice(0, 30) + '...'
        },
        {
          image: 'https://picsum.photos/600/400?random=2',
          text: '故事继续，温馨有趣的情节。'
        },
        {
          image: 'https://picsum.photos/600/400?random=3',
          text: '故事结尾，适合小朋友的正能量结局。'
        }
      ]
    }
    auditStatus.value = 'pass'
    addGenerateCount()
    userInfo.value = getUserInfo()
    generating.value = false
    ElMessage.success('绘本生成完成，内容已通过审核')
  }, 1500)
}
</script>