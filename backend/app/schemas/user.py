"""
用户相关的 Pydantic schemas
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class UserBase(BaseModel):
    """用户基础信息"""

    github_login: str
    github_id: int
    avatar_url: Optional[str] = None


class UserCreate(UserBase):
    """创建用户时的数据"""

    github_access_token: str


class UserResponse(UserBase):
    """返回给客户端的用户信息"""

    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserInDB(UserResponse):
    """数据库中的用户信息（包含敏感字段）"""

    github_access_token: str

    class Config:
        from_attributes = True

