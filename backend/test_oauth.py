#!/usr/bin/env python3
"""
GitHub OAuth 流程测试脚本
用于验证 OAuth 端点是否正常工作
"""
import asyncio
import json
from typing import Optional

import httpx

# 配置
API_BASE_URL = "http://localhost:8000"
GITHUB_CLIENT_ID = "your_github_client_id"  # 需要替换为实际的 Client ID


async def test_github_login():
    """测试 GET /auth/github/login 端点"""
    print("\n" + "=" * 60)
    print("测试 1: GET /auth/github/login")
    print("=" * 60)

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{API_BASE_URL}/auth/github/login")
            response.raise_for_status()

            data = response.json()
            print("✓ 请求成功")
            print(f"  状态码: {response.status_code}")
            print(f"  响应数据:")
            print(json.dumps(data, indent=2, ensure_ascii=False))

            if "authorization_url" in data:
                print(f"\n✓ 授权 URL 已生成")
                print(f"  你可以在浏览器中打开此 URL 进行授权:")
                print(f"  {data['authorization_url'][:80]}...")
                return True
            else:
                print("❌ 响应中缺少 authorization_url")
                return False

        except httpx.HTTPError as e:
            print(f"❌ 请求失败: {e}")
            return False


async def test_health():
    """测试 GET /health 端点"""
    print("\n" + "=" * 60)
    print("测试 0: GET /health (健康检查)")
    print("=" * 60)

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{API_BASE_URL}/health")
            response.raise_for_status()

            data = response.json()
            print("✓ API 服务正常运行")
            print(f"  状态码: {response.status_code}")
            print(f"  响应数据: {data}")
            return True

        except httpx.HTTPError as e:
            print(f"❌ API 服务无法访问: {e}")
            print(f"  请确保后端服务已启动: python -m uvicorn app.main:app --reload")
            return False


async def test_callback_without_code():
    """测试 GET /auth/github/callback 端点（不带 code）"""
    print("\n" + "=" * 60)
    print("测试 2: GET /auth/github/callback (缺少 code 参数)")
    print("=" * 60)

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{API_BASE_URL}/auth/github/callback")
            print(f"  状态码: {response.status_code}")

            if response.status_code == 422:
                print("✓ 正确返回 422 (缺少必要参数)")
                data = response.json()
                print(f"  错误详情: {data['detail'][0]['msg']}")
                return True
            else:
                print(f"❌ 预期状态码 422，实际: {response.status_code}")
                return False

        except httpx.HTTPError as e:
            print(f"❌ 请求失败: {e}")
            return False


async def test_api_docs():
    """测试 API 文档是否可访问"""
    print("\n" + "=" * 60)
    print("测试 3: API 文档可访问性")
    print("=" * 60)

    async with httpx.AsyncClient() as client:
        try:
            # 测试 Swagger UI
            response = await client.get(f"{API_BASE_URL}/docs")
            if response.status_code == 200:
                print("✓ Swagger UI 可访问")
                print(f"  访问地址: {API_BASE_URL}/docs")
            else:
                print(f"❌ Swagger UI 无法访问 (状态码: {response.status_code})")

            # 测试 OpenAPI schema
            response = await client.get(f"{API_BASE_URL}/openapi.json")
            if response.status_code == 200:
                print("✓ OpenAPI schema 可访问")
                data = response.json()
                print(f"  API 标题: {data.get('info', {}).get('title')}")
                print(f"  API 版本: {data.get('info', {}).get('version')}")
            else:
                print(f"❌ OpenAPI schema 无法访问 (状态码: {response.status_code})")

            return True

        except httpx.HTTPError as e:
            print(f"❌ 请求失败: {e}")
            return False


async def main():
    """主测试函数"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 58 + "║")
    print("║" + "  DevOrbit GitHub OAuth 流程测试".center(58) + "║")
    print("║" + " " * 58 + "║")
    print("╚" + "=" * 58 + "╝")

    results = []

    # 测试 1: 健康检查
    results.append(("健康检查", await test_health()))

    if not results[-1][1]:
        print("\n❌ 后端服务未运行，无法继续测试")
        return

    # 测试 2: GitHub 登录
    results.append(("GitHub 登录", await test_github_login()))

    # 测试 3: 回调端点（缺少 code）
    results.append(("回调端点验证", await test_callback_without_code()))

    # 测试 4: API 文档
    results.append(("API 文档", await test_api_docs()))

    # 总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✓" if result else "❌"
        print(f"{status} {name}")

    print(f"\n通过: {passed}/{total}")

    if passed == total:
        print("\n🎉 所有测试都通过了！")
        print("\n下一步:")
        print("1. 在 .env 文件中填入 GitHub OAuth 凭证")
        print("2. 访问 http://localhost:8000/docs 查看 API 文档")
        print("3. 点击 'Try it out' 测试 /auth/github/login 端点")
        print("4. 在浏览器中打开返回的授权 URL 进行授权")
    else:
        print("\n⚠️  有些测试未通过，请检查错误信息")

    print()


if __name__ == "__main__":
    asyncio.run(main())

