"""
健康检查端点
"""
from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check():
    """
    健康检查端点
    用于验证 API 是否正常运行

    Returns:
        {"status": "ok"}
    """
    return {"status": "ok"}

