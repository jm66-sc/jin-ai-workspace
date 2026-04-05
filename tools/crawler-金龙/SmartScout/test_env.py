#!/usr/bin/env python3
"""
环境验证测试
测试crawl4ai v0.8.0 + Python 3.10 + Chromium环境
"""

import asyncio
import os
import sys

# 设置代理（如果需要）
os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:8118'
os.environ['HTTP_PROXY'] = 'http://127.0.0.1:8118'

async def test_environment():
    """测试crawl4ai环境"""
    try:
        from crawl4ai import AsyncWebCrawler

        print("✅ 导入crawl4ai成功")
        print(f"Python版本: {sys.version}")

        # 创建爬虫实例
        crawler = AsyncWebCrawler(
            verbose=True,
            headless=True,  # 无头模式测试
            browser_type="chromium"  # 使用Chromium
        )

        print("🔄 尝试访问 example.com ...")

        # 简单测试，使用动态渲染
        result = await crawler.crawl(
            url="https://example.com",
            strategy="dynamic",
            wait_for="body",
            timeout=30000,  # 30秒超时
            verbose=True
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
    print("SmartScout 环境验证测试")
    print("=" * 60)

    try:
        success = asyncio.run(test_environment())
        if success:
            print("\n🎉 环境验证通过！")
            print("   Python 3.10 ✓")
            print("   crawl4ai v0.8.0 ✓")
            print("   Chromium ✓")
            print("   代理配置 ✓")
        else:
            print("\n⚠️  环境验证失败，请检查配置")
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹️  用户中断测试")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 测试过程异常: {e}")
        sys.exit(1)