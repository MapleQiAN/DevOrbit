"""
GitHub 相关的 Pydantic schemas
"""
from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel


class GithubRepoBase(BaseModel):
    """GitHub 仓库基础信息"""

    repo_id: int
    name: str
    full_name: str
    private: bool
    language: Optional[str] = None
    html_url: str
    description: Optional[str] = None


class GithubRepoResponse(GithubRepoBase):
    """返回给客户端的仓库信息"""

    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class GithubDailyStatBase(BaseModel):
    """GitHub 每日统计基础信息"""

    date: date
    commit_count: int = 0
    pr_count: int = 0
    issue_count: int = 0
    star_delta: int = 0


class GithubDailyStatResponse(GithubDailyStatBase):
    """返回给客户端的每日统计信息"""

    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class GithubSyncResponse(BaseModel):
    """GitHub 数据同步响应"""

    message: str
    repos_count: int
    stats_updated: int
    date_range: Optional[str] = None


class GithubDailyStatsQueryResponse(BaseModel):
    """每日统计查询响应"""

    data: List[GithubDailyStatResponse]
    total: int

