"""
GitHub 数据同步和查询端点
实现 GitHub 数据同步和统计查询功能
"""
from datetime import date, datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models import GithubDailyStat, User
from app.schemas.github import GithubDailyStatsQueryResponse, GithubSyncResponse
from app.services.github_sync import sync_github_data

router = APIRouter(prefix="/github", tags=["github"])


@router.post("/sync")
async def sync_github(
    from_date: Optional[str] = Query(
        None,
        description="开始日期 (YYYY-MM-DD)，默认为 90 天前",
        regex=r"^\d{4}-\d{2}-\d{2}$",
    ),
    to_date: Optional[str] = Query(
        None,
        description="结束日期 (YYYY-MM-DD)，默认为今天",
        regex=r"^\d{4}-\d{2}-\d{2}$",
    ),
    mode: str = Query(
        "standard",
        description="同步模式：standard（90 天内 GitHub events），deep（任意时间段，耗时更长）",
        regex=r"^(standard|deep)$",
    ),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> GithubSyncResponse:
    """
    同步用户的 GitHub 数据

    从 GitHub API 拉取用户的仓库和活动数据，并存储到数据库。

    **认证**: 需要有效的 JWT token

    Returns:
        GithubSyncResponse: 同步结果，包含仓库数和更新的统计记录数

    Raises:
        HTTPException: 如果同步过程中出现错误
    """
    try:
        # 解析日期范围
        if to_date:
            end_date = datetime.strptime(to_date, "%Y-%m-%d").date()
        else:
            end_date = datetime.now().date()

        if from_date:
            start_date = datetime.strptime(from_date, "%Y-%m-%d").date()
        else:
            # deep 模式默认近 365 天；standard 模式默认近 90 天
            default_days = 365 if mode == "deep" else 90
            start_date = end_date - timedelta(days=default_days)

        if start_date > end_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="开始日期不能晚于结束日期",
            )

        repos_count, stats_updated = await sync_github_data(
            current_user,
            db,
            start_date=start_date,
            end_date=end_date,
            days=(end_date - start_date).days + 1,
            mode=mode,
        )

        date_range = f"{start_date} 至 {end_date}"

        return GithubSyncResponse(
            message="GitHub 数据同步成功",
            repos_count=repos_count,
            stats_updated=stats_updated,
            date_range=date_range,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"GitHub 数据同步失败: {str(e)}",
        )


@router.get("/stats/daily", response_model=GithubDailyStatsQueryResponse)
async def get_daily_stats(
    from_date: Optional[str] = Query(
        None,
        description="开始日期 (YYYY-MM-DD)，默认为 30 天前",
        regex=r"^\d{4}-\d{2}-\d{2}$",
    ),
    to_date: Optional[str] = Query(
        None,
        description="结束日期 (YYYY-MM-DD)，默认为今天",
        regex=r"^\d{4}-\d{2}-\d{2}$",
    ),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> GithubDailyStatsQueryResponse:
    """
    查询用户的每日 GitHub 统计数据

    返回指定时间范围内的每日 commit、PR、issue 等统计数据。

    **认证**: 需要有效的 JWT token

    **查询参数**:
    - `from_date`: 开始日期 (YYYY-MM-DD)，默认为 30 天前
    - `to_date`: 结束日期 (YYYY-MM-DD)，默认为今天

    **示例**:
    ```
    GET /github/stats/daily?from_date=2025-11-09&to_date=2025-12-09
    ```

    Returns:
        GithubDailyStatsQueryResponse: 包含每日统计数据的列表

    Raises:
        HTTPException: 如果日期格式不正确
    """
    # 解析日期参数
    try:
        if to_date:
            end_date = datetime.strptime(to_date, "%Y-%m-%d").date()
        else:
            end_date = datetime.now().date()

        if from_date:
            start_date = datetime.strptime(from_date, "%Y-%m-%d").date()
        else:
            start_date = end_date - timedelta(days=30)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"日期格式不正确: {str(e)}",
        )

    # 验证日期范围
    if start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="开始日期不能晚于结束日期",
        )

    # 查询数据库
    stats = (
        db.query(GithubDailyStat)
        .filter(
            GithubDailyStat.user_id == current_user.id,
            GithubDailyStat.date >= start_date,
            GithubDailyStat.date <= end_date,
        )
        .order_by(GithubDailyStat.date)
        .all()
    )

    return GithubDailyStatsQueryResponse(
        data=stats,
        total=len(stats),
    )

