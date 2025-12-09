import { defineStore } from 'pinia'

type SyncMode = 'standard' | 'deep'

interface SettingsState {
  syncMode: SyncMode
  defaultFromDate: string
  defaultToDate: string
}

function formatDate(date: Date) {
  return date.toISOString().split('T')[0]
}

export const useSettingsStore = defineStore('settings', {
  state: (): SettingsState => {
    const today = new Date()
    const oneYearAgo = new Date(today.getTime() - 365 * 24 * 60 * 60 * 1000)
    return {
      syncMode: 'standard',
      defaultFromDate: formatDate(oneYearAgo),
      defaultToDate: formatDate(today),
    }
  },
  actions: {
    setSyncMode(mode: SyncMode) {
      this.syncMode = mode
    },
    setDefaultRange(from: string, to: string) {
      this.defaultFromDate = from
      this.defaultToDate = to
    },
  },
})

