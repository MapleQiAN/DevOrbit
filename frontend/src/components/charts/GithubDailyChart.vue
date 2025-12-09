<template>
  <div class="chart-container">
    <div class="chart-header">
      <h3>{{ title }}</h3>
      <div class="chart-controls">
        <input
          v-model="fromDate"
          type="date"
          class="date-input"
          @change="handleDateChange"
        />
        <span>至</span>
        <input
          v-model="toDate"
          type="date"
          class="date-input"
          @change="handleDateChange"
        />
      </div>
    </div>

    <div v-if="isLoading" class="loading">
      <div class="spinner"></div>
      <p>加载中...</p>
    </div>

    <div v-else-if="error" class="error">
      <p>{{ error }}</p>
    </div>

    <div v-else class="chart-wrapper">
      <div ref="chartRef" class="chart"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import * as echarts from 'echarts'
import { getDailyStats } from '@/api/github'
import type { GithubDailyStat } from '@/api/github'

interface Props {
  title?: string
}

withDefaults(defineProps<Props>(), {
  title: 'GitHub 每日提交统计',
})

const chartRef = ref<HTMLElement>()
let chart: echarts.ECharts | null = null

const isLoading = ref(false)
const error = ref<string | null>(null)

// 日期范围：默认最近 30 天
const today = new Date()
const thirtyDaysAgo = new Date(today.getTime() - 30 * 24 * 60 * 60 * 1000)

const toDate = ref(today.toISOString().split('T')[0])
const fromDate = ref(thirtyDaysAgo.toISOString().split('T')[0])

const stats = ref<GithubDailyStat[]>([])

// 初始化图表
function initChart() {
  if (!chartRef.value) return

  if (!chart) {
    chart = echarts.init(chartRef.value)
  }

  const dates = stats.value.map((s) => s.date)
  const commits = stats.value.map((s) => s.commit_count)
  const prs = stats.value.map((s) => s.pr_count)
  const issues = stats.value.map((s) => s.issue_count)

  const option: echarts.EChartsOption = {
    title: {
      text: '',
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross',
      },
    },
    legend: {
      data: ['Commits', 'Pull Requests', 'Issues'],
      top: 20,
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      top: '15%',
      containLabel: true,
    },
    xAxis: {
      type: 'category',
      data: dates,
      boundaryGap: false,
    },
    yAxis: {
      type: 'value',
      name: '数量',
    },
    series: [
      {
        name: 'Commits',
        data: commits,
        type: 'line',
        smooth: true,
        itemStyle: {
          color: '#667eea',
        },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            {
              offset: 0,
              color: 'rgba(102, 126, 234, 0.3)',
            },
            {
              offset: 1,
              color: 'rgba(102, 126, 234, 0)',
            },
          ]),
        },
      },
      {
        name: 'Pull Requests',
        data: prs,
        type: 'line',
        smooth: true,
        itemStyle: {
          color: '#27ae60',
        },
      },
      {
        name: 'Issues',
        data: issues,
        type: 'line',
        smooth: true,
        itemStyle: {
          color: '#f39c12',
        },
      },
    ],
  }

  chart.setOption(option)
}

// 加载数据
async function loadData() {
  isLoading.value = true
  error.value = null

  try {
    const response = await getDailyStats(fromDate.value, toDate.value)
    stats.value = response.data
    initChart()
  } catch (err: any) {
    error.value = err.response?.data?.detail || '加载数据失败'
    console.error('Failed to load GitHub stats:', err)
  } finally {
    isLoading.value = false
  }
}

// 日期变化处理
function handleDateChange() {
  loadData()
}

// 窗口大小变化时重新调整图表
function handleResize() {
  if (chart) {
    chart.resize()
  }
}

onMounted(() => {
  loadData()
  window.addEventListener('resize', handleResize)
})

// 清理
watch(
  () => chartRef.value,
  () => {
    if (!chartRef.value && chart) {
      chart.dispose()
      chart = null
    }
  }
)
</script>

<style scoped>
.chart-container {
  background-color: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 20px;
}

.chart-header h3 {
  font-size: 18px;
  color: #333;
  margin: 0;
}

.chart-controls {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 14px;
  color: #666;
}

.date-input {
  padding: 6px 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
}

.date-input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.1);
}

.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 400px;
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

.loading p {
  color: #666;
  font-size: 14px;
}

.error {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 400px;
  color: #e74c3c;
  font-size: 14px;
}

.chart-wrapper {
  width: 100%;
  height: 400px;
}

.chart {
  width: 100%;
  height: 100%;
}
</style>

