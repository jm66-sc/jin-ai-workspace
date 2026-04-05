#!/usr/bin/env python3
# test_no_verbose.py - 不使用verbose参数的测试

import asyncio
import sys
from crawl4ai import AsyncWebCrawler

async def test_no_verbose():
    print("🧪 测试（无verbose参数）")
    print(f"Python: {sys.version.split()[0]}")
    print(f"crawl4ai: 0.8.0")

    crawler = AsyncWebCrawler()

    # 测试1: example.com (应该100%成功)
    print("\n1. 测试 example.com...")
    try:
        # 移除verbose参数
        result = await crawler.arun(
            url="https://example.com",
            strategy="dynamic",
            wait_for="body",
            timeout=30000,
            # 不传递verbose参数
        )

        print(f"   成功: {result.success}")
        if result.success:
            print(f"   标题: {result.metadata.get('title', 'N/A')}")
            print(f"   HTML长度: {len(result.html)}")
        else:
            print(f"   错误: {result.error_message}")

    except Exception as e:
        print(f"   异常: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

    # 测试2: 政府采购网站主页
    print("\n2. 测试政府采购网站主页...")
    try:
        result2 = await crawler.arun(
            url="https://www.ccgp-sichuan.gov.cn",
            strategy="dynamic",
            wait_for="body",
            timeout=60000,
            # 不传递verbose参数
        )

        print(f"   成功: {result2.success}")
        if result2.success:
            print(f"   标题: {result2.metadata.get('title', 'N/A')}")
            print(f"   HTML长度: {len(result2.html)}")
        else:
            print(f"   错误: {result2.error_message}")

    except Exception as e:
        print(f"   异常: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

    await crawler.close()

    print("\n" + "="*60)
    print("测试完成")

    # 网络连通性测试
    print("\n🌐 网络连通性测试:")
    try:
        import requests
        print("   尝试使用requests库访问...")
        response = requests.get("https://www.ccgp-sichuan.gov.cn", timeout=10)
        print(f"   Status Code: {response.status_code}")
        print(f"   内容长度: {len(response.text)}")
    except Exception as e:
        print(f"   ❌ requests访问失败: {e}")

    return result2.success if 'result2' in locals() else False

if __name__ == "__main__":
    success = asyncio.run(test_no_verbose())