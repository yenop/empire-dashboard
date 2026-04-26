import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/api'

const TOKEN_KEY = 'empire_token'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem(TOKEN_KEY) || '')
  const isAuthenticated = computed(() => Boolean(token.value))

  function setToken(t) {
    token.value = t || ''
    if (t) localStorage.setItem(TOKEN_KEY, t)
    else localStorage.removeItem(TOKEN_KEY)
  }

  function restore() {
    const t = localStorage.getItem(TOKEN_KEY)
    if (t) token.value = t
  }

  async function login(username, password) {
    const { data } = await api.post('/api/auth/login', { username, password })
    setToken(data.access_token)
  }

  function logout() {
    setToken('')
  }

  return { token, isAuthenticated, login, logout, restore, setToken }
})
