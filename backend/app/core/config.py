"""
应用配置管理模块
从环境变量读取配置，支持开发和生产环境
"""
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用全局设置"""

    # 应用基础配置
    APP_NAME: str = "DevOrbit"
    APP_VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"

    # 数据库配置
    DATABASE_URL: str = "sqlite:///./devorbit.db"

    # GitHub OAuth 配置
    GITHUB_CLIENT_ID: str = ""
    GITHUB_CLIENT_SECRET: str = ""
    GITHUB_REDIRECT_URI: str = "http://localhost:3000/auth/github/callback"
    GITHUB_API_BASE_URL: str = "https://api.github.com"

    # JWT 配置
    JWT_SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 10080  # 7 days

    # API 配置
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_RELOAD: bool = True

    # CORS 配置
    CORS_ORIGINS: List[str] = ["*"]

    class Config:
        env_file = ".env"
        case_sensitive = True


# 创建全局配置实例
settings = Settings()

