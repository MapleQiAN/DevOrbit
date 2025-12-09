"""
GitHub OAuth 认证端点
实现 GitHub OAuth 登录流程和 JWT token 签发
"""
from typing import Optional
from urllib.parse import urlencode

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import create_access_token
from app.db.session import get_db
from app.models import User
from app.schemas.auth import GithubUserInfo, LoginResponse
from app.schemas.user import UserResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/github/login")
async def github_login():
    """
    获取 GitHub OAuth 授权 URL
    前端调用此端点获取授权 URL，然后跳转到 GitHub 授权页面

    Returns:
        {"authorization_url": "https://github.com/login/oauth/authorize?..."}
    """
    # GitHub OAuth 授权端点
    github_auth_url = "https://github.com/login/oauth/authorize"

    params = {
        "client_id": settings.GITHUB_CLIENT_ID,
        "redirect_uri": settings.GITHUB_REDIRECT_URI,
        "scope": "user:email read:user",  # 请求的权限范围
        "allow_signup": "true",
    }

    authorization_url = f"{github_auth_url}?{urlencode(params)}"

    return {"authorization_url": authorization_url}


@router.get("/github/callback")
async def github_callback(
    code: str = Query(..., description="GitHub OAuth 授权码"),
    state: Optional[str] = Query(None, description="CSRF 防护状态码"),
    db: Session = Depends(get_db),
) -> LoginResponse:
    """
    处理 GitHub OAuth 回调
    使用授权码向 GitHub 交换 access token，获取用户信息，创建/更新用户，签发 JWT

    Args:
        code: GitHub OAuth 授权码
        state: CSRF 防护状态码（可选）
        db: 数据库会话

    Returns:
        LoginResponse: 包含 JWT token 和用户信息

    Raises:
        HTTPException: 如果 OAuth 流程失败
    """
    if not settings.GITHUB_CLIENT_ID or not settings.GITHUB_CLIENT_SECRET:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="GitHub OAuth 配置不完整",
        )

    # 第 1 步：使用授权码向 GitHub 交换 access token
    token_url = "https://github.com/login/oauth/access_token"
    token_params = {
        "client_id": settings.GITHUB_CLIENT_ID,
        "client_secret": settings.GITHUB_CLIENT_SECRET,
        "code": code,
        "redirect_uri": settings.GITHUB_REDIRECT_URI,
    }

    try:
        async with httpx.AsyncClient() as client:
            # 请求 access token
            token_response = await client.post(
                token_url,
                data=token_params,
                headers={"Accept": "application/json"},
                timeout=10.0,
            )
            token_response.raise_for_status()
            token_data = token_response.json()

            if "error" in token_data:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"GitHub OAuth 失败: {token_data.get('error_description', 'Unknown error')}",
                )

            access_token = token_data.get("access_token")
            if not access_token:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="无法获取 GitHub access token",
                )

            # 第 2 步：使用 access token 获取用户信息
            user_url = "https://api.github.com/user"
            user_response = await client.get(
                user_url,
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/vnd.github.v3+json",
                },
                timeout=10.0,
            )
            user_response.raise_for_status()
            github_user_data = user_response.json()

            # 解析 GitHub 用户信息
            github_user = GithubUserInfo(
                id=github_user_data["id"],
                login=github_user_data["login"],
                avatar_url=github_user_data.get("avatar_url", ""),
                name=github_user_data.get("name"),
                bio=github_user_data.get("bio"),
                public_repos=github_user_data.get("public_repos", 0),
                followers=github_user_data.get("followers", 0),
                following=github_user_data.get("following", 0),
            )

    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"GitHub API 请求失败: {str(e)}",
        )

    # 第 3 步：在数据库中创建或更新用户
    user = db.query(User).filter(User.github_id == github_user.id).first()

    if user:
        # 更新现有用户
        user.github_login = github_user.login
        user.avatar_url = github_user.avatar_url
        user.github_access_token = access_token
    else:
        # 创建新用户
        user = User(
            github_id=github_user.id,
            github_login=github_user.login,
            avatar_url=github_user.avatar_url,
            github_access_token=access_token,
        )
        db.add(user)

    db.commit()
    db.refresh(user)

    # 第 4 步：签发 JWT token
    jwt_token = create_access_token(subject=str(user.id))

    return LoginResponse(
        access_token=jwt_token,
        token_type="bearer",
        user=UserResponse(
            id=user.id,
            github_id=user.github_id,
            github_login=user.github_login,
            avatar_url=user.avatar_url,
            created_at=user.created_at,
            updated_at=user.updated_at,
        ),
    )

