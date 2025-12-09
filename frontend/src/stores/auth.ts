import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User } from '@/api/auth'

const STORAGE_KEY = 'devorbit_auth'

export const useAuthStore = defineStore('auth', () => {
  // 状态
  const token = ref<string | null>(localStorage.getItem(`${STORAGE_KEY}_token`))
  const user = ref<User | null>(null)

  // 尝试从 localStorage 恢复用户信息
  const storedUser = localStorage.getItem(`${STORAGE_KEY}_user`)
  if (storedUser) {
    try {
      user.value = JSON.parse(storedUser)
    } catch (e) {
      console.error('Failed to parse stored user:', e)
    }
  }

  // 计算属性
  const isAuthenticated = computed(() => !!token.value && !!user.value)

  // 方法
  function setAuth(newToken: string, newUser: User) {
    token.value = newToken
    user.value = newUser

    // 保存到 localStorage
    localStorage.setItem(`${STORAGE_KEY}_token`, newToken)
    localStorage.setItem(`${STORAGE_KEY}_user`, JSON.stringify(newUser))
  }

  function logout() {
    token.value = null
    user.value = null

    // 清除 localStorage
    localStorage.removeItem(`${STORAGE_KEY}_token`)
    localStorage.removeItem(`${STORAGE_KEY}_user`)
  }

  return {
    token,
    user,
    isAuthenticated,
    setAuth,
    logout,
  }
})

