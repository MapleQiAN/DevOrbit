<template>
  <div class="dashboard-container">
    <Header />

    <main class="dashboard-main">
      <div class="dashboard-wrapper">
        <!-- 统计卡片 -->
        <div class="stats-grid">
          <div class="stat-card">
            <div class="stat-icon commits">
              <span>📝</span>
            </div>
            <div class="stat-content">
              <p class="stat-label">总提交数</p>
              <p class="stat-value">{{ totalStats.commits }}</p>
            </div>
          </div>

          <div class="stat-card">
            <div class="stat-icon prs">
              <span>🔀</span>
            </div>
            <div class="stat-content">
              <p class="stat-label">Pull Requests</p>
              <p class="stat-value">{{ totalStats.prs }}</p>
            </div>
          </div>

          <div class="stat-card">
            <div class="stat-icon issues">
              <span>⚠️</span>
            </div>
            <div class="stat-content">
              <p class="stat-label">Issues</p>
              <p class="stat-value">{{ totalStats.issues }}</p>
            </div>
          </div>

          <div class="stat-card">
            <div class="stat-icon stars">
              <span>⭐</span>
            </div>
            <div class="stat-content">
              <p class="stat-label">Stars 增长</p>
              <p class="stat-value">{{ totalStats.stars }}</p>
            </div>
          </div>
        </div>

        <!-- 同步按钮 -->
        <div class="sync-section">
          <div class="sync-controls">
            <label class="sync-label">同步时间范围：</label>
            <input v-model="syncFromDate" type="date" class="sync-input" />
            <span>至</span>
            <input v-model="syncToDate" type="date" class="sync-input" />
          </div>
          <div class="sync-actions">
            <button
              @click="handleSync"
              :disabled="isSyncing"
              class="btn-sync"
            >
              <span v-if="!isSyncing">🔄 同步 GitHub 数据</span>
              <span v-else>同步中...</span>
            </button>
            <p v-if="syncMessage" :class="['sync-message', syncMessageType]">
              {{ syncMessage }}
            </p>
          </div>
        </div>

        <!-- 图表 -->
        <div class="charts-section">
          <GithubDailyChart title="GitHub 每日活动统计" :reload-key="chartReloadKey" />
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import Header from '@/components/Header.vue'
import GithubDailyChart from '@/components/charts/GithubDailyChart.vue'
import { syncGithubData, getDailyStats } from '@/api/github'
import { useSettingsStore } from '@/stores/settings'

const isSyncing = ref(false)
const syncMessage = ref<string | null>(null)
const syncMessageType = ref<'success' | 'error' | null>(null)
const stats = ref<any[]>([])
const settingsStore = useSettingsStore()
const today = new Date()
const oneYearAgo = new Date(today.getTime() - 365 * 24 * 60 * 60 * 1000)
const syncToDate = ref(settingsStore.defaultToDate || today.toISOString().split('T')[0])
const syncFromDate = ref(settingsStore.defaultFromDate || oneYearAgo.toISOString().split('T')[0])
const chartReloadKey = ref(0)

const totalStats = computed(() => {
  return {
    commits: stats.value.reduce((sum, s) => sum + s.commit_count, 0),
    prs: stats.value.reduce((sum, s) => sum + s.pr_count, 0),
    issues: stats.value.reduce((sum, s) => sum + s.issue_count, 0),
    stars: stats.value.reduce((sum, s) => sum + s.star_delta, 0),
  }
})

async function handleSync() {
  isSyncing.value = true
  syncMessage.value = null
  syncMessageType.value = null

  if (new Date(syncFromDate.value) > new Date(syncToDate.value)) {
    syncMessage.value = '开始日期不能晚于结束日期'
    syncMessageType.value = 'error'
    isSyncing.value = false
    return
  }

  try {
    const result = await syncGithubData({
      fromDate: syncFromDate.value,
      toDate: syncToDate.value,
      mode: settingsStore.syncMode,
    })
    syncMessage.value = `✓ 同步成功（${result.date_range}）。更新了 ${result.repos_count} 个仓库，${result.stats_updated} 条统计记录`
    syncMessageType.value = 'success'

    // 重新加载数据
    await loadStats()
    chartReloadKey.value += 1

    // 3 秒后清除消息
    setTimeout(() => {
      syncMessage.value = null
    }, 3000)
  } catch (error: any) {
    syncMessage.value = `✗ 同步失败: ${error.response?.data?.detail || '未知错误'}`
    syncMessageType.value = 'error'
  } finally {
    isSyncing.value = false
  }
}

async function loadStats() {
  try {
    const today = new Date()
    const thirtyDaysAgo = new Date(today.getTime() - 30 * 24 * 60 * 60 * 1000)

    const response = await getDailyStats(
      thirtyDaysAgo.toISOString().split('T')[0],
      today.toISOString().split('T')[0]
    )
    stats.value = response.data
  } catch (error) {
    console.error('Failed to load stats:', error)
  }
}

onMounted(() => {
  loadStats()
})
</script>

<style scoped>
.dashboard-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background-color: #f5f5f5;
}

.dashboard-main {
  flex: 1;
  padding: 30px 20px;
}

.dashboard-wrapper {
  max-width: 1400px;
  margin: 0 auto;
  width: 100%;
}

/* 统计卡片 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.stat-card {
  background-color: white;
  border-radius: 8px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
}

.stat-icon.commits {
  background-color: rgba(102, 126, 234, 0.1);
}

.stat-icon.prs {
  background-color: rgba(39, 174, 96, 0.1);
}

.stat-icon.issues {
  background-color: rgba(243, 156, 18, 0.1);
}

.stat-icon.stars {
  background-color: rgba(231, 76, 60, 0.1);
}

.stat-content {
  flex: 1;
}

.stat-label {
  font-size: 12px;
  color: #999;
  margin: 0;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #333;
  margin: 4px 0 0 0;
}

/* 同步部分 */
.sync-section {
  margin-bottom: 30px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.btn-sync {
  padding: 12px 24px;
  background-color: #667eea;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.btn-sync:hover:not(:disabled) {
  background-color: #5568d3;
}

.btn-sync:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.sync-message {
  font-size: 14px;
  color: #27ae60;
  margin: 0;
}

.sync-message.error {
  color: #e74c3c;
}

.sync-controls,
.sync-actions {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.sync-input {
  padding: 8px 10px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
}

.sync-label {
  font-size: 14px;
  color: #555;
}

/* 图表部分 */
.charts-section {
  margin-bottom: 30px;
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }

  .sync-section {
    flex-direction: column;
    align-items: flex-start;
  }

  .btn-sync {
    width: 100%;
  }
}
</style>

