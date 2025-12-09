"""
GitHub 仓库数据模型
"""
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.base import Base


class GithubRepo(Base):
    """GitHub 仓库模型"""

    __tablename__ = "github_repos"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    repo_id = Column(Integer, unique=True, index=True, nullable=False)  # GitHub 仓库 ID
    name = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False, index=True)
    private = Column(Boolean, default=False)
    language = Column(String(100), nullable=True)
    html_url = Column(String(500), nullable=False)
    description = Column(String(1000), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # 关系定义
    user = relationship("User", back_populates="repos")

    def __repr__(self) -> str:
        return f"<GithubRepo(id={self.id}, full_name={self.full_name})>"

