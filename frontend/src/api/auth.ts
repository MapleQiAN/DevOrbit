import client from './client'

export interface User {
  id: number
  github_id: number
  github_login: string
  avatar_url: string | null
  created_at: string
  updated_at: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
  user: User
}

export interface AuthorizationUrlResponse {
  authorization_url: string
}

/**
 * 获取 GitHub OAuth 授权 URL
 */
export async function getGithubAuthorizationUrl(): Promise<string> {
  const response = await client.get<AuthorizationUrlResponse>('/auth/github/login')
  return response.data.authorization_url
}

/**
 * 处理 GitHub OAuth 回调
 */
export async function handleGithubCallback(code: string): Promise<LoginResponse> {
  const response = await client.get<LoginResponse>('/auth/github/callback', {
    params: { code },
  })
  return response.data
}

