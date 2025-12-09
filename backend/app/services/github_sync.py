"""
GitHub 数据同步服务
调用 GitHub API，获取用户数据并进行聚合
"""
from datetime import date, datetime, time, timedelta, timezone
from typing import Dict, List, Optional, Tuple
import collections
import logging
import sys
from calendar import monthrange

import httpx
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models import GithubDailyStat, GithubRepo, User

logger = logging.getLogger(__name__)


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


async def fetch_current_username(github_token: str) -> str:
    async with httpx.AsyncClient() as client:
        user_response = await client.get(
            f"{settings.GITHUB_API_BASE_URL}/user",
            headers={
                "Authorization": f"Bearer {github_token}",
                "Accept": "application/vnd.github.v3+json",
            },
            timeout=10.0,
        )
        user_response.raise_for_status()
        return user_response.json()["login"]


async def fetch_user_events(
    github_token: str,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    days: int = 90,
) -> List[dict]:
    """
    获取用户的事件列表（包括 push、pull request、issue 等）

    Args:
        github_token: GitHub access token
        start_date: 开始日期（不传则使用 days 计算）
        end_date: 结束日期（不传则默认为当前时间）
        days: 当未指定 start_date 时，获取最近多少天的事件（默认 90 天）

    Returns:
        事件列表，每个事件包含 type, created_at, payload 等信息

    Raises:
        httpx.HTTPError: 如果 API 请求失败
    """
    events: List[dict] = []
    page = 1
    per_page = 100
    end_dt = (
        datetime.combine(end_date, time.max, tzinfo=timezone.utc)
        if end_date
        else datetime.now(timezone.utc)
    )
    cutoff_date = (
        datetime.combine(start_date, time.min, tzinfo=timezone.utc)
        if start_date
        else end_dt - timedelta(days=days)
    )

    async with httpx.AsyncClient() as client:
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

        while True:
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

                # 过滤结束日期之后的事件
                if event_date > end_dt:
                    continue

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
            if commits:
                stats[event_date]["commit_count"] += len(commits)
            else:
                # 有些事件只包含 size，不返回 commits 列表
                size = payload.get("size")
                if isinstance(size, int) and size > 0:
                    stats[event_date]["commit_count"] += size
                else:
                    # 最少按 1 次提交计入，避免被漏记
                    stats[event_date]["commit_count"] += 1

        elif event_type == "PullRequestEvent":
            action = event.get("payload", {}).get("action", "")
            # opened / reopened / closed (包含 merged) 都计一次
            if action in {"opened", "reopened", "closed"}:
                stats[event_date]["pr_count"] += 1

        elif event_type == "IssuesEvent":
            action = event.get("payload", {}).get("action", "")
            if action in {"opened", "reopened"}:
                stats[event_date]["issue_count"] += 1

        elif event_type == "WatchEvent":
            # Star 事件
            stats[event_date]["star_delta"] += 1
        elif event_type == "PublicEvent":
            # 仓库公开事件，按 1 次 star 增量处理，避免丢失
            stats[event_date]["star_delta"] += 1

    return stats


def _month_chunks(start_date: date, end_date: date) -> List[Tuple[date, date]]:
    chunks: List[Tuple[date, date]] = []
    cursor = start_date
    while cursor <= end_date:
        last_day = monthrange(cursor.year, cursor.month)[1]
        chunk_end = date(cursor.year, cursor.month, last_day)
        if chunk_end > end_date:
            chunk_end = end_date
        chunks.append((cursor, chunk_end))
        cursor = chunk_end + timedelta(days=1)
    return chunks


async def _search_github(
    github_token: str, url: str, params: dict, accept: str = "application/vnd.github+json"
) -> List[dict]:
    items: List[dict] = []
    page = 1
    per_page = 100
    async with httpx.AsyncClient() as client:
        while True:
            resp = await client.get(
                url,
                params={**params, "page": page, "per_page": per_page},
                headers={
                    "Authorization": f"Bearer {github_token}",
                    "Accept": accept,
                },
                timeout=15.0,
            )
            resp.raise_for_status()
            data = resp.json()
            page_items = data.get("items", [])
            items.extend(page_items)
            if len(page_items) < per_page:
                break
            page += 1
    return items


async def search_commits_by_range(
    github_token: str, username: str, start_date: date, end_date: date
) -> List[datetime]:
    dates: List[datetime] = []
    for chunk_start, chunk_end in _month_chunks(start_date, end_date):
        query = f"author:{username} committer-date:{chunk_start}..{chunk_end}"
        items = await _search_github(
            github_token,
            f"{settings.GITHUB_API_BASE_URL}/search/commits",
            {"q": query, "sort": "committer-date", "order": "asc"},
            accept="application/vnd.github.cloak-preview+json",
        )
        for item in items:
            commit = item.get("commit", {})
            dt_str = commit.get("author", {}).get("date") or commit.get("committer", {}).get("date")
            if dt_str:
                dates.append(datetime.fromisoformat(dt_str.replace("Z", "+00:00")))
    return dates


async def search_issues_pr_by_range(
    github_token: str, username: str, start_date: date, end_date: date, is_pr: bool
) -> List[datetime]:
    dates: List[datetime] = []
    type_filter = "pr" if is_pr else "issue"
    for chunk_start, chunk_end in _month_chunks(start_date, end_date):
        query = f"author:{username} type:{type_filter} created:{chunk_start}..{chunk_end}"
        items = await _search_github(
            github_token,
            f"{settings.GITHUB_API_BASE_URL}/search/issues",
            {"q": query, "sort": "created", "order": "asc"},
        )
        for item in items:
            dt_str = item.get("created_at")
            if dt_str:
                dates.append(datetime.fromisoformat(dt_str.replace("Z", "+00:00")))
    return dates


async def fetch_repo_stars_delta(
    github_token: str, repos: List[dict], start_date: date, end_date: date
) -> List[datetime]:
    """使用 GitHub GraphQL 拉取每个仓库在时间范围内的 star 事件时间"""
    if not repos:
        return []
    gql_url = "https://api.github.com/graphql"
    query = """
    query ($owner: String!, $name: String!, $after: String) {
      repository(owner: $owner, name: $name) {
        stargazers(first: 100, after: $after, orderBy: {field: STARRED_AT, direction: ASC}) {
          pageInfo { hasNextPage endCursor }
          edges { starredAt }
        }
      }
    }
    """
    headers = {
        "Authorization": f"Bearer {github_token}",
        "Accept": "application/vnd.github+json",
    }
    collected: List[datetime] = []

    async with httpx.AsyncClient() as client:
        for repo in repos:
            full_name = repo.get("full_name") if isinstance(repo, dict) else getattr(repo, "full_name", "")
            if not full_name:
                continue
            owner, name = full_name.split("/", 1)
            after = None
            while True:
                resp = await client.post(
                    gql_url,
                    json={"query": query, "variables": {"owner": owner, "name": name, "after": after}},
                    headers=headers,
                    timeout=20.0,
                )
                resp.raise_for_status()
                data = resp.json()
                edges = (
                    data.get("data", {})
                    .get("repository", {})
                    .get("stargazers", {})
                    .get("edges", [])
                )
                page_info = (
                    data.get("data", {})
                    .get("repository", {})
                    .get("stargazers", {})
                    .get("pageInfo", {})
                )
                for edge in edges:
                    starred_at = edge.get("starredAt")
                    if starred_at:
                        dt = datetime.fromisoformat(starred_at.replace("Z", "+00:00"))
                        if dt.date() < start_date:
                            continue
                        if dt.date() > end_date:
                            # 因为按时间升序，超过范围即可停止本仓库
                            page_info["hasNextPage"] = False
                            break
                        collected.append(dt)
                if not page_info.get("hasNextPage"):
                    break
                after = page_info.get("endCursor")
    return collected


def aggregate_deep_stats(
    commit_dates: List[datetime],
    pr_dates: List[datetime],
    issue_dates: List[datetime],
    star_dates: List[datetime],
) -> Dict[date, Dict[str, int]]:
    stats: Dict[date, Dict[str, int]] = {}

    def _add(d: date, key: str, amount: int = 1):
        if d not in stats:
            stats[d] = {"commit_count": 0, "pr_count": 0, "issue_count": 0, "star_delta": 0}
        stats[d][key] += amount

    for dt in commit_dates:
        _add(dt.date(), "commit_count", 1)
    for dt in pr_dates:
        _add(dt.date(), "pr_count", 1)
    for dt in issue_dates:
        _add(dt.date(), "issue_count", 1)
    for dt in star_dates:
        _add(dt.date(), "star_delta", 1)

    return stats


async def sync_github_data(
    user: User,
    db: Session,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    days: int = 90,
    mode: str = "standard",
) -> Tuple[int, int]:
    """
    同步用户的 GitHub 数据

    Args:
        user: 用户对象
        db: 数据库会话
        start_date: 同步的开始日期
        end_date: 同步的结束日期
        days: 未提供开始日期时默认回溯的天数
        mode: standard（90 天事件）/ deep（任意时间段，使用搜索+GraphQL）

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

    def _log(msg: str):
        # print + flush 确保在容器/终端可见
        print(msg, file=sys.stdout, flush=True)
        logger.info(msg)

    if mode == "deep":
        username = await fetch_current_username(github_token)
        _log(f"[github_sync][deep] username={username} range={start_date}..{end_date}")
        commit_dates = await search_commits_by_range(github_token, username, start_date, end_date)
        pr_dates = await search_issues_pr_by_range(github_token, username, start_date, end_date, True)
        issue_dates = await search_issues_pr_by_range(
            github_token, username, start_date, end_date, False
        )
        star_dates = await fetch_repo_stars_delta(github_token, repos, start_date, end_date)

        _log(
            f"[github_sync][deep] commits={len(commit_dates)} prs={len(pr_dates)} issues={len(issue_dates)} stars={len(star_dates)}"
        )
        daily_stats = aggregate_deep_stats(commit_dates, pr_dates, issue_dates, star_dates)
    else:
        # 第 2 步：获取用户事件（仅近 90 天）
        events = await fetch_user_events(
            github_token,
            start_date=start_date,
            end_date=end_date,
            days=days,
        )
        event_types = collections.Counter(e.get("type", "") for e in events)
        first_event = events[0] if events else None
        _log(f"[github_sync] events total={len(events)} types={dict(event_types)}")
        _log(f"[github_sync] first event={first_event}")

        # 第 3 步：聚合每日统计
        daily_stats = aggregate_daily_stats(events)
        _log(f"[github_sync] aggregated days={len(daily_stats)}")

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

