<template>
  <div class="creator-page">
    <div class="creator-card">
      <h2>✨ AI 绘本创作</h2>

      <!-- 步骤1：标题 -->
      <div class="form-item">
        <label>📖 绘本标题</label>
        <input v-model="title" placeholder="例如：小兔子的一天" />
      </div>

      <!-- 步骤2：故事草稿（可选） -->
      <div class="form-item">
        <label>✏️ 故事草稿（可选，AI会帮你优化）</label>
        <textarea v-model="storyDraft" rows="3" placeholder="简单写一下想讲的故事..."></textarea>
      </div>

      <!-- 步骤3：年龄段 -->
      <div class="form-item">
        <label>👶 适合年龄段</label>
        <select v-model="ageGroup">
          <option value="2-4">2-4岁（超简单）</option>
          <option value="5-7">5-7岁（简单）</option>
          <option value="8+">8岁以上（丰富）</option>
        </select>
      </div>

      <!-- 步骤4：页数 -->
      <div class="form-item">
        <label>📄 页数</label>
        <select v-model="pageCount">
          <option value="3">3页</option>
          <option value="4">4页</option>
          <option value="5">5页</option>
          <option value="6">6页</option>
        </select>
      </div>

      <!-- 步骤5：阅读权限 -->
      <div class="form-item">
        <label>🔒 阅读权限</label>
        <select v-model="isVipOnly">
          <option :value="false">📖 免费阅读（所有人可见）</option>
          <option :value="true">👑 会员专享（仅VIP可读）</option>
        </select>
      </div>

      <!-- 步骤6：主角形象描述 -->
      <div class="form-item">
        <label>🐰 主角形象描述</label>
        <textarea 
          v-model="characterDesc" 
          rows="2" 
          placeholder="例如：一只穿着超人披风的彩虹小马"
        ></textarea>
        <div class="char-hint">💡 描述越详细，AI生成的图片越符合你的想象</div>
      </div>

      <!-- 随机生成按钮 -->
      <button class="random-char-btn" @click="randomCharacter">🎲 随机示例</button>

      <!-- 生成按钮 -->
      <button class="generate-btn" @click="generateBook" :disabled="loading">
        {{ loading ? "创作中..." : "🚀 开始创作绘本" }}
      </button>

      <!-- 编辑区域：生成后显示 -->
      <div v-if="book.pages && book.pages.length > 0" class="result-section">
        <h3>📝 编辑绘本（可修改文字和图片）</h3>

        <!-- 标题编辑 -->
        <div class="edit-title">
          <label>绘本标题</label>
          <input v-model="book.title" />
        </div>

        <!-- 每一页的编辑区 -->
        <div v-for="(page, idx) in book.pages" :key="idx" class="page-edit">
          <div class="page-header">
            <span class="page-num">📄 第 {{ idx+1 }} 页</span>
          </div>

          <!-- 文字编辑区 -->
          <label>📝 故事文字</label>
          <textarea v-model="page.text" rows="2" placeholder="编辑故事文字..."></textarea>

          <!-- 图片显示区（带loading） -->
          <label>🎨 绘本插图</label>
          <div class="image-container">
            <!-- 加载中 -->
            <div v-if="page.imageLoading" class="loading-wrapper">
              <div class="loading-spinner"></div>
              <p>🎨 AI 正在创作插画...</p>
              <p class="loading-tip">可能需要几秒钟，请稍等~</p>
            </div>
            
            <!-- 图片显示 -->
            <img 
              v-show="!page.imageLoading && page.image"
              :src="page.image" 
              :alt="`第${idx+1}页插图`"
              @load="page.imageLoading = false"
              @error="() => handleImageError(page, idx)"
            />
            
            <!-- 无图片占位 -->
            <div v-if="!page.imageLoading && !page.image" class="image-placeholder">
              🖼️ 暂无图片
            </div>
          </div>

          <!-- 手动重新生成图片按钮 -->
          <button 
            class="regenerate-btn" 
            @click="regenerateImage(idx)" 
            :disabled="page.regenerating"
          >
            {{ page.regenerating ? "生成中..." : "🔄 根据当前文字重新生成图片" }}
          </button>
        </div>

        <!-- 发布按钮 -->
        <button class="publish-btn" @click="publishBook" :disabled="publishing">
          {{ publishing ? "发布中..." : "✅ 发布并阅读" }}
        </button>
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
import axios from 'axios'
import { useRouter } from 'vue-router'

const router = useRouter()

// 表单数据
const title = ref('')
const storyDraft = ref('')
const ageGroup = ref('5-7')
const pageCount = ref('4')
const loading = ref(false)
const publishing = ref(false)
const isVipOnly = ref(false)

// 主角形象描述
const characterDesc = ref('一只白色的小兔子，穿着蓝色背带裤')

// 绘本数据
const book = ref({
  title: '',
  pages: []
})

// 随机生成示例描述
const randomCharacter = () => {
  const examples = [
    '一只白色的小兔子，穿着蓝色背带裤，戴着红色蝴蝶结',
    '一只棕色的小熊，围着黄色围巾，手里拿着一罐蜂蜜',
    '一只橙色的小狐狸，穿着魔法师袍子，戴着尖顶帽',
    '一只灰色的小刺猬，背着绿色小书包，戴着小眼镜',
    '一只黄色的小鸭子，戴着蓝色小帽子，穿着水手服',
    '一只粉色的小猫，穿着公主裙，头上戴着蝴蝶结',
    '一只白色的小狗，穿着超人披风，脚踩滑板',
    '一只棕色的小松鼠，抱着一个大橡果，穿着小背心'
  ]
  characterDesc.value = examples[Math.floor(Math.random() * examples.length)]
}

// 生成绘本
const generateBook = async () => {
  if (!title.value) {
    alert('请输入绘本标题')
    return
  }
  
  loading.value = true
  try {
    const res = await axios.post('http://127.0.0.1:8000/generate-book', {
      topic: title.value,
      outline: storyDraft.value,
      ageGroup: ageGroup.value,
      pageCount: parseInt(pageCount.value),
      character_desc: characterDesc.value,
      is_vip_only: isVipOnly.value
    })

    book.value = {
      title: res.data.title,
      pages: res.data.pages.map(p => ({ 
        ...p, 
        regenerating: false,
        imageLoading: false
      }))
    }
    
    alert(`生成成功！共${book.value.pages.length}页，可继续编辑`)
  } catch (err) {
    console.error('生成失败', err)
    alert('生成失败：' + (err.response?.data?.detail || err.message))
  } finally {
    loading.value = false
  }
}

// 重新生成单页图片
const regenerateImage = async (idx) => {
  const page = book.value.pages[idx]
  
  page.regenerating = true
  page.imageLoading = true
  page.image = ''
  
  try {
    const res = await axios.post('http://127.0.0.1:8000/refresh-image', {
      text: page.text
    })
    page.image = res.data.image
  } catch (err) {
    page.imageLoading = false
    page.regenerating = false
    alert('生成失败')
  }
}

// 图片加载失败处理
const handleImageError = (page, idx) => {
  page.imageLoading = false
  page.regenerating = false
  console.warn(`第${idx+1}页图片加载失败`)
  page.image = `https://picsum.photos/400/400?random=${idx}`
}

// 发布到书库
const publishBook = async () => {
  if (!book.value.title || book.value.pages.length === 0) {
    alert('请先生成绘本')
    return
  }
  
  publishing.value = true
  try {
    const res = await axios.post('http://127.0.0.1:8000/save-book-from-editor', {
      title: book.value.title,
      pages: book.value.pages.map(p => ({
        text: p.text,
        image: p.image
      })),
      userId: localStorage.getItem('userId') || 'test'
    })
    
    alert('发布成功！')
    router.push(`/read/${res.data.bookId}`)
  } catch (err) {
    console.error('发布失败', err)
    alert('发布失败：' + (err.response?.data?.detail || err.message))
  } finally {
    publishing.value = false
  }
}
</script>

<style scoped>
.creator-page {
  background: #fdfbf6;
  min-height: 100vh;
  padding: 30px 20px 80px;
}

.creator-card {
  background: #ffffff;
  border-radius: 24px;
  padding: 30px;
  max-width: 700px;
  margin: 0 auto;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

h2, h3 {
  color: #444444;
  text-align: center;
}

.form-item {
  margin-bottom: 20px;
}

label {
  display: block;
  margin-bottom: 8px;
  color: #666;
  font-size: 14px;
  font-weight: 500;
}

input, select, textarea {
  width: 100%;
  padding: 12px;
  border-radius: 12px;
  border: 1px solid #eeeeee;
  box-sizing: border-box;
  font-size: 14px;
  font-family: inherit;
}

input:focus, select:focus, textarea:focus {
  outline: none;
  border-color: #ffb74d;
}

.char-hint {
  font-size: 12px;
  color: #999;
  margin-top: 5px;
}

.random-char-btn {
  background: #ffd48f;
  color: #666;
  border: none;
  padding: 8px 16px;
  border-radius: 20px;
  cursor: pointer;
  font-size: 12px;
  margin-bottom: 20px;
}

.generate-btn, .publish-btn {
  width: 100%;
  padding: 14px;
  background: #ffb74d;
  color: white;
  border: none;
  border-radius: 12px;
  margin-top: 10px;
  font-size: 16px;
  cursor: pointer;
  transition: background 0.2s;
}

.generate-btn:hover, .publish-btn:hover {
  background: #ffa01e;
}

.generate-btn:disabled, .publish-btn:disabled {
  background: #ffd48f;
  cursor: not-allowed;
}

/* 编辑区域 */
.result-section {
  margin-top: 30px;
  border-top: 2px solid #ffd48f;
  padding-top: 20px;
}

.edit-title {
  margin-bottom: 20px;
}

.edit-title input {
  font-size: 16px;
  font-weight: bold;
}

.page-edit {
  background: #faf8f5;
  border-radius: 16px;
  padding: 16px;
  margin-bottom: 20px;
}

.page-header {
  margin-bottom: 12px;
}

.page-num {
  font-weight: bold;
  color: #ffb74d;
  font-size: 16px;
}

.page-edit label {
  margin-top: 10px;
  margin-bottom: 5px;
  font-size: 12px;
  color: #888;
}

.page-edit textarea {
  background: white;
  margin-bottom: 10px;
}

/* 图片容器 */
.image-container {
  min-height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f0f0f0;
  border-radius: 12px;
  margin: 10px 0;
  overflow: hidden;
}

.loading-wrapper {
  text-align: center;
  padding: 30px;
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

.loading-wrapper p {
  margin: 5px 0;
  color: #ffb74d;
  font-size: 14px;
}

.loading-tip {
  font-size: 12px;
  color: #999;
}

.image-container img {
  max-width: 100%;
  max-height: 300px;
  border-radius: 8px;
}

.image-placeholder {
  padding: 40px;
  text-align: center;
  color: #999;
}

.regenerate-btn {
  width: 100%;
  padding: 10px;
  background: #ffb74d;
  color: white;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  margin-top: 10px;
}

.regenerate-btn:hover:not(:disabled) {
  background: #ffa01e;
}

.regenerate-btn:disabled {
  background: #ffd48f;
  cursor: not-allowed;
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