<template>
  <div class="vip-page">
    <!-- 标题栏 -->
    <div class="header">
      <div class="back-btn" @click="$router.back()">←</div>
      <div class="tab-group">
        <span class="tab active">✨ 会员专属权益</span>
      </div>
    </div>

    <!-- 权益图标网格 -->
    <div class="benefit-grid">
      <div class="benefit-item" v-for="(item, index) in benefits" :key="index">
        <div class="icon-circle">
          <span class="icon">{{ item.icon }}</span>
          <span class="crown">👑</span>
        </div>
        <div class="text">{{ item.name }}</div>
      </div>
    </div>

    <!-- 开通按钮区域 -->
    <div class="action-area">
      <div class="payment-tip">✅ 开通后永久生效，解锁全部权益</div>
      <el-button class="open-btn" :disabled="!agree" @click="handleOpenVip">
        立即开通会员
      </el-button>
      <label class="checkbox-label">
        <input type="checkbox" v-model="agree" />
        我已阅读并同意《会员服务协议》
      </label>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { openVip } from '@/api'
import { ElMessage } from 'element-plus'

const router = useRouter()
const agree = ref(false)

// 绘本APP专属权益列表
const benefits = ref([
  { icon: '📖', name: '无限AI绘本创作' },
  { icon: '🎨', name: '全站绘本自由阅读' },
  { icon: '⭐', name: '会员专属精美绘本' },
  { icon: '📝', name: '优先审核通道' },
  { icon: '📈', name: '创作者收益加成' },
  { icon: '📚', name: '独家绘本资源' },
  { icon: '🎁', name: '会员专属活动' },
  { icon: '💬', name: '专属客服支持' },
  { icon: '🎯', name: '定制绘本推荐' },
])

const handleOpenVip = async () => {
  const username = localStorage.getItem('user')
  await openVip(username)
  ElMessage.success('🎉 会员开通成功！已解锁全部权益')
  router.back()
}
</script>

<style scoped>
.vip-page {
  background-color: var(--bg-page);
  min-height: 100vh;
  padding: 20px;
}

.header {
  display: flex;
  align-items: center;
  margin-bottom: 24px;
}
.back-btn {
  font-size: 20px;
  cursor: pointer;
  margin-right: 16px;
}
.tab-group {
  flex: 1;
  text-align: center;
}
.tab {
  font-size: 18px;
  font-weight: bold;
  color: var(--text-dark);
}

.benefit-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin-bottom: 40px;
}
.benefit-item {
  text-align: center;
}
.icon-circle {
  width: 80px;
  height: 80px;
  margin: 0 auto 8px;
  background-color: #fff9e6;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}
.icon {
  font-size: 32px;
}
.crown {
  position: absolute;
  top: -6px;
  left: 8px;
  font-size: 16px;
}
.text {
  font-size: 14px;
  color: var(--text-dark);
}

.action-area {
  position: fixed;
  bottom: 20px;
  left: 20px;
  right: 20px;
  text-align: center;
}
.payment-tip {
  margin-bottom: 12px;
  color: var(--text-light);
}
.open-btn {
  width: 100%;
  height: 50px;
  background-color: #f8d88b;
  color: var(--text-dark);
  border: none;
  border-radius: 25px;
  font-size: 18px;
  font-weight: bold;
}
.open-btn:disabled {
  background-color: #e6e6e6;
}
.checkbox-label {
  display: block;
  margin-top: 12px;
  font-size: 13px;
  color: var(--text-light);
}
</style>