#!/usr/bin/env python3
"""
环境验证测试 v3
简化API调用
"""

import asyncio
import os
import sys

os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:8118'
os.environ['HTTP_PROXY'] = 'http://127.0.0.1:8118'

async def test_environment():
    try:
        from crawl4ai import AsyncWebCrawler, BrowserConfig

        print("✅ 导入crawl4ai成功")

        # 简单浏览器配置
        browser_config = BrowserConfig(
            headless=True,
            verbose=True,
            browser_type="chromium",
        )

        crawler = AsyncWebCrawler(config=browser_config)

        print("🔄 尝试访问 example.com (直接参数)...")

        # 尝试直接传递参数
        result = await crawler.arun(
            url="https://example.com",
            strategy="dynamic",
            wait_for="body",
            timeout=30000,
            verbose=True
        )

        if result.success:
            print(f"✅ 爬取成功!")
            print(f"   HTML长度: {len(result.html)} 字符")
            return True
        else:
            print(f"❌ 爬取失败: {result.error_message}")
            return False

    except Exception as e:
        print(f"❌ 测试异常: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("环境测试 v3 - 直接参数")
    print("=" * 60)

    try:
        success = asyncio.run(test_environment())
        if success:
            print("\n🎉 测试通过!")
        else:
            print("\n⚠️ 测试失败")
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n💥 异常: {e}")
        sys.exit(1)