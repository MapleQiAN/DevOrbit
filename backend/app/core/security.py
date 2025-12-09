"""
JWT 和安全相关的工具函数
"""
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

import jwt
from pydantic import ValidationError

from app.core.config import settings


def create_access_token(
    subject: str, expires_delta: Optional[timedelta] = None
) -> str:
    """
    创建 JWT access token

    Args:
        subject: token 的主体（通常是用户 ID）
        expires_delta: token 过期时间差（如果为 None 则使用配置中的默认值）

    Returns:
        JWT token 字符串
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.JWT_EXPIRE_MINUTES
        )

    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def decode_token(token: str) -> Optional[str]:
    """
    解码并验证 JWT token

    Args:
        token: JWT token 字符串

    Returns:
        token 中的 subject（用户 ID），如果验证失败返回 None
    """
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        subject: str = payload.get("sub")
        if subject is None:
            return None
        return subject
    except (jwt.InvalidTokenError, ValidationError):
        return None

