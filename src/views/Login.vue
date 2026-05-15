<template>
  <div class="login-page">
    <el-card class="login-card" shadow="hover">
      <h2 class="title">{{ isRegister ? '用户注册' : '用户登录' }}</h2>

      <el-form label-width="80px" style="margin-top:20px">
        <el-form-item label="手机号">
          <el-input v-model="form.phone" placeholder="请输入手机号码" />
        </el-form-item>

        <!-- 注册时显示昵称输入框 -->
        <el-form-item label="昵称" v-if="isRegister">
          <el-input v-model="form.username" placeholder="请输入昵称" />
        </el-form-item>

        <el-form-item label="密码">
          <el-input v-model="form.password" type="password" placeholder="请输入密码" />
        </el-form-item>

        <el-form-item label="确认密码" v-if="isRegister">
          <el-input v-model="form.confirmPwd" type="password" placeholder="请确认密码" />
        </el-form-item>

        <el-form-item>
          <el-button
            block
            @click="submit"
            style="background:#68cff8; border-color:#68cff8; color:#fff;">
            {{ isRegister ? '注册' : '登录' }}
          </el-button>
        </el-form-item>

        <el-form-item>
          <el-button text @click="toggleMode">
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
import axios from 'axios'

const router = useRouter()
const isRegister = ref(false)

const form = ref({
  phone: '',
  username: '',
  password: '',
  confirmPwd: ''
})

const isPhone = (val) => {
  const reg = /^1[3-9]\d{9}$/
  return reg.test(val)
}

const toggleMode = () => {
  isRegister.value = !isRegister.value
  // 切换模式时清空表单
  form.value = { phone: '', username: '', password: '', confirmPwd: '' }
}

const submit = async () => {
  if (!form.value.phone || !form.value.password) {
    ElMessage.warning('请输入手机号和密码')
    return
  }
  if (!isPhone(form.value.phone)) {
    ElMessage.error('请输入有效的11位手机号码！')
    return
  }

  if (isRegister.value) {
    // 注册
    if (!form.value.username) {
      ElMessage.warning('请输入昵称')
      return
    }
    if (form.value.password !== form.value.confirmPwd) {
      ElMessage.error('两次密码不一致')
      return
    }

    try {
      await axios.post('http://127.0.0.1:8000/user/register', {
        phone: form.value.phone,
        username: form.value.username,
        password: form.value.password
      })
      ElMessage.success('注册成功！请登录')
      toggleMode()
    } catch (err) {
      console.error('注册失败', err)
      ElMessage.error(err.response?.data?.detail || '注册失败')
    }

  } else {
    // 登录
    try {
      const res = await axios.post('http://127.0.0.1:8000/user/login', {
        phone: form.value.phone,
        password: form.value.password
      })
      
      console.log('登录返回数据:', res.data)
      
      localStorage.setItem('userId', res.data.userId)
      localStorage.setItem('username', res.data.username)
      localStorage.setItem('phone', res.data.phone)
      localStorage.setItem('isVip', res.data.isVip)
      
      ElMessage.success('登录成功！')
      router.push('/profile')
    } catch (err) {
      console.error('登录失败', err)
      ElMessage.error(err.response?.data?.detail || '手机号或密码错误')
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
  background: #fdfbf6;
}
.login-card {
  width: 420px;
  border-radius: 12px;
  padding: 30px;
  background: white;
  border: 1px solid #eee;
}
.title {
  text-align: center;
  color: #444;
}
</style>