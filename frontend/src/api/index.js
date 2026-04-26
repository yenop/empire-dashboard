import axios from 'axios'
import router from '@/router'

const TOKEN_KEY = 'empire_token'
const base = import.meta.env.VITE_API_BASE || ''

const api = axios.create({
  baseURL: base || undefined,
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.request.use((config) => {
  const t = localStorage.getItem(TOKEN_KEY)
  if (t) {
    config.headers.Authorization = `Bearer ${t}`
  }
  return config
})

api.interceptors.response.use(
  (r) => r,
  async (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem(TOKEN_KEY)
      const { useAuthStore } = await import('@/stores/auth')
      useAuthStore().setToken('')
      if (router.currentRoute.value.path !== '/login') {
        router.push({ name: 'login', query: { redirect: router.currentRoute.value.fullPath } })
      }
    }
    return Promise.reject(err)
  }
)

export default api
