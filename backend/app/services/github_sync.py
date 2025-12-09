"""
GitHub 数据同步服务
调用 GitHub API，获取用户数据并进行聚合
"""
from datetime import date, datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple

import httpx
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models import GithubDailyStat, GithubRepo, User


async def fetch_user_repos(github_token: str) -> List[dict]:
    """
    获取用户的所有仓库列表

    Args:
        github_token: GitHub access token

    Returns:
        仓库列表，每个仓库包含 id, name, full_name, private, language, html_url, description

    Raises:
        httpx.HTTPError: 如果 API 请求失败
    """
    repos = []
    page = 1
    per_page = 100

    async with httpx.AsyncClient() as client:
        while True:
            url = f"{settings.GITHUB_API_BASE_URL}/user/repos"
            params = {
                "page": page,
                "per_page": per_page,
                "sort": "updated",
                "direction": "desc",
            }

            response = await client.get(
                url,
                params=params,
                headers={
                    "Authorization": f"Bearer {github_token}",
                    "Accept": "application/vnd.github.v3+json",
                },
                timeout=10.0,
            )
            response.raise_for_status()

            page_repos = response.json()
            if not page_repos:
                break

            repos.extend(page_repos)
            page += 1

            # 如果返回的仓库数少于 per_page，说明已经是最后一页
            if len(page_repos) < per_page:
                break

    return repos


async def fetch_user_events(github_token: str, days: int = 90) -> List[dict]:
    """
    获取用户的事件列表（包括 push、pull request、issue 等）

    Args:
        github_token: GitHub access token
        days: 获取最近多少天的事件（默认 90 天）

    Returns:
        事件列表，每个事件包含 type, created_at, payload 等信息

    Raises:
        httpx.HTTPError: 如果 API 请求失败
    """
    events = []
    page = 1
    per_page = 100
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)

    async with httpx.AsyncClient() as client:
        while True:
            url = f"{settings.GITHUB_API_BASE_URL}/users/{{user}}/events"
            
            # 首先获取用户信息以获取用户名
            user_response = await client.get(
                f"{settings.GITHUB_API_BASE_URL}/user",
                headers={
                    "Authorization": f"Bearer {github_token}",
                    "Accept": "application/vnd.github.v3+json",
                },
                timeout=10.0,
            )
            user_response.raise_for_status()
            username = user_response.json()["login"]

            # 获取用户事件
            url = f"{settings.GITHUB_API_BASE_URL}/users/{username}/events"
            params = {
                "page": page,
                "per_page": per_page,
            }

            response = await client.get(
                url,
                params=params,
                headers={
                    "Authorization": f"Bearer {github_token}",
                    "Accept": "application/vnd.github.v3+json",
                },
                timeout=10.0,
            )
            response.raise_for_status()

            page_events = response.json()
            if not page_events:
                break

            # 过滤超出时间范围的事件
            for event in page_events:
                event_date = datetime.fromisoformat(event["created_at"].replace("Z", "+00:00"))
                if event_date < cutoff_date:
                    # 已经超出时间范围，停止获取
                    return events

                events.append(event)

            page += 1

            # 如果返回的事件数少于 per_page，说明已经是最后一页
            if len(page_events) < per_page:
                break

    return events


def aggregate_daily_stats(events: List[dict]) -> Dict[date, Dict[str, int]]:
    """
    聚合事件数据，按日期统计各类活动

    Args:
        events: GitHub 事件列表

    Returns:
        按日期聚合的统计数据，格式：
        {
            date(2025-01-01): {
                "commit_count": 5,
                "pr_count": 1,
                "issue_count": 0,
                "star_delta": 0,
            },
            ...
        }
    """
    stats: Dict[date, Dict[str, int]] = {}

    for event in events:
        # 解析事件时间
        event_date_str = event["created_at"]
        event_datetime = datetime.fromisoformat(event_date_str.replace("Z", "+00:00"))
        event_date = event_datetime.date()

        # 初始化该日期的统计数据
        if event_date not in stats:
            stats[event_date] = {
                "commit_count": 0,
                "pr_count": 0,
                "issue_count": 0,
                "star_delta": 0,
            }

        # 根据事件类型统计
        event_type = event.get("type", "")

        if event_type == "PushEvent":
            # 统计 push 中的 commit 数
            payload = event.get("payload", {})
            commits = payload.get("commits", [])
            stats[event_date]["commit_count"] += len(commits)

        elif event_type == "PullRequestEvent":
            action = event.get("payload", {}).get("action", "")
            if action == "opened":
                stats[event_date]["pr_count"] += 1

        elif event_type == "IssuesEvent":
            action = event.get("payload", {}).get("action", "")
            if action == "opened":
                stats[event_date]["issue_count"] += 1

        elif event_type == "WatchEvent":
            # Star 事件
            stats[event_date]["star_delta"] += 1

    return stats


async def sync_github_data(
    user: User, db: Session
) -> Tuple[int, int]:
    """
    同步用户的 GitHub 数据

    Args:
        user: 用户对象
        db: 数据库会话

    Returns:
        (repos_count, stats_updated_count) - 仓库数和更新的统计记录数

    Raises:
        httpx.HTTPError: 如果 API 请求失败
    """
    github_token = user.github_access_token

    # 第 1 步：获取仓库列表
    repos = await fetch_user_repos(github_token)

    # 更新仓库信息
    for repo_data in repos:
        existing_repo = db.query(GithubRepo).filter(
            GithubRepo.repo_id == repo_data["id"]
        ).first()

        if existing_repo:
            # 更新现有仓库
            existing_repo.name = repo_data["name"]
            existing_repo.full_name = repo_data["full_name"]
            existing_repo.private = repo_data["private"]
            existing_repo.language = repo_data.get("language")
            existing_repo.html_url = repo_data["html_url"]
            existing_repo.description = repo_data.get("description")
        else:
            # 创建新仓库
            new_repo = GithubRepo(
                user_id=user.id,
                repo_id=repo_data["id"],
                name=repo_data["name"],
                full_name=repo_data["full_name"],
                private=repo_data["private"],
                language=repo_data.get("language"),
                html_url=repo_data["html_url"],
                description=repo_data.get("description"),
            )
            db.add(new_repo)

    db.commit()

    # 第 2 步：获取用户事件
    events = await fetch_user_events(github_token, days=90)

    # 第 3 步：聚合每日统计
    daily_stats = aggregate_daily_stats(events)

    # 第 4 步：更新数据库中的每日统计
    stats_updated = 0
    for stat_date, stat_data in daily_stats.items():
        existing_stat = db.query(GithubDailyStat).filter(
            GithubDailyStat.user_id == user.id,
            GithubDailyStat.date == stat_date,
        ).first()

        if existing_stat:
            # 更新现有统计
            existing_stat.commit_count = stat_data["commit_count"]
            existing_stat.pr_count = stat_data["pr_count"]
            existing_stat.issue_count = stat_data["issue_count"]
            existing_stat.star_delta = stat_data["star_delta"]
        else:
            # 创建新统计
            new_stat = GithubDailyStat(
                user_id=user.id,
                date=stat_date,
                commit_count=stat_data["commit_count"],
                pr_count=stat_data["pr_count"],
                issue_count=stat_data["issue_count"],
                star_delta=stat_data["star_delta"],
            )
            db.add(new_stat)

        stats_updated += 1

    db.commit()

    return len(repos), stats_updated

