<template>
  <header class="header">
    <div class="header-content">
      <div class="logo">
        <h1>DevOrbit</h1>
      </div>

      <nav class="nav">
        <router-link to="/dashboard" class="nav-link" active-class="active">
          仪表盘
        </router-link>
        <router-link to="/settings" class="nav-link" active-class="active">
          设置
        </router-link>
      </nav>

      <div class="header-actions">
        <div class="user-menu">
          <img
            v-if="currentUser?.avatar_url"
            :src="currentUser.avatar_url"
            :alt="currentUser.github_login"
            class="avatar"
            @click="toggleUserMenu"
          />
          <span v-else class="avatar-placeholder" @click="toggleUserMenu">
            {{ currentUser?.github_login?.charAt(0).toUpperCase() }}
          </span>

          <div v-if="showUserMenu" class="dropdown-menu">
            <div class="user-info">
              <img
                v-if="currentUser?.avatar_url"
                :src="currentUser.avatar_url"
                :alt="currentUser.github_login"
                class="dropdown-avatar"
              />
              <div class="user-details">
                <p class="username">{{ currentUser?.github_login }}</p>
                <p class="user-id">ID: {{ currentUser?.github_id }}</p>
              </div>
            </div>
            <div class="dropdown-divider"></div>
            <button @click="goSettings" class="dropdown-item">
              设置
            </button>
            <button @click="handleLogout" class="dropdown-item logout">
              退出登录
            </button>
          </div>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const showUserMenu = ref(false)
const currentUser = computed(() => authStore.user)

function toggleUserMenu() {
  showUserMenu.value = !showUserMenu.value
}

function handleLogout() {
  authStore.logout()
  showUserMenu.value = false
  router.push('/login')
}

function goSettings() {
  showUserMenu.value = false
  router.push('/settings')
}

// 点击其他地方关闭菜单
document.addEventListener('click', (e) => {
  const target = e.target as HTMLElement
  if (!target.closest('.user-menu')) {
    showUserMenu.value = false
  }
})
</script>

<style scoped>
.header {
  background-color: white;
  border-bottom: 1px solid #eee;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 64px;
}

.logo h1 {
  font-size: 24px;
  font-weight: 700;
  color: #667eea;
  margin: 0;
}

.nav {
  display: flex;
  gap: 30px;
  flex: 1;
  margin-left: 40px;
}

.nav-link {
  color: #666;
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
  transition: color 0.3s ease;
  padding: 8px 0;
  border-bottom: 2px solid transparent;
}

.nav-link:hover {
  color: #667eea;
}

.nav-link.active {
  color: #667eea;
  border-bottom-color: #667eea;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 20px;
}

.user-menu {
  position: relative;
}

.avatar,
.avatar-placeholder {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #667eea;
  color: white;
  font-weight: 600;
  font-size: 16px;
  transition: transform 0.3s ease;
}

.avatar {
  object-fit: cover;
}

.avatar:hover,
.avatar-placeholder:hover {
  transform: scale(1.05);
}

.dropdown-menu {
  position: absolute;
  top: 100%;
  right: 0;
  background-color: white;
  border: 1px solid #eee;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  min-width: 200px;
  margin-top: 8px;
  overflow: hidden;
  z-index: 1000;
}

.user-info {
  display: flex;
  gap: 12px;
  padding: 12px 16px;
  align-items: center;
}

.dropdown-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  object-fit: cover;
}

.user-details {
  flex: 1;
}

.username {
  font-size: 14px;
  font-weight: 600;
  color: #333;
  margin: 0;
}

.user-id {
  font-size: 12px;
  color: #999;
  margin: 4px 0 0 0;
}

.dropdown-divider {
  height: 1px;
  background-color: #eee;
}

.dropdown-item {
  width: 100%;
  padding: 12px 16px;
  border: none;
  background: none;
  text-align: left;
  cursor: pointer;
  font-size: 14px;
  color: #666;
  transition: background-color 0.3s ease;
}

.dropdown-item:hover {
  background-color: #f5f5f5;
}

.dropdown-item.logout {
  color: #e74c3c;
}

.dropdown-item.logout:hover {
  background-color: #fee;
}
</style>

