<template>
  <div class="vip-page">
    <div class="page-header">
      <h1>选择适合您的方案</h1>
      <p>解锁更多创作与阅读权益</p>
    </div>

    <div class="plans-grid">
      <!-- 免费版卡片 -->
      <div class="plan-card">
        <div class="plan-title">免费版</div>
        <div class="price">免费</div>
        <div class="desc">基础功能</div>
        <button class="btn-free" :disabled="!isVip" @click="switchToFree">
          {{ !isVip ? '当前方案' : '切换到此方案' }}
        </button>
        <div class="features">
          <div class="feature">✅ 每日3次AI创作</div>
          <div class="feature">✅ 免费绘本试读</div>
          <div class="feature">❌ 会员专属绘本</div>
          <div class="feature">❌ 优先审核通道</div>
        </div>
      </div>

      <!-- 会员版卡片 -->
      <div class="plan-card featured">
        <div class="hot-tag">推荐</div>
        <div class="plan-title">会员版</div>
        <div class="price">¥19.9 / 月</div>
        <div class="desc">全部功能解锁</div>
        <button class="btn-vip" @click="openVip" :disabled="isVip">
          {{ isVip ? '已是会员' : '立即开通' }}
        </button>
        <div class="features">
          <div class="feature">✅ 无限次AI创作</div>
          <div class="feature">✅ 全站绘本全本阅读</div>
          <div class="feature">✅ 会员专属绘本资源</div>
          <div class="feature">✅ 内容优先审核通道</div>
        </div>
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
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'

const route = useRoute()
const router = useRouter()
const isVip = ref(false)

// 检查会员状态
const checkVipStatus = () => {
  isVip.value = localStorage.getItem('isVip') === 'true'
}

// 开通会员
const openVip = async () => {
  if (isVip.value) return
  
  // 获取来源绘本ID（从URL参数）
  const fromBookId = route.query.from_book_id || ''
  
  try {
    // 调用后端开通接口
    const res = await axios.post('http://127.0.0.1:8000/vip/open', {
      userId: localStorage.getItem('userId'),
      from_book_id: fromBookId
    })
    
    if (res.data.code === 200) {
      localStorage.setItem('isVip', 'true')
      isVip.value = true
      ElMessage.success('会员开通成功！')
      
      // 如果是从绘本来的，返回绘本页
      if (fromBookId) {
        router.push(`/read/${fromBookId}`)
      } else {
        router.push('/profile')
      }
    } else {
      ElMessage.error(res.data.msg || '开通失败')
    }
  } catch (err) {
    console.error('开通失败', err)
    ElMessage.error('开通失败，请稍后重试')
  }
}

onMounted(() => {
  checkVipStatus()
})
</script>

<style scoped>
.vip-page {
  background: #fdfbf6;
  min-height: 100vh;
  padding: 30px 20px 80px;
}
.page-header {
  text-align: center;
  margin-bottom: 30px;
}
.page-header h1 {
  margin: 0;
  font-size: 28px;
}
.page-header p {
  color: #888;
}
.plans-grid {
  display: flex;
  gap: 20px;
  max-width: 700px;
  margin: 0 auto;
}
.plan-card {
  flex: 1;
  background: white;
  border-radius: 20px;
  padding: 24px;
  box-shadow: 0 8px 16px rgba(0,0,0,0.08);
  position: relative;
}
.plan-card.featured {
  border: 2px solid #ff9800;
}
.hot-tag {
  position: absolute;
  top: -10px;
  right: 15px;
  background: #ff9800;
  color: white;
  padding: 4px 10px;
  border-radius: 10px;
  font-size: 12px;
}
.plan-title {
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 8px;
}
.price {
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 8px;
}
.desc {
  color: #666;
  margin-bottom: 16px;
}
button {
  width: 100%;
  padding: 12px;
  border-radius: 12px;
  border: none;
  margin-bottom: 16px;
  cursor: pointer;
}
.btn-free {
  background: #eee;
  color: #666;
}
.btn-free:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
.btn-vip {
  background: #ff9800;
  color: white;
}
.btn-vip:disabled {
  background: #ffc46b;
  cursor: not-allowed;
}
.features {
  font-size: 14px;
  line-height: 2;
}
.bottom-nav {
  display: flex;
  justify-content: space-around;
  align-items: center;
  background: #fff;
  border-top: 1px solid #eee;
  padding: 10px 0;
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
}
.nav-item {
  text-align: center;
  font-size: 12px;
  color: #333;
  cursor: pointer;
}
.icon {
  font-size: 20px;
  display: block;
}
</style>