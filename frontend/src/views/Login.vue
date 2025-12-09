<template>
  <div class="login-container">
    <div class="login-card">
      <div class="login-header">
        <h1>DevOrbit</h1>
        <p>开发者数字履历仪表盘</p>
      </div>

      <div class="login-content">
        <p class="description">
          把你散落在 GitHub / 刷题平台 / 本地笔记里的碎片努力，聚合成一份可视化的「数字履历」。
        </p>

        <button
          class="github-login-btn"
          @click="handleGithubLogin"
          :disabled="isLoading"
        >
          <svg class="github-icon" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v 3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
          </svg>
          使用 GitHub 登录
        </button>
      </div>

      <div class="login-footer">
        <p>这是一个开源项目，用于聚合个人开发活动数据</p>
        <p>
          <a href="https://github.com/your-username/DevOrbit" target="_blank">
            GitHub 仓库
          </a>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { getGithubAuthorizationUrl } from '@/api/auth'

const isLoading = ref(false)

async function handleGithubLogin() {
  isLoading.value = true
  try {
    const authUrl = await getGithubAuthorizationUrl()
    // 重定向到 GitHub 授权页面
    window.location.href = authUrl
  } catch (error) {
    console.error('Failed to get GitHub authorization URL:', error)
    isLoading.value = false
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.login-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  padding: 40px;
  max-width: 400px;
  width: 100%;
}

.login-header {
  text-align: center;
  margin-bottom: 30px;
}

.login-header h1 {
  font-size: 32px;
  font-weight: 700;
  color: #333;
  margin-bottom: 8px;
}

.login-header p {
  font-size: 14px;
  color: #666;
}

.login-content {
  margin-bottom: 30px;
}

.description {
  font-size: 14px;
  color: #666;
  line-height: 1.6;
  margin-bottom: 20px;
}

.github-login-btn {
  width: 100%;
  padding: 12px 16px;
  background-color: #24292e;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: background-color 0.3s ease;
}

.github-login-btn:hover:not(:disabled) {
  background-color: #1a1e22;
}

.github-login-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.github-icon {
  width: 20px;
  height: 20px;
}

.login-footer {
  text-align: center;
  border-top: 1px solid #eee;
  padding-top: 20px;
}

.login-footer p {
  font-size: 12px;
  color: #999;
  margin: 8px 0;
}

.login-footer a {
  color: #667eea;
  text-decoration: none;
}

.login-footer a:hover {
  text-decoration: underline;
}
</style>

