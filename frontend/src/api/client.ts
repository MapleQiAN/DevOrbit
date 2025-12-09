import axios, { AxiosInstance } from 'axios'
import { useAuthStore } from '@/stores/auth'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

const client: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器：自动添加 Authorization header
client.interceptors.request.use(
  (config) => {
    const authStore = useAuthStore()
    if (authStore.token) {
      config.headers.Authorization = `Bearer ${authStore.token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器：处理错误
client.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    // 如果返回 401，说明 token 过期或无效
    if (error.response?.status === 401) {
      const authStore = useAuthStore()
      authStore.logout()
      // 重定向到登录页面
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default client

