import client from './client'

export interface GithubDailyStat {
  id: number
  user_id: number
  date: string
  commit_count: number
  pr_count: number
  issue_count: number
  star_delta: number
  created_at: string
  updated_at: string
}

export interface GithubDailyStatsResponse {
  data: GithubDailyStat[]
  total: number
}

export interface GithubSyncResponse {
  message: string
  repos_count: number
  stats_updated: number
  date_range: string
}

export interface SyncGithubParams {
  fromDate?: string
  toDate?: string
  mode?: 'standard' | 'deep'
}

/**
 * 同步 GitHub 数据（支持自定义时间范围）
 */
export async function syncGithubData(params?: SyncGithubParams): Promise<GithubSyncResponse> {
  const response = await client.post<GithubSyncResponse>('/github/sync', null, {
    params: {
      from_date: params?.fromDate,
      to_date: params?.toDate,
      mode: params?.mode,
    },
  })
  return response.data
}

/**
 * 获取每日统计数据
 */
export async function getDailyStats(
  fromDate?: string,
  toDate?: string
): Promise<GithubDailyStatsResponse> {
  const response = await client.get<GithubDailyStatsResponse>('/github/stats/daily', {
    params: {
      from_date: fromDate,
      to_date: toDate,
    },
  })
  return response.data
}

