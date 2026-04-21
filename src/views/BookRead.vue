<template>
  <div style="max-width:800px; margin:0 auto; padding:20px;">
    <el-card title="📖 绘本阅读" shadow="hover">

      <!-- 会员状态提示 -->
      <div style="margin-bottom:15px;">
        <el-tag v-if="isVip" type="success">👑 会员可阅读全本</el-tag>
        <el-tag v-else type="warning">普通用户（试读模式）</el-tag>
      </div>

      <!-- 绘本内容 -->
      <div style="text-align:center;">
        <img :src="pages[currentPage]" style="max-width:100%; border-radius:10px;" />
        <div style="margin-top:15px; font-size:16px; line-height:1.8;">
          {{ content[currentPage] }}
        </div>
      </div>

      <!-- 翻页按钮 -->
      <div style="text-align:center; margin-top:20px;">
        <el-button @click="currentPage--" :disabled="currentPage === 0">上一页</el-button>
        <span style="margin:0 10px;">第 {{ currentPage+1 }} / {{ totalPage }} 页</span>
        <el-button @click="nextPage">下一页</el-button>
      </div>

      <!-- 试读限制提示 -->
      <div v-if="!isVip && currentPage >= 1" style="margin-top:15px; text-align:center; color:red;">
        试读结束！开通会员阅读完整绘本
      </div>

    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { onBookRead } from '../utils/authorIncome.js'

const isVip = ref(localStorage.getItem('isVip') === 'true')

// 绘本页数
const totalPage = 5
const currentPage = ref(0)

// 绘本图片 + 内容
const pages = ref([
  "https://picsum.photos/600/400?random=10",
  "https://picsum.photos/600/400?random=11",
  "https://picsum.photos/600/400?random=12",
  "https://picsum.photos/600/400?random=13",
  "https://picsum.photos/600/400?random=14"
])

const content = ref([
  "小兔子在森林里快乐地玩耍",
  "它遇到了好朋友小松鼠",
  "它们一起分享美味的坚果",
  "太阳下山了，它们开心地回家",
  "这是一个温暖又适合小朋友的故事"
])

// 翻页 + 试读限制
const nextPage = () => {
  if (!isVip.value && currentPage.value >= 1) return
  if (currentPage.value < totalPage - 1) currentPage.value++
}

// 阅读完成 → 给作者加收益
onMounted(() => {
  onBookRead()
})
</script>