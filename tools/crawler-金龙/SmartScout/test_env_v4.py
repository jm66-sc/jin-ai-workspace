#!/usr/bin/env python3
"""
环境验证测试 v4
最小化参数调用
"""

import asyncio
import os
import sys

os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:8118'
os.environ['HTTP_PROXY'] = 'http://127.0.0.1:8118'

async def test_environment():
    try:
        from crawl4ai import AsyncWebCrawler

        print("✅ 导入crawl4ai成功")

        # 使用默认配置
        crawler = AsyncWebCrawler()

        print("🔄 尝试访问 example.com (仅strategy参数)...")

        # 仅传递必要参数
        result = await crawler.arun(
            url="https://example.com",
            strategy="dynamic",
            wait_for="body",
            timeout=30000,
        )

        if result.success:
            print(f"✅ 爬取成功!")
            print(f"   标题: {result.title}")
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
    print("环境测试 v4 - 最小参数")
    print("=" * 60)

    try:
        success = asyncio.run(test_environment())
        if success:
            print("\n🎉 测试通过!")
            print("   strategy='dynamic' 工作正常 ✓")
        else:
            print("\n⚠️ 测试失败")
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n💥 异常: {e}")
        sys.exit(1)