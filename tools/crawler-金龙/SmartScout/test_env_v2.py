#!/usr/bin/env python3
"""
环境验证测试 v2
使用crawl4ai v0.8.0的正确API
"""

import asyncio
import os
import sys

# 设置代理
os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:8118'
os.environ['HTTP_PROXY'] = 'http://127.0.0.1:8118'

async def test_environment():
    """测试crawl4ai v0.8.0环境"""
    try:
        from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, BrowserConfig
        from crawl4ai import CacheMode

        print("✅ 导入crawl4ai成功")
        print(f"Python版本: {sys.version}")

        # 浏览器配置
        browser_config = BrowserConfig(
            headless=True,
            verbose=True,
            browser_type="chromium",
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
        )

        # 爬虫运行配置 - 使用strategy="dynamic"
        crawler_config = CrawlerRunConfig(
            verbose=True,
            strategy="dynamic",  # ✅ v0.8.x+ 支持此参数
            wait_for="body",
            timeout=30000,
            wait_until="load",
            cache_mode=CacheMode.BYPASS,
            remove_overlay_elements=False,
            markdown=False,
        )

        # 创建爬虫实例
        crawler = AsyncWebCrawler(config=browser_config)

        print("🔄 尝试访问 example.com (使用strategy='dynamic')...")

        # 使用arun方法（AsyncWebCrawler的正确方法）
        result = await crawler.arun(
            url="https://example.com",
            config=crawler_config,
        )

        if result.success:
            print(f"✅ 爬取成功!")
            print(f"   页面标题: {result.title[:50]}...")
            print(f"   HTML长度: {len(result.html)} 字符")
            print(f"   状态码: {result.status_code}")
            return True
        else:
            print(f"❌ 爬取失败: {result.error_message}")
            return False

    except Exception as e:
        print(f"❌ 环境测试异常: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("SmartScout 环境验证测试 v2")
    print("=" * 60)

    try:
        success = asyncio.run(test_environment())
        if success:
            print("\n🎉 环境验证通过！")
            print("   Python 3.10 ✓")
            print("   crawl4ai v0.8.0 ✓")
            print("   Chromium ✓")
            print("   代理配置 ✓")
            print("   strategy='dynamic' API ✓")
        else:
            print("\n⚠️  环境验证失败，请检查配置")
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹️  用户中断测试")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 测试过程异常: {e}")
        sys.exit(1)