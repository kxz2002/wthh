<template>
  <div class="dashboard-container">
    <nav class="navbar">
      <div class="nav-brand">家庭圈用户识别系统 - 仪表板</div>
      <div class="nav-links">
        <span class="username">欢迎，{{ user?.username || '用户' }}</span>
        <button @click="handleLogout">退出登录</button>
      </div>
    </nav>

    <div class="content">
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-label">训练集用户</div>
          <div class="stat-value">{{ stats.train?.total_users || 0 }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">验证集用户</div>
          <div class="stat-value">{{ stats.valid?.total_users || 0 }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">测试集用户</div>
          <div class="stat-value">{{ stats.test?.total_users || 0 }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { authAPI, dataAPI } from '@/api'

const router = useRouter()
const user = ref(null)
const stats = ref({})

const loadUser = async () => {
  try {
    const response = await authAPI.getUserInfo()
    user.value = response.data
  } catch (err) {
    console.error('Failed to load user:', err)
  }
}

const loadStatistics = async () => {
  try {
    const response = await dataAPI.getStatistics()
    stats.value = response.data
  } catch (err) {
    console.error('Failed to load statistics:', err)
  }
}

const handleLogout = async () => {
  try {
    await authAPI.logout()
    router.push('/login')
  } catch (err) {
    console.error('Logout failed:', err)
  }
}

onMounted(() => {
  loadUser()
  loadStatistics()
})
</script>

<style scoped>
.dashboard-container {
  min-height: 100vh;
  background: #f5f7fa;
}

.navbar {
  background: white;
  padding: 1rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.nav-brand {
  font-size: 1.25rem;
  font-weight: 600;
  color: #333;
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.username {
  color: #666;
}

.nav-links button {
  padding: 0.5rem 1rem;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

.content {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
}

.stat-card {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.stat-label {
  color: #666;
  font-size: 0.875rem;
  margin-bottom: 0.5rem;
}

.stat-value {
  font-size: 2rem;
  font-weight: 600;
  color: #667eea;
}
</style>
