<template>
  <div class="home-container">
    <nav class="navbar">
      <div class="nav-brand">家庭圈用户识别系统</div>
      <div class="nav-links">
        <span class="username">欢迎，{{ user?.username || '用户' }}</span>
        <button @click="handleLogout">退出登录</button>
      </div>
    </nav>

    <div class="content">
      <!-- 统计卡片 -->
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

      <!-- 标签页 -->
      <div class="tabs">
        <button :class="['tab', { active: activeTab === 'list' }]" @click="activeTab = 'list'">
          家庭圈列表
        </button>
        <button :class="['tab', { active: activeTab === 'graph' }]" @click="activeTab = 'graph'">
          知识图谱
        </button>
      </div>

      <!-- 家庭圈列表 -->
      <div v-show="activeTab === 'list'" class="section">
        <h3>家庭圈列表</h3>
        <div class="search-box">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="搜索用户ID..."
            @input="handleSearch"
          />
        </div>
        <div v-if="searchResults.length > 0" class="search-results">
          <div
            v-for="result in searchResults"
            :key="result.user_id"
            class="search-item"
            @click="viewUser(result.user_id)"
          >
            {{ result.user_id }}
          </div>
        </div>
        <div class="circles-table">
          <table>
            <thead>
              <tr>
                <th>家庭圈ID</th>
                <th>成员数量</th>
                <th>关键人</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="circle in circles" :key="circle.circle_id">
                <td>{{ circle.circle_id }}</td>
                <td>{{ circle.size }}</td>
                <td>{{ circle.key_person || '-' }}</td>
                <td>
                  <button class="view-graph-btn" @click="viewCircleGraph(circle.circle_id)">
                    查看图谱
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div class="pagination">
          <button :disabled="page <= 1" @click="loadCircles(page - 1)">上一页</button>
          <span>第 {{ page }} 页</span>
          <button @click="loadCircles(page + 1)">下一页</button>
        </div>
      </div>

      <!-- 知识图谱 -->
      <div v-show="activeTab === 'graph'" class="section">
        <h3>知识图谱</h3>
        <div class="graph-controls">
          <select v-model="graphDataset">
            <option value="train">训练集</option>
            <option value="valid">验证集</option>
            <option value="test">测试集</option>
          </select>
          <input
            v-model="graphCircleId"
            type="number"
            placeholder="输入家庭圈ID"
            @keyup.enter="loadGraph"
          />
          <button @click="loadGraph">加载图谱</button>
        </div>
        <div v-if="graphError" class="error-message">{{ graphError }}</div>
        <div ref="graphContainer" class="graph-container"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, watch } from 'vue'
import { useRouter } from 'vue-router'
import { authAPI, dataAPI } from '@/api'
import { Network } from 'vis-network/standalone'
import { DataSet } from 'vis-data'

const router = useRouter()
const user = ref(null)
const stats = ref({})
const circles = ref([])
const page = ref(1)
const perPage = ref(20)
const searchQuery = ref('')
const searchResults = ref([])
const activeTab = ref('list')

// Graph state
const graphContainer = ref(null)
const graphDataset = ref('train')
const graphCircleId = ref('')
const graphError = ref('')
let network = null
const nodes = new DataSet([])
const edges = new DataSet([])

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

const loadCircles = async (newPage = 1) => {
  try {
    const response = await dataAPI.getFamilyCircles(newPage, perPage.value)
    circles.value = response.data.circles
    page.value = response.data.page
  } catch (err) {
    console.error('Failed to load circles:', err)
  }
}

const handleSearch = async () => {
  if (!searchQuery.value.trim()) {
    searchResults.value = []
    return
  }
  try {
    const response = await dataAPI.searchUsers(searchQuery.value)
    searchResults.value = response.data.users
  } catch (err) {
    console.error('Search failed:', err)
  }
}

const viewUser = (userId) => {
  searchQuery.value = userId
  searchResults.value = []
}

const loadGraph = async () => {
  if (!graphCircleId.value) {
    graphError.value = '请输入家庭圈ID'
    return
  }

  graphError.value = ''

  try {
    const response = await dataAPI.getCircleGraph(graphCircleId.value, graphDataset.value)
    const { nodes: graphNodes, edges: graphEdges } = response.data

    // Clear existing data
    nodes.clear()
    edges.clear()

    // Add new data
    nodes.add(graphNodes.map(node => ({
      id: node.id,
      label: node.label,
      group: node.group,
      title: node.title
    })))

    edges.add(graphEdges.map(edge => ({
      from: edge.from,
      to: edge.to,
      label: edge.label,
      color: edge.color
    })))

    // Create network
    await nextTick()
    if (graphContainer.value) {
      if (network) {
        network.destroy()
      }

      const options = {
        nodes: {
          shape: 'dot',
          size: 16,
          font: { size: 14 },
          borderWidth: 2,
          color: {
            background: '#97C2FC',
            border: '#2B7CDE',
            highlight: { background: '#FFB84D', border: '#FF9800' }
          }
        },
        edges: {
          width: 2,
          color: { inherit: 'from' },
          arrows: { to: { enabled: true } }
        },
        groups: {
          key_person: {
            color: { background: '#FFD700', border: '#FFA500' },
            size: 24
          },
          member: {
            color: { background: '#97C2FC', border: '#2B7CDE' }
          }
        },
        physics: {
          stabilization: false,
          barnesHut: {
            gravitationalConstant: -8000,
            springConstant: 0.04,
            springLength: 95
          }
        },
        interaction: {
          hover: true,
          tooltipDelay: 200
        }
      }

      network = new Network(graphContainer.value, { nodes, edges }, options)
    }
  } catch (err) {
    graphError.value = err.response?.data?.error || '加载图谱失败'
  }
}

const viewCircleGraph = (circleId) => {
  graphCircleId.value = circleId
  activeTab.value = 'graph'
  nextTick(() => {
    loadGraph()
  })
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
  loadCircles()
})
</script>

<style scoped>
.home-container {
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

.nav-links button:hover {
  background: #5568d3;
}

.content {
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 1.5rem;
  border-radius: 8px;
  text-align: center;
}

.stat-label {
  font-size: 0.875rem;
  margin-bottom: 0.5rem;
}

.stat-value {
  font-size: 2rem;
  font-weight: 600;
}

.tabs {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
  border-bottom: 2px solid #eee;
}

.tab {
  padding: 0.75rem 1.5rem;
  background: none;
  border: none;
  font-size: 1rem;
  color: #666;
  cursor: pointer;
  border-bottom: 3px solid transparent;
  transition: all 0.3s;
}

.tab.active {
  color: #667eea;
  border-bottom-color: #667eea;
  font-weight: 600;
}

.section {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.section h3 {
  margin-bottom: 1rem;
  color: #333;
}

.search-box {
  margin-bottom: 1rem;
}

.search-box input {
  width: 100%;
  max-width: 400px;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 6px;
}

.search-results {
  max-width: 400px;
  background: white;
  border: 1px solid #ddd;
  border-radius: 6px;
  margin-bottom: 1rem;
}

.search-item {
  padding: 0.75rem;
  cursor: pointer;
  border-bottom: 1px solid #eee;
}

.search-item:hover {
  background: #f5f5f5;
}

.circles-table {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th, td {
  padding: 0.75rem;
  text-align: left;
  border-bottom: 1px solid #eee;
}

th {
  background: #f8f9fa;
  font-weight: 600;
  color: #555;
}

.view-graph-btn {
  padding: 0.25rem 0.75rem;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.875rem;
}

.view-graph-btn:hover {
  background: #5568d3;
}

.pagination {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-top: 1rem;
}

.pagination button {
  padding: 0.5rem 1rem;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

.pagination button:disabled {
  background: #ccc;
  cursor: not-allowed;
}

/* Graph styles */
.graph-controls {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
  align-items: center;
}

.graph-controls select,
.graph-controls input {
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 6px;
}

.graph-controls input {
  width: 200px;
}

.graph-controls button {
  padding: 0.5rem 1rem;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

.graph-container {
  width: 100%;
  height: 600px;
  border: 1px solid #ddd;
  border-radius: 8px;
  background: #fafafa;
}

.error-message {
  color: #e74c3c;
  font-size: 0.875rem;
  margin-bottom: 1rem;
}
</style>
