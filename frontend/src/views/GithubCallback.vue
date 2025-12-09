<template>
  <div class="callback-container">
    <div class="callback-card">
      <div v-if="isLoading" class="loading-state">
        <div class="spinner"></div>
        <p>正在处理授权...</p>
      </div>

      <div v-else-if="error" class="error-state">
        <h2>授权失败</h2>
        <p>{{ error }}</p>
        <router-link to="/login" class="btn-back">返回登录</router-link>
      </div>

      <div v-else class="success-state">
        <h2>授权成功！</h2>
        <p>正在跳转到仪表盘...</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { handleGithubCallback } from '@/api/auth'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const isLoading = ref(true)
const error = ref<string | null>(null)

onMounted(async () => {
  try {
    // 从 URL 中提取 code 参数
    const code = route.query.code as string

    if (!code) {
      error.value = '未找到授权码，请重新尝试登录'
      isLoading.value = false
      return
    }

    // 调用后端 API 处理回调
    const response = await handleGithubCallback(code)

    // 保存认证信息
    authStore.setAuth(response.access_token, response.user)

    // 延迟 1 秒后跳转到仪表盘
    setTimeout(() => {
      router.push('/dashboard')
    }, 1000)
  } catch (err: any) {
    console.error('GitHub callback error:', err)
    error.value = err.response?.data?.detail || '授权失败，请重新尝试'
    isLoading.value = false
  }
})
</script>

<style scoped>
.callback-container {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.callback-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  padding: 40px;
  max-width: 400px;
  width: 100%;
  text-align: center;
}

.loading-state,
.error-state,
.success-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

.loading-state p {
  font-size: 16px;
  color: #666;
}

.error-state h2,
.success-state h2 {
  font-size: 20px;
  color: #333;
  margin: 0;
}

.error-state p {
  color: #e74c3c;
  font-size: 14px;
}

.success-state p {
  color: #27ae60;
  font-size: 14px;
}

.btn-back {
  display: inline-block;
  padding: 10px 20px;
  background-color: #667eea;
  color: white;
  text-decoration: none;
  border-radius: 6px;
  font-size: 14px;
  transition: background-color 0.3s ease;
}

.btn-back:hover {
  background-color: #5568d3;
}
</style>

