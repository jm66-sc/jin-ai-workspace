#!/usr/bin/env python3
# test_direct.py - 直接测试Crawl4AI，不使用代理

from crawl4ai import AsyncWebCrawler
import asyncio
import sys

async def test_crawl():
    """测试最简单的一行代码调用"""
    print("🧪 测试最简单的一行代码调用")
    print(f"Python版本: {sys.version.split()[0]}")

    try:
        # 尝试导入版本信息
        import crawl4ai
        if hasattr(crawl4ai, '__version__'):
            print(f"Crawl4AI版本: {crawl4ai.__version__}")
    except:
        pass

    crawler = AsyncWebCrawler()

    # 测试1: 先测试一个简单网站
    print("\n1. 测试 example.com...")
    try:
        result = await crawler.crawl(
            url="https://example.com",
            strategy="dynamic",
            wait_for="body",
            timeout=30000,
        )
        print(f"   成功: {result.success}")
        print(f"   错误信息: {result.error_message if result.error_message else '无'}")
        print(f"   HTML长度: {len(result.cleaned_html) if result.cleaned_html else 0}")
    except Exception as e:
        print(f"   异常: {type(e).__name__}: {e}")

    # 测试2: 测试目标网站
    print("\n2. 测试目标网站 (政府采购)...")
    try:
        result2 = await crawler.crawl(
            url="https://www.ccgp-sichuan.gov.cn",
            strategy="dynamic",
            wait_for="body",
            timeout=60000,
        )
        print(f"   成功: {result2.success}")
        print(f"   错误信息: {result2.error_message if result2.error_message else '无'}")
        print(f"   HTML长度: {len(result2.cleaned_html) if result2.cleaned_html else 0}")
        if result2.success and result2.cleaned_html:
            print(f"   HTML预览: {result2.cleaned_html[:200]}")
    except Exception as e:
        print(f"   异常: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

    # 测试3: 测试搜索页面
    print("\n3. 测试搜索页面...")
    try:
        result3 = await crawler.crawl(
            url="https://www.ccgp-sichuan.gov.cn/maincms-web/fullSearching?searchKey=消防",
            strategy="dynamic",
            wait_for=".list-item",
            timeout=90000,
        )
        print(f"   成功: {result3.success}")
        print(f"   错误信息: {result3.error_message if result3.error_message else '无'}")
        print(f"   HTML长度: {len(result3.cleaned_html) if result3.cleaned_html else 0}")
    except Exception as e:
        print(f"   异常: {type(e).__name__}: {e}")

    await crawler.close()

if __name__ == "__main__":
    asyncio.run(test_crawl())