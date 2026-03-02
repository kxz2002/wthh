import axios from 'axios'

const api = axios.create({
  baseURL: '/auth',
  withCredentials: true
})

export const authAPI = {
  login(username, password) {
    return api.post('/api/login', { username, password })
  },

  register(username, password, password_confirm) {
    return api.post('/api/register', { username, password, password_confirm })
  },

  getUserInfo() {
    return api.get('/api/userinfo')
  },

  logout() {
    return api.get('/logout')
  }
}

export const dataAPI = {
  getStatistics() {
    return axios.get('/api/statistics')
  },

  getFamilyCircles(page = 1, perPage = 20) {
    return axios.get('/api/family_circles', { params: { page, per_page: perPage } })
  },

  getUser(userId) {
    return axios.get(`/api/user/${userId}`)
  },

  searchUsers(query) {
    return axios.get('/api/search', { params: { q: query } })
  },

  getCircleGraph(circleId, dataset = 'train') {
    return axios.get(`/api/circle_graph/${circleId}`, { params: { dataset } })
  }
}

export default api
