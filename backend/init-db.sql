-- ============================================
-- DevOrbit 数据库初始化脚本
-- ============================================
-- 此脚本在 PostgreSQL 容器启动时自动执行

-- 创建扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 设置字符编码
SET client_encoding = 'UTF8';

-- 创建基础表（如果不存在）
-- 注：实际的表结构由 Alembic 迁移管理

-- 创建索引优化查询性能
-- 这些将在 Alembic 迁移中创建

-- 初始化完成
SELECT 'Database initialization completed' as status;

