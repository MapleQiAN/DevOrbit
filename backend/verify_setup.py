#!/usr/bin/env python3
"""
DevOrbit 后端设置验证脚本
检查所有必要的依赖和配置是否正确
"""
import sys
from pathlib import Path

def check_python_version():
    """检查 Python 版本"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 10):
        print(f"❌ Python 版本过低: {version.major}.{version.minor}")
        print("   需要 Python 3.10 或更高版本")
        return False
    print(f"✓ Python 版本: {version.major}.{version.minor}.{version.micro}")
    return True


def check_dependencies():
    """检查必要的依赖是否已安装"""
    required_packages = [
        "fastapi",
        "uvicorn",
        "sqlalchemy",
        "pydantic",
        "pydantic_settings",
        "httpx",
        "jwt",
        "dotenv",
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"✓ {package}")
        except ImportError:
            print(f"❌ {package}")
            missing.append(package)
    
    if missing:
        print(f"\n缺少以下依赖: {', '.join(missing)}")
        print("请运行: pip install -e .")
        return False
    
    return True


def check_env_file():
    """检查 .env 文件是否存在"""
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠️  .env 文件不存在")
        print("   请复制 .env.example 到 .env 并填入配置")
        return False
    
    print("✓ .env 文件存在")
    return True


def check_config():
    """检查配置是否可以正确加载"""
    try:
        from app.core.config import settings
        print("✓ 配置加载成功")
        print(f"  - 数据库: {settings.DATABASE_URL}")
        print(f"  - 环境: {settings.ENVIRONMENT}")
        print(f"  - API 端口: {settings.API_PORT}")
        return True
    except Exception as e:
        print(f"❌ 配置加载失败: {e}")
        return False


def check_database():
    """检查数据库连接"""
    try:
        from app.db.session import engine
        from app.db.base import Base
        
        # 尝试连接数据库
        with engine.connect() as conn:
            print("✓ 数据库连接成功")
        
        # 创建所有表
        Base.metadata.create_all(bind=engine)
        print("✓ 数据库表创建成功")
        return True
    except Exception as e:
        print(f"❌ 数据库错误: {e}")
        return False


def check_models():
    """检查数据模型是否可以正确导入"""
    try:
        from app.models import User, GithubRepo, GithubDailyStat
        print("✓ 数据模型导入成功")
        print(f"  - User")
        print(f"  - GithubRepo")
        print(f"  - GithubDailyStat")
        return True
    except Exception as e:
        print(f"❌ 数据模型导入失败: {e}")
        return False


def check_api():
    """检查 API 端点是否可以正确导入"""
    try:
        from app.main import app
        print("✓ FastAPI 应用创建成功")
        
        # 检查路由
        routes = [route.path for route in app.routes]
        print(f"  - 已注册 {len(routes)} 个路由")
        
        if "/health" in routes:
            print("  - ✓ /health 端点已注册")
        
        return True
    except Exception as e:
        print(f"❌ API 应用创建失败: {e}")
        return False


def main():
    """主验证流程"""
    print("=" * 60)
    print("DevOrbit 后端设置验证")
    print("=" * 60)
    print()
    
    checks = [
        ("Python 版本", check_python_version),
        ("依赖包", check_dependencies),
        (".env 文件", check_env_file),
        ("配置加载", check_config),
        ("数据库", check_database),
        ("数据模型", check_models),
        ("API 应用", check_api),
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\n[检查] {name}")
        print("-" * 60)
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ 检查失败: {e}")
            results.append((name, False))
    
    print()
    print("=" * 60)
    print("验证结果总结")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓" if result else "❌"
        print(f"{status} {name}")
    
    print()
    print(f"通过: {passed}/{total}")
    
    if passed == total:
        print()
        print("🎉 所有检查都通过了！")
        print()
        print("你可以现在启动后端服务:")
        print("  python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload")
        print()
        print("然后访问 API 文档:")
        print("  http://localhost:8000/docs")
        return 0
    else:
        print()
        print("⚠️  有些检查未通过，请解决上述问题后重试")
        return 1


if __name__ == "__main__":
    sys.exit(main())

