import { createRouter, createWebHistory } from 'vue-router'
import { authAPI } from '@/api'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/Home.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { guest: true }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/Register.vue'),
    meta: { guest: true }
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/views/Dashboard.vue'),
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach(async (to, from, next) => {
  try {
    const response = await authAPI.getUserInfo()
    const isAuthenticated = response.status === 200

    if (to.meta.requiresAuth && !isAuthenticated) {
      next({ name: 'Login' })
    } else if (to.meta.guest && isAuthenticated) {
      next({ name: 'Home' })
    } else {
      next()
    }
  } catch (error) {
    if (to.meta.requiresAuth) {
      next({ name: 'Login' })
    } else {
      next()
    }
  }
})

export default router
