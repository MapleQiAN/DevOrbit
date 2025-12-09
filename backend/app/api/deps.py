"""
API 依赖注入函数
用于 FastAPI 的 Depends 机制
"""
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.security import decode_token
from app.db.session import get_db
from app.models import User

# HTTP Bearer 认证方案
security = HTTPBearer(auto_error=False)


def get_token(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> str:
    """
    从 Authorization header 中提取 Bearer token

    Args:
        credentials: HTTP Bearer 认证凭证

    Returns:
        token 字符串

    Raises:
        HTTPException: 如果 token 不存在或格式不正确
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return credentials.credentials


def get_current_user(
    token: str = Depends(get_token),
    db: Session = Depends(get_db),
) -> User:
    """
    获取当前登录的用户
    从 JWT token 中解码用户 ID，然后从数据库查询用户信息

    Args:
        token: JWT token（从 Authorization header 中获取）
        db: 数据库会话

    Returns:
        当前用户对象

    Raises:
        HTTPException: 如果 token 无效或用户不存在
    """
    user_id = decode_token(token)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user = db.query(User).filter(User.id == int(user_id)).first()
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token format",
        )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user

