#!/usr/bin/env python3
# test_simple.py - 最简单的测试

from crawl4ai import AsyncWebCrawler
import asyncio
import os
import sys

# 代理设置
os.environ['https_proxy'] = 'http://127.0.0.1:8118'
os.environ['http_proxy'] = 'http://127.0.0.1:8118'

async def test_simple():
    """最简单的测试"""
    print("🚀 简单测试...")

    # 测试1: 先测试example.com
    print("\n1️⃣ 测试 example.com...")
    crawler = AsyncWebCrawler()

    try:
        result = await crawler.arun(
            url="https://example.com",
            strategy="dynamic",
            wait_for="body",
            timeout=30000,
        )

        if hasattr(result, '_results') and len(result._results) > 0:
            actual = result._results[0]
            print(f"   ✅ 成功: {actual.success}")
            print(f"   📄 HTML长度: {len(actual.cleaned_html) if actual.cleaned_html else 0}")
        else:
            print(f"   ❌ 结果结构异常")

    except Exception as e:
        print(f"   ❌ 错误: {type(e).__name__}: {e}")

    await crawler.close()

    # 测试2: 尝试百度
    print("\n2️⃣ 测试 baidu.com...")
    crawler2 = AsyncWebCrawler()

    try:
        result2 = await crawler2.arun(
            url="https://baidu.com",
            strategy="dynamic",
            wait_for="body",
            timeout=30000,
        )

        if hasattr(result2, '_results') and len(result2._results) > 0:
            actual2 = result2._results[0]
            print(f"   ✅ 成功: {actual2.success}")
            print(f"   📄 HTML长度: {len(actual2.cleaned_html) if actual2.cleaned_html else 0}")
        else:
            print(f"   ❌ 结果结构异常")

    except Exception as e:
        print(f"   ❌ 错误: {type(e).__name__}: {e}")

    await crawler2.close()

    # 测试3: 尝试政府采购网站（不带搜索参数）
    print("\n3️⃣ 测试政府采购网站主页...")
    crawler3 = AsyncWebCrawler()

    try:
        result3 = await crawler3.arun(
            url="https://www.ccgp-sichuan.gov.cn",
            strategy="dynamic",
            wait_for="body",
            timeout=60000,
        )

        if hasattr(result3, '_results') and len(result3._results) > 0:
            actual3 = result3._results[0]
            print(f"   ✅ 成功: {actual3.success}")
            print(f"   📄 HTML长度: {len(actual3.cleaned_html) if actual3.cleaned_html else 0}")
            print(f"   ❌ 错误: {actual3.error_message if actual3.error_message else '无'}")

            if actual3.success and actual3.cleaned_html:
                print(f"   🔍 预览: {actual3.cleaned_html[:200]}")
        else:
            print(f"   ❌ 结果结构异常")

    except Exception as e:
        print(f"   ❌ 错误: {type(e).__name__}: {e}")

    await crawler3.close()

if __name__ == "__main__":
    print("🔧 Python版本:", sys.version.split()[0])
    asyncio.run(test_simple())