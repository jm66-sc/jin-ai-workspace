#!/usr/bin/env python3
# 检查CrawlResult对象结构

import asyncio
from crawl4ai import AsyncWebCrawler
import os

os.environ['https_proxy'] = 'http://127.0.0.1:8118'
os.environ['http_proxy'] = 'http://127.0.0.1:8118'

async def check_structure():
    crawler = AsyncWebCrawler()

    try:
        # 使用example.com测试
        result = await crawler.arun(
            url="https://example.com",
            strategy="dynamic",
            wait_for="body",
            timeout=10000,
            verbose=False
        )

        print("✅ 爬取成功，检查CrawlResult结构...")
        print(f"result类型: {type(result)}")
        print(f"result.success: {result.success}")
        print(f"result.html长度: {len(result.html) if result.html else 0}")

        # 列出所有属性
        print("\n📋 属性列表:")
        attrs = [attr for attr in dir(result) if not attr.startswith('_')]
        for attr in attrs[:20]:  # 先显示前20个
            try:
                value = getattr(result, attr)
                if not callable(value):
                    print(f"  {attr}: {type(value)} = {repr(value)[:100]}")
            except:
                print(f"  {attr}: <无法访问>")

        # 检查_objects
        print("\n🔍 检查_objects:")
        if hasattr(result, '_objects'):
            print(f"  _objects: {type(result._objects)}")

        # 检查_results
        print("\n🔍 检查_results:")
        if hasattr(result, '_results'):
            print(f"  _results长度: {len(result._results)}")
            if result._results:
                first = result._results[0]
                print(f"  第一个结果类型: {type(first)}")
                print(f"  第一个结果属性: {[a for a in dir(first) if not a.startswith('_')][:10]}")

    except Exception as e:
        print(f"❌ 错误: {e}")
    finally:
        await crawler.close()

if __name__ == "__main__":
    asyncio.run(check_structure())