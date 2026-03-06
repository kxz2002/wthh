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
          <label class="toggle-label">
            <input type="checkbox" v-model="hideNodeLabels" @change="handleToggleLabels" />
            隐藏节点ID
          </label>
        </div>
        <div v-if="graphError" class="error-message">{{ graphError }}</div>

        <!-- 节点图例 -->
        <div class="graph-legend">
          <span class="legend-item"><span class="legend-circle" style="background: #FFD700;"></span> 关键人</span>
          <span class="legend-item"><span class="legend-circle" style="background: #97C2FC;"></span> 成员</span>
        </div>

        <!-- 画布区域 -->
        <div class="graph-wrapper">
          <!-- 连线图例和筛选 - 在画布外面但相对于wrapper定位 -->
          <div class="edge-legend">
            <div class="edge-legend-title">关系筛选</div>
            <label class="edge-legend-item">
              <input type="checkbox" v-model="edgeFilters.地址关联" @change="handleFilterEdges" />
              <span class="edge-line" style="background: #97C2FC;"></span> 地址关联
            </label>
            <label class="edge-legend-item">
              <input type="checkbox" v-model="edgeFilters.账户关联" @change="handleFilterEdges" />
              <span class="edge-line" style="background: #FFB84D;"></span> 账户关联
            </label>
            <label class="edge-legend-item">
              <input type="checkbox" v-model="edgeFilters.家庭网关联" @change="handleFilterEdges" />
              <span class="edge-line" style="background: #7B68EE;"></span> 家庭网关联
            </label>
          </div>
          <div ref="graphContainer" class="graph-container"></div>
        </div>
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
const hideNodeLabels = ref(false)

// 边筛选器
const edgeFilters = ref({
  '地址关联': true,
  '账户关联': true,
  '家庭网关联': true
})

// 存储原始边数据
let originalEdges = []
let originalNodes = []
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
  console.log('Loading graph for circle:', graphCircleId.value, 'dataset:', graphDataset.value)

  try {
    const response = await dataAPI.getCircleGraph(graphCircleId.value, graphDataset.value)
    const { nodes: graphNodes, edges: graphEdges } = response.data
    console.log('Graph data received:', graphNodes.length, 'nodes,', graphEdges.length, 'edges')

    // Clear existing data
    nodes.clear()
    edges.clear()

    // 保存原始节点数据
    originalNodes = graphNodes.map(node => ({
      id: node.id,
      label: node.label,
      originalLabel: node.label,
      group: node.group,
      title: node.title
    }))

    // Add nodes
    nodes.add(originalNodes)

    // 保存原始边数据用于筛选
    originalEdges = graphEdges.map(edge => ({
      from: edge.from,
      to: edge.to,
      label: edge.label,
      color: edge.color
    }))

    edges.add(originalEdges.map(edge => ({
      from: edge.from,
      to: edge.to,
      label: false,  // 隐藏连线文字
      color: edge.color
    })))

    // 重置筛选器
    edgeFilters.value = {
      '地址关联': true,
      '账户关联': true,
      '家庭网关联': true
    }

    console.log('Data prepared, container:', graphContainer.value)

    // Create network
    await nextTick()
    if (graphContainer.value) {
      console.log('Creating network...')
      if (network) {
        network.destroy()
      }

      const options = {
        nodes: {
          shape: 'dot',
          size: 16,
          font: { size: 12, color: '#333', strokeWidth: 0 },
          borderWidth: 2,
          color: {
            background: '#97C2FC',
            border: '#2B7CDE',
            highlight: { background: '#FFB84D', border: '#FF9800' },
            hover: { background: '#FFB84D', border: '#FF9800' }
          }
        },
        edges: {
          width: 1.5,
          color: { color: '#97C2FC', opacity: 0.6 },
          arrows: { to: { enabled: false } },
          smooth: { type: 'continuous' }
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
          enabled: true,
          stabilization: false,
          barnesHut: {
            gravitationalConstant: -5000,
            springConstant: 0.04,
            springLength: 150,
            centralGravity: 0.3
          }
        },
        interaction: {
          hover: true,
          tooltipDelay: 200,
          zoomView: true,
          dragView: true
        }
      }

      network = new Network(graphContainer.value, { nodes, edges }, options)
      console.log('Network created successfully!')
    } else {
      console.log('graphContainer is null!')
    }
  } catch (err) {
    console.error('Network creation error:', err)
    graphError.value = '图谱初始化失败: ' + err.message
  }
}

const handleToggleLabels = () => {
  if (!network) return

  // 获取所有节点ID并更新标签
  const allNodes = nodes.get()
  const updates = allNodes.map(node => ({
    id: node.id,
    label: hideNodeLabels.value ? '' : node.originalLabel || node.label
  }))

  nodes.update(updates)
}

const handleFilterEdges = () => {
  if (!network || originalEdges.length === 0) return

  // 根据筛选条件过滤边
  const filteredEdges = originalEdges.filter(edge => {
    const label = edge.label || ''
    // 判断边的类型
    if (label.includes('地址') || label.includes('小区') || label.includes('区域') || label.includes('基站')) {
      return edgeFilters.value['地址关联'] === true
    } else if (label.includes('账户') || label.includes('缴费')) {
      return edgeFilters.value['账户关联'] === true
    } else if (label.includes('家庭网') || label.includes('泛家庭')) {
      return edgeFilters.value['家庭网关联'] === true
    }
    return true
  })

  // 获取过滤后的边连接的节点ID
  const connectedNodeIds = new Set()
  filteredEdges.forEach(edge => {
    connectedNodeIds.add(edge.from)
    connectedNodeIds.add(edge.to)
  })

  // 更新边数据（隐藏标签）
  const edgesWithHiddenLabel = filteredEdges.map(edge => ({
    ...edge,
    label: false
  }))

  edges.clear()
  edges.add(edgesWithHiddenLabel)

  // 处理节点：保留所有节点，但为孤立节点设置固定位置防止消失
  const nodesToUpdate = originalNodes.map(node => {
    if (!connectedNodeIds.has(node.id)) {
      // 孤立节点保持原位置，设置固定不移动
      return { ...node, physics: false }
    }
    return { ...node, physics: true }
  })

  nodes.clear()
  nodes.add(nodesToUpdate)

  // 重新创建网络（使用新的节点数据）
  network.setData({ nodes, edges })
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

.graph-wrapper {
  position: relative;
  width: 100%;
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

.toggle-label {
  display: flex;
  align-items: center;
  gap: 5px;
  margin-left: 15px;
  cursor: pointer;
}

.graph-legend {
  display: flex;
  gap: 20px;
  padding: 10px;
  margin-bottom: 10px;
  background: #f5f5f5;
  border-radius: 8px;
  flex-wrap: wrap;
}
.legend-item {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 14px;
}
.legend-color {
  display: inline-block;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  border: 2px solid #333;
}

.legend-circle {
  display: inline-block;
  width: 14px;
  height: 14px;
  border-radius: 50%;
  border: 2px solid #333;
}

/* 边图例 - 右上角定位 */
.edge-legend {
  position: absolute;
  top: 10px;
  right: 10px;
  background: rgba(255, 255, 255, 0.95);
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 12px;
  z-index: 9999;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  pointer-events: auto;
}

.edge-legend-title {
  font-size: 12px;
  font-weight: 600;
  color: #333;
  margin-bottom: 8px;
}

.edge-legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: #555;
  cursor: pointer;
  margin-bottom: 6px;
}

.edge-legend-item input {
  cursor: pointer;
}

.edge-line {
  display: inline-block;
  width: 24px;
  height: 3px;
  border-radius: 2px;
}

</style>
