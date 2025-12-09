"""
数据库基础配置
定义 SQLAlchemy 的 declarative base，所有模型都应继承此 base
"""
from sqlalchemy.orm import declarative_base

Base = declarative_base()

