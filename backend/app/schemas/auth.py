"""
认证相关的 Pydantic schemas
"""
from typing import Optional

from pydantic import BaseModel

from app.schemas.user import UserResponse


class Token(BaseModel):
    """JWT token 响应"""

    access_token: str
    token_type: str = "bearer"


class LoginResponse(BaseModel):
    """登录响应，包含 token 和用户信息"""

    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class GithubOAuthCallbackRequest(BaseModel):
    """GitHub OAuth 回调请求"""

    code: str
    state: Optional[str] = None


class GithubUserInfo(BaseModel):
    """GitHub API 返回的用户信息"""

    id: int
    login: str
    avatar_url: str
    name: Optional[str] = None
    bio: Optional[str] = None
    public_repos: int = 0
    followers: int = 0
    following: int = 0

