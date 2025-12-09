"""
GitHub 每日统计数据模型
"""
from datetime import date, datetime

from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship

from app.db.base import Base


class GithubDailyStat(Base):
    """GitHub 每日统计模型 - 按日期聚合用户的 GitHub 活动"""

    __tablename__ = "github_daily_stats"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    
    # 统计数据
    commit_count = Column(Integer, default=0)
    pr_count = Column(Integer, default=0)  # 预留：Pull Request 数
    issue_count = Column(Integer, default=0)  # 预留：Issue 数
    star_delta = Column(Integer, default=0)  # 预留：Star 增量
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # 关系定义
    user = relationship("User", back_populates="daily_stats")

    def __repr__(self) -> str:
        return f"<GithubDailyStat(user_id={self.user_id}, date={self.date}, commits={self.commit_count})>"

