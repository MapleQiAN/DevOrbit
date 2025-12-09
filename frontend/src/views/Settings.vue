<template>
  <div class="settings-container">
    <Header />
    <main class="settings-main">
      <div class="hero">
        <div>
          <p class="eyebrow">同步策略</p>
          <h2>选择同步模式 & 默认时间范围</h2>
          <p class="hint">
            标准模式快速且仅限近 90 天事件；深度模式可跨任意时间段，耗时更长，可能触发速率限制。
          </p>
        </div>
        <div class="badges">
          <span class="badge speed">⚡ 快速</span>
          <span class="badge deep">🛰️ 深度</span>
          <span class="badge time">⏱️ 默认近一年</span>
        </div>
      </div>

      <div class="grid">
        <div class="settings-card">
          <div class="card-header">
            <div>
              <p class="card-eyebrow">模式</p>
              <h3>同步模式</h3>
            </div>
            <span class="pill">{{ syncMode === 'standard' ? '标准' : '深度' }}</span>
          </div>
          <p class="card-hint">可随时切换，深度模式适合需要长期历史的场景。</p>

          <div class="radio-group">
            <label class="radio">
              <input type="radio" value="standard" v-model="syncMode" />
              <div class="radio-body">
                <p class="radio-title">标准模式</p>
                <p class="radio-desc">最快速，基于 GitHub Events（约近 90 天，或近300条）</p>
              </div>
            </label>
            <label class="radio">
              <input type="radio" value="deep" v-model="syncMode" />
              <div class="radio-body">
                <p class="radio-title">深度模式</p>
                <p class="radio-desc">任意时间段，使用搜索与 GraphQL，耗时更长</p>
              </div>
            </label>
          </div>
        </div>

        <div class="settings-card">
          <div class="card-header">
            <div>
              <p class="card-eyebrow">时间范围</p>
              <h3>默认同步区间</h3>
            </div>
            <span class="pill secondary">近一年</span>
          </div>
          <p class="card-hint">修改后将作为仪表盘同步的默认起止日期。</p>

          <div class="date-row">
            <div class="date-field">
              <label>开始</label>
              <input type="date" v-model="from" />
            </div>
            <span class="to">至</span>
            <div class="date-field">
              <label>结束</label>
              <input type="date" v-model="to" />
            </div>
          </div>
          <p class="note">请确保开始日期不晚于结束日期。</p>

          <div class="actions">
            <button class="btn" @click="save">保存设置</button>
            <span v-if="saved" class="saved">已保存</span>
            <span v-if="error" class="error-msg">{{ error }}</span>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import Header from '@/components/Header.vue'
import { useSettingsStore } from '@/stores/settings'

const settings = useSettingsStore()
const syncMode = ref(settings.syncMode)
const from = ref(settings.defaultFromDate)
const to = ref(settings.defaultToDate)
const saved = ref(false)
const error = ref<string | null>(null)

function save() {
  if (new Date(from.value) > new Date(to.value)) {
    saved.value = false
    error.value = '开始日期不能晚于结束日期'
    return
  }
  error.value = null
  settings.setSyncMode(syncMode.value as 'standard' | 'deep')
  settings.setDefaultRange(from.value, to.value)
  saved.value = true
  setTimeout(() => (saved.value = false), 1500)
}
</script>

<style scoped>
.settings-container {
  min-height: 100vh;
  background: #f5f5f5;
}
.settings-main {
  max-width: 960px;
  margin: 0 auto;
  padding: 32px 20px 60px;
}
.hero {
  background: linear-gradient(120deg, #667eea, #764ba2);
  color: #fff;
  border-radius: 14px;
  padding: 22px 24px;
  display: flex;
  justify-content: space-between;
  gap: 20px;
  align-items: center;
  box-shadow: 0 12px 28px rgba(102, 126, 234, 0.25);
}
.eyebrow {
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-size: 12px;
  opacity: 0.85;
  margin: 0 0 6px;
}
.hero h2 {
  margin: 0;
  font-size: 22px;
  line-height: 1.3;
}
.hint {
  color: rgba(255, 255, 255, 0.88);
  margin: 8px 0 0;
  font-size: 14px;
  max-width: 620px;
}
.badges {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}
.badge {
  padding: 6px 10px;
  border-radius: 999px;
  font-size: 12px;
  border: 1px solid rgba(255, 255, 255, 0.4);
}
.badge.speed {
  background: rgba(255, 255, 255, 0.15);
}
.badge.deep {
  background: rgba(255, 255, 255, 0.08);
}
.badge.time {
  background: rgba(255, 255, 255, 0.08);
}
.grid {
  margin-top: 22px;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 18px;
}
.settings-card {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 8px 22px rgba(0, 0, 0, 0.06);
  border: 1px solid #f0f1f5;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}
.card-eyebrow {
  font-size: 12px;
  color: #777;
  margin: 0 0 4px;
}
.card-hint {
  color: #666;
  font-size: 13px;
  margin: 0 0 14px;
}
.pill {
  padding: 6px 10px;
  border-radius: 999px;
  background: #eef2ff;
  color: #4c51bf;
  font-size: 12px;
  border: 1px solid #e2e8ff;
}
.pill.secondary {
  background: #f5f7fb;
  color: #555;
  border-color: #e5e7eb;
}
.radio-group {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.radio {
  display: flex;
  gap: 10px;
  align-items: flex-start;
  padding: 12px;
  border: 1px solid #e8e8ef;
  border-radius: 10px;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
  background: #fafbff;
}
.radio:hover {
  border-color: #667eea;
  box-shadow: 0 6px 16px rgba(102, 126, 234, 0.12);
}
.radio input {
  margin-top: 4px;
}
.radio-body {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.radio-title {
  margin: 0;
  font-weight: 600;
  color: #333;
}
.radio-desc {
  margin: 0;
  color: #666;
  font-size: 13px;
}
.date-row {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}
.date-field {
  display: flex;
  flex-direction: column;
  gap: 6px;
  min-width: 200px;
}
.date-field label {
  font-size: 13px;
  color: #555;
}
input[type='date'] {
  padding: 10px 12px;
  border: 1px solid #dcdfe6;
  border-radius: 8px;
  font-size: 14px;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}
input[type='date']:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.15);
}
.to {
  color: #666;
  font-size: 13px;
}
.note {
  color: #888;
  font-size: 13px;
  margin: 10px 0 0;
}
.actions {
  margin-top: 16px;
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}
.btn {
  padding: 12px 20px;
  background: linear-gradient(120deg, #667eea, #5a67d8);
  color: #fff;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  box-shadow: 0 8px 18px rgba(102, 126, 234, 0.28);
  transition: transform 0.15s ease, box-shadow 0.2s ease, filter 0.2s ease;
}
.btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 10px 22px rgba(102, 126, 234, 0.35);
}
.btn:active {
  transform: translateY(0);
  filter: brightness(0.98);
}
.saved {
  color: #27ae60;
  font-size: 14px;
}
.error-msg {
  color: #e74c3c;
  font-size: 13px;
}

@media (max-width: 640px) {
  .hero {
    flex-direction: column;
    align-items: flex-start;
  }
  .date-field {
    min-width: 160px;
  }
}
</style>

