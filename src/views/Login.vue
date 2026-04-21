<template>
  <div class="login-page">
    <el-card class="login-card" shadow="hover">
      <h2 class="title">{{ isRegister ? '用户注册' : '用户登录' }}</h2>

      <el-form label-width="80px" style="margin-top:20px">
        <el-form-item label="账号">
          <el-input v-model="form.username" placeholder="请输入手机号码" />
        </el-form-item>

        <el-form-item label="密码">
          <el-input v-model="form.password" type="password" placeholder="请输入密码" />
        </el-form-item>

        <!-- 注册时才显示 -->
        <el-form-item label="确认密码" v-if="isRegister">
          <el-input v-model="form.confirmPwd" type="password" placeholder="请确认密码" />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" block @click="submit">
            {{ isRegister ? '注册' : '登录' }}
          </el-button>
        </el-form-item>

        <el-form-item>
          <el-button text @click="isRegister = !isRegister">
            {{ isRegister ? '已有账号？去登录' : '没有账号？去注册' }}
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'

const router = useRouter()
const isRegister = ref(false)

const form = ref({
  username: '',
  password: '',
  confirmPwd: ''
})

// 模拟已注册用户列表
const registeredUsers = ref([
  { username: '13800138000', password: '123456' }
])

// 手机号正则验证
const isPhone = (val) => {
  const reg = /^1[3-9]\d{9}$/
  return reg.test(val)
}

// 提交
const submit = () => {
  // 1. 先验证是否为空
  if (!form.value.username || !form.value.password) {
    ElMessage.warning('请输入账号密码')
    return
  }

  // 2. 验证必须是手机号（关键！）
  if (!isPhone(form.value.username)) {
    ElMessage.error('请输入有效的11位手机号码！')
    form.value.username = '' // 清空错误输入
    return
  }

  if (isRegister.value) {
    // 注册流程
    if (form.value.password !== form.value.confirmPwd) {
      ElMessage.error('两次密码不一致')
      return
    }
    registeredUsers.value.push({
      username: form.value.username,
      password: form.value.password
    })
    ElMessage.success('注册成功！请登录')
    isRegister.value = false
    form.value = { username: '', password: '', confirmPwd: '' }
  } else {
    // 登录流程
    const user = registeredUsers.value.find(
      item => item.username === form.value.username && item.password === form.value.password
    )
    if (user) {
      ElMessage.success('登录成功！')
      localStorage.setItem('user', form.value.username)
      router.push('/profile')
    } else {
      ElMessage.error('账号或密码错误，请重新输入')
      form.value.password = ''
    }
  }
}
</script>

<style scoped>
.login-page {
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  /* 统一页面背景 */
  background: var(--bg-page);
}
.login-card {
  width: 420px;
  border-radius: 12px;
  padding: 30px;
  /* 统一卡片样式 */
  background: var(--bg-card);
  border: 1px solid var(--border);
  box-shadow: 0 1px 4px rgba(0,0,0,0.05);
}
.title {
  text-align: center;
  margin: 0;
  /* 统一文字颜色 */
  color: var(--text-dark);
}
</style>