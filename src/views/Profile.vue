<template>
  <div class="profile-container">
    <el-card class="user-card" shadow="hover">
      <div class="user-info">
        <el-avatar :size="80" src="https://picsum.photos/200/200" />
        <div class="user-text">
          <h2>{{ displayName }}</h2>
          <p>儿童绘本创作者 / 读者</p>
          <div style="display: flex; gap: 6px; margin-top: 4px">
            <el-tag type="success" size="small">已实名认证</el-tag>
            <el-tag size="small" :type="isVip ? 'success' : 'warning'">
              {{ isVip ? '🌟 会员' : '普通用户' }}
            </el-tag>
          </div>
          <el-button
            v-if="!isVip"
            type="warning"
            size="small"
            style="margin-top: 10px"
            @click="$router.push('/vip')"
          >
            开通会员
          </el-button>
        </div>
      </div>
    </el-card>

    <el-card style="margin-bottom:20px;">
      <h4 style="margin:0 0 8px 0;">🌟 会员专属权益</h4>
      <div>• 无限次 AI 绘本创作</div>
      <div>• 全站绘本自由阅读，无试读限制</div>
      <div>• 会员专属精美绘本资源</div>
      <div>• 内容优先审核</div>
    </el-card>

    <el-card class="income-card" style="margin-bottom:20px;">
      <h3 style="margin:0 0 10px 0;">💰 作者收益中心</h3>
      <div style="font-size:24px; font-weight:bold; color:#ffb74d;">
        ¥{{ earnings.total.toFixed(2) }}
      </div>
      <div style="margin-top:12px; display: flex; gap: 20px;">
        <div>
          <div style="font-size:12px; color:#999;">会员订阅分成</div>
          <div style="font-size:18px; font-weight:bold;">¥{{ earnings.vipShare.toFixed(2) }}</div>
        </div>
        <div>
          <div style="font-size:12px; color:#999;">绘本阅读奖励</div>
          <div style="font-size:18px; font-weight:bold;">¥{{ earnings.readReward.toFixed(2) }}</div>
        </div>
      </div>
    </el-card>

    <div class="menu-grid">
      <el-card class="menu-item" @click="activeTab = 1">
        <div class="icon">📖</div><span>阅读历史</span>
      </el-card>
      <el-card class="menu-item" @click="activeTab = 2">
        <div class="icon">✏️</div><span>我的创作</span>
      </el-card>
      <el-card class="menu-item" @click="activeTab = 3">
        <div class="icon">⭐</div><span>我的收藏</span>
      </el-card>
      <el-card class="menu-item" @click="activeTab = 4">
        <div class="icon">⚙️</div><span>账号设置</span>
      </el-card>
    </div>

    <el-card class="content-card">
      <!-- 阅读历史 -->
      <div v-if="activeTab === 1">
        <h3>阅读历史</h3>
        <el-empty description="暂无记录" />
      </div>

      <!-- 我的创作 -->
      <div v-if="activeTab === 2">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
          <h3>我的创作</h3>
          <el-button type="primary" size="small" @click="$router.push('/creation')">+ 新创作</el-button>
        </div>
        
        <el-empty v-if="myBooks.length === 0" description="还没有创作过绘本，去创作一本吧！">
          <el-button type="primary" @click="$router.push('/creation')">开始创作</el-button>
        </el-empty>
        
        <div v-else class="book-list">
          <div v-for="book in myBooks" :key="book.book_id" class="book-item">
            <div class="book-info" style="flex: 1;">
              <h4>📖 {{ book.title }}</h4>
              <p>🆔 ID：{{ book.book_id }}</p>
              <p>📅 创作时间：{{ formatDate(book.create_time) }}</p>
              <p>👁️ 阅读量：{{ book.click_count || 0 }} 次</p>
            </div>
            <div class="book-actions">
              <el-button size="small" type="primary" @click.stop="goToRead(book.book_id)">阅读</el-button>
              <el-button size="small" type="warning" @click.stop="goToEdit(book.book_id)">编辑</el-button>
              
              <div class="vip-switch-item" @click.stop>
                <span class="vip-label">🔒 {{ book.is_vip_only ? '会员专享' : '免费' }}</span>
                <el-switch 
                  v-model="book.is_vip_only" 
                  active-text="会员"
                  inactive-text="免费"
                  @change="(val) => toggleVipStatus(book, val)"
                  size="small"
                />
              </div>
              
              <el-button size="small" type="danger" @click.stop="deleteBook(book.book_id)">删除</el-button>
            </div>
          </div>
        </div>
      </div>

      <!-- 我的收藏 -->
      <div v-if="activeTab === 3">
        <h3>我的收藏</h3>
        <el-empty description="暂无收藏" />
      </div>

      <!-- 账号设置 -->
      <div v-if="activeTab === 4">
        <h3>账号设置</h3>
        <el-form label-width="100px">
          <el-form-item label="昵称">
            <el-input v-model="form.name" placeholder="请输入昵称" />
          </el-form-item>
          <el-form-item label="家长管控">
            <el-switch v-model="form.parentControl" />
          </el-form-item>
          <el-form-item>
            <el-button 
              @click="saveToDatabase"
              style="background:#68cff8; border-color:#68cff8; color:#fff;">
              保存设置
            </el-button>
            <el-button type="default" @click="logout">退出登录</el-button>
            <el-button type="danger" @click="deleteAccount">注销账号</el-button>
          </el-form-item>
        </el-form>
      </div>
    </el-card>

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
import { ref, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const activeTab = ref(2)
const userId = ref('')
const form = ref({ name: '', parentControl: true })
const isVip = ref(false)
const myBooks = ref([])

// 收益数据
const earnings = ref({
  total: 0,
  vipShare: 0,
  readReward: 0
})

// 显示昵称（优先使用用户设置的昵称，否则用 localStorage 中的 username）
const displayName = computed(() => {
  return form.value.name || localStorage.getItem('username') || '用户'
})

// 格式化日期
const formatDate = (dateStr) => {
  if (!dateStr) return '未知'
  const date = new Date(dateStr)
  return `${date.getFullYear()}/${date.getMonth() + 1}/${date.getDate()}`
}

// 加载用户创作的绘本
const loadMyBooks = async () => {
  if (!userId.value) return
  try {
    const res = await axios.get(`http://127.0.0.1:8000/user/books?userId=${userId.value}`)
    myBooks.value = res.data || []
  } catch (err) {
    console.error('加载绘本失败', err)
  }
}

// 加载收益数据
const loadEarnings = async () => {
  if (!userId.value) return
  try {
    const res = await axios.get(`http://127.0.0.1:8000/user/earnings?userId=${userId.value}`)
    earnings.value = res.data || { total: 0, vipShare: 0, readReward: 0 }
  } catch (err) {
    console.error('加载收益失败', err)
  }
}

// 跳转阅读
const goToRead = (bookId) => {
  const userId = localStorage.getItem('userId') || ''
  router.push(`/read/${bookId}?userId=${userId}`)
}

// 跳转编辑
const goToEdit = (bookId) => {
  router.push(`/edit/${bookId}`)
}

// 删除绘本
const deleteBook = async (bookId) => {
  try {
    await ElMessageBox.confirm('确定要删除这本绘本吗？删除后无法恢复。', '警告', {
      confirmButtonText: '确定删除',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await axios.post(`http://127.0.0.1:8000/book/delete/${bookId}`)
    ElMessage.success('删除成功')
    await loadMyBooks()
  } catch (err) {
    if (err !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

// 切换会员状态
const toggleVipStatus = async (book, isVipOnly) => {
  try {
    await axios.post('http://127.0.0.1:8000/book/update-vip-status', {
      bookId: book.book_id,
      userId: userId.value,
      isVipOnly: isVipOnly
    })
    ElMessage.success(`已设为${isVipOnly ? '会员专享' : '免费'}`)
  } catch (err) {
    ElMessage.error('修改失败：' + (err.response?.data?.detail || err.message))
    book.is_vip_only = !isVipOnly
  }
}

// 保存昵称
const saveToDatabase = async () => {
  if (!form.value.name.trim()) {
    ElMessage.warning('昵称不能为空')
    return
  }

  try {
    await axios.post('http://127.0.0.1:8000/user/update-name', {
      userId: userId.value,
      newName: form.value.name.trim()
    })
    ElMessage.success('保存成功！')
    localStorage.setItem('username', form.value.name.trim())
  } catch (err) {
    ElMessage.error('保存失败，请检查后端是否启动')
  }
}

// 退出登录
const logout = () => {
  ElMessageBox.confirm('确定要退出当前账号吗？', '退出登录', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'info'
  }).then(() => {
    localStorage.clear()
    ElMessage.success('退出成功')
    router.push('/login')
  }).catch(() => {})
}

// 注销账号
const deleteAccount = () => {
  ElMessageBox.confirm('⚠️ 注销后账号将永久删除，所有数据不可恢复！', '注销账号', {
    confirmButtonText: '确定删除',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    axios.post(`http://127.0.0.1:8000/user/delete?userId=${userId.value}`).catch(console.error)
    localStorage.clear()
    ElMessage.success('账号已注销')
    router.push('/login')
  }).catch(() => {})
}

onMounted(async () => {
  const uid = localStorage.getItem('userId')
  if (!uid) {
    router.push('/login')
    return
  }
  userId.value = uid

  // 获取用户信息
  try {
    const res = await axios.get('http://127.0.0.1:8000/user/info', {
      params: { userId: uid }
    })
    if (res.data.username) {
      form.value.name = res.data.username
      localStorage.setItem('username', res.data.username)
    }
  } catch (e) {
    console.log('加载用户信息失败', e)
  }

  // 获取会员状态
  const vip = localStorage.getItem('isVip')
  isVip.value = vip === 'true'
  
  // 监听会员状态变化
  window.addEventListener('focus', () => {
    const newVip = localStorage.getItem('isVip')
    isVip.value = newVip === 'true'
  })
  
  // 加载数据
  await loadMyBooks()
  await loadEarnings()
})
</script>

<style scoped>
.profile-container {
  max-width: 900px;
  margin: 0 auto;
  padding: 20px;
  padding-bottom: 80px;
}
.user-card {
  margin-bottom: 20px;
  border-radius: 12px;
  padding: 20px;
}
.user-info {
  display: flex;
  align-items: center;
  gap: 20px;
}
.menu-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
  margin-bottom: 20px;
}
.menu-item {
  text-align: center;
  padding: 16px;
  cursor: pointer;
  border-radius: 10px;
  border: 1px solid #eee;
  transition: 0.2s;
}
.menu-item:hover {
  border-color: #ffb74d;
  background: #faf8f5;
}
.icon {
  font-size: 28px;
  margin-bottom: 6px;
  color: #ffb74d;
}
.content-card {
  border-radius: 12px;
  min-height: 300px;
  padding: 20px;
}
.income-card {
  padding: 16px;
  border-radius: 12px;
}

.book-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.book-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  border: 1px solid #eee;
  border-radius: 12px;
  background: white;
  transition: all 0.2s;
}
.book-item:hover {
  background: #faf8f5;
  border-color: #ffb74d;
}
.book-info h4 {
  margin: 0 0 8px 0;
  font-size: 16px;
  color: #333;
}
.book-info p {
  margin: 4px 0;
  font-size: 12px;
  color: #888;
}
.book-actions {
  display: flex;
  gap: 8px;
  align-items: center;
  flex-wrap: wrap;
}
.vip-switch-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}
.vip-label {
  font-size: 10px;
  color: #666;
}

.bottom-nav {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  display: flex;
  justify-content: space-around;
  align-items: center;
  background: #fff;
  border-top: 1px solid #eee;
  padding: 10px 0;
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
