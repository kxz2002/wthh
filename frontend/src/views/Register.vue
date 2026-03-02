<template>
  <div class="register-container">
    <div class="register-box">
      <h1>家庭圈用户识别系统</h1>
      <h2>注册</h2>
      <form @submit.prevent="handleRegister">
        <div class="form-group">
          <label for="username">用户名</label>
          <input
            id="username"
            v-model="username"
            type="text"
            placeholder="请输入用户名"
            required
          />
        </div>
        <div class="form-group">
          <label for="password">密码</label>
          <input
            id="password"
            v-model="password"
            type="password"
            placeholder="请输入密码（至少6位）"
            required
          />
        </div>
        <div class="form-group">
          <label for="password_confirm">确认密码</label>
          <input
            id="password_confirm"
            v-model="password_confirm"
            type="password"
            placeholder="请再次输入密码"
            required
          />
        </div>
        <div v-if="error" class="error-message">{{ error }}</div>
        <div v-if="success" class="success-message">{{ success }}</div>
        <button type="submit" :disabled="loading">
          {{ loading ? '注册中...' : '注册' }}
        </button>
      </form>
      <div class="links">
        <router-link to="/login">已有账号？立即登录</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { authAPI } from '@/api'

const router = useRouter()
const username = ref('')
const password = ref('')
const password_confirm = ref('')
const error = ref('')
const success = ref('')
const loading = ref(false)

const handleRegister = async () => {
  error.value = ''
  success.value = ''

  if (password.value !== password_confirm.value) {
    error.value = '两次密码不一致'
    return
  }

  if (password.value.length < 6) {
    error.value = '密码长度至少6位'
    return
  }

  loading.value = true

  try {
    const response = await authAPI.register(username.value, password.value, password_confirm.value)
    if (response.data.success) {
      success.value = '注册成功，正在跳转...'
      setTimeout(() => {
        router.push('/login')
      }, 1500)
    }
  } catch (err) {
    error.value = err.response?.data?.error || '注册失败，请重试'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.register-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.register-box {
  background: white;
  padding: 2.5rem;
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
  width: 100%;
  max-width: 400px;
}

h1 {
  text-align: center;
  color: #333;
  font-size: 1.5rem;
  margin-bottom: 0.5rem;
}

h2 {
  text-align: center;
  color: #666;
  font-size: 1.2rem;
  margin-bottom: 2rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

label {
  display: block;
  margin-bottom: 0.5rem;
  color: #555;
  font-weight: 500;
}

input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 1rem;
  box-sizing: border-box;
}

input:focus {
  outline: none;
  border-color: #667eea;
}

button {
  width: 100%;
  padding: 0.875rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 1rem;
  cursor: pointer;
  transition: transform 0.2s;
}

button:hover:not(:disabled) {
  transform: translateY(-2px);
}

button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.error-message {
  color: #e74c3c;
  font-size: 0.875rem;
  margin-bottom: 1rem;
  text-align: center;
}

.success-message {
  color: #27ae60;
  font-size: 0.875rem;
  margin-bottom: 1rem;
  text-align: center;
}

.links {
  margin-top: 1.5rem;
  text-align: center;
}

.links a {
  color: #667eea;
  text-decoration: none;
}

.links a:hover {
  text-decoration: underline;
}
</style>
