#!/usr/bin/env python3
"""
⚠️ 注意：此文件基于 Crawl4AI v0.6.3 编写
升级到 v0.8.x+ 后，需要更新API调用方式

v0.6.3 与 v0.8.x+ 的主要API差异：
1. v0.6.3: 使用 crawler.crawl() 方法，但参数有限
2. v0.8.x+: 支持 strategy="dynamic" 参数，智能等待机制

【更新建议】
- 将测试URL更换为目标网站
- 测试 strategy="dynamic" 参数
- 验证 wait_for 选择器的效果
================================================================================

测试Crawl4AI 0.6.3 API（需要升级到v0.8.x+）"""
import asyncio
import crawl4ai
from crawl4ai import AsyncWebCrawler

async def test_api():
    print("测试Crawl4AI AsyncWebCrawler API")

    # 创建爬虫实例
    crawler = AsyncWebCrawler(verbose=True)

    # 检查可用方法
    print("\nAsyncWebCrawler方法列表:")
    methods = [m for m in dir(crawler) if not m.startswith('_')]
    for m in methods:
        print(f"  - {m}")

    # 检查crawl方法是否存在
    if hasattr(crawler, 'crawl'):
        print("\n'crawl'方法存在")
        # 检查参数
        import inspect
        sig = inspect.signature(crawler.crawl)
        print(f"crawl方法签名: {sig}")

    if hasattr(crawler, 'run'):
        print("\n'run'方法存在")

    if hasattr(crawler, 'fetch'):
        print("\n'fetch'方法存在")

    # 尝试调用crawl方法（不实际抓取）
    print("\n尝试调用crawl方法...")
    try:
        # 只测试方法调用，使用一个简单URL
        result = await crawler.crawl(url="https://example.com", strategy="static", verbose=False)
        print(f"调用成功，返回类型: {type(result)}")
        if hasattr(result, 'success'):
            print(f"success属性: {result.success}")
        if hasattr(result, 'html'):
            print(f"html长度: {len(result.html) if result.html else 0}")
    except Exception as e:
        print(f"调用失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_api())