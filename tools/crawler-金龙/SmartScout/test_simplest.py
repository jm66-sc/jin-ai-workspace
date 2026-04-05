#!/usr/bin/env python3
# test_simplest.py - 最简单的测试，不使用CrawlerRunConfig

import os
import sys
import asyncio
from crawl4ai import AsyncWebCrawler, BrowserConfig

print("="*60)
print("🧪 最简单的Crawl4AI测试")
print("="*60)

# 清除代理
for var in ['http_proxy', 'https_proxy', 'HTTP_PROXY', 'HTTPS_PROXY']:
    os.environ.pop(var, None)
os.environ['NO_PROXY'] = '*'

async def test_simplest():
    """最简单的测试，不使用CrawlerRunConfig"""

    # 最简单的浏览器配置
    browser_config = BrowserConfig(
        browser_mode="chromium",  # 使用标准模式
        headless=True,            # 无头模式
        user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )

    print("📋 配置:")
    print(f"  - browser_mode: {browser_config.browser_mode}")
    print(f"  - headless: {browser_config.headless}")

    async with AsyncWebCrawler(config=browser_config) as crawler:
        # 测试1: example.com - 不使用CrawlerRunConfig
        print("\n1. 测试 example.com (不使用CrawlerRunConfig)...")
        try:
            # 直接在arun中传递参数
            result = await crawler.arun(
                url="https://example.com",
                strategy="dynamic",
                wait_for="body",
                timeout=30000,
                verbose=False  # 不显示详细日志
            )
            print(f"   ✅ 成功: {result.success}")
            if result.success:
                print(f"   标题: {result.metadata.get('title', 'N/A')}")
                print(f"   内容长度: {len(result.html)} 字符")
            else:
                print(f"   ❌ 错误: {result.error_message}")
        except Exception as e:
            print(f"   ❌ 异常: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()

        # 测试2: 使用官方防检测配置
        print("\n2. 测试官方防检测配置...")
        browser_config2 = BrowserConfig(
            browser_mode="undetected",      # 防检测模式
            enable_stealth=True,           # 隐身模式
            headless=False,                # 显示窗口
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            proxy=None                     # 禁用代理
        )

        async with AsyncWebCrawler(config=browser_config2) as crawler2:
            try:
                result2 = await crawler2.arun(
                    url="https://example.com",
                    strategy="dynamic",
                    wait_for="body",
                    timeout=30000,
                    verbose=False
                )
                print(f"   ✅ 成功: {result2.success}")
                if result2.success:
                    print(f"   标题: {result2.metadata.get('title', 'N/A')}")
                    print(f"   内容长度: {len(result2.html)} 字符")
                else:
                    print(f"   ❌ 错误: {result2.error_message}")
            except Exception as e:
                print(f"   ❌ 异常: {type(e).__name__}: {e}")

        return True

if __name__ == "__main__":
    asyncio.run(test_simplest())
    print("\n" + "="*60)
    print("测试完成")
    print("="*60)