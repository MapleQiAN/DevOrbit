"""
用户数据模型
"""
from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import relationship

from app.db.base import Base


class User(Base):
    """用户模型"""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    github_id = Column(Integer, unique=True, index=True, nullable=False)
    github_login = Column(String(255), unique=True, index=True, nullable=False)
    avatar_url = Column(String(500), nullable=True)
    github_access_token = Column(String(500), nullable=False)  # 存储 GitHub token 用于 API 调用
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # 关系定义
    repos = relationship("GithubRepo", back_populates="user", cascade="all, delete-orphan")
    daily_stats = relationship("GithubDailyStat", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<User(id={self.id}, github_login={self.github_login})>"

