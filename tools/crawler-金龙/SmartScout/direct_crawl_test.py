#!/usr/bin/env python3
# direct_crawl_test.py
import os
import asyncio
from crawl4ai import AsyncWebCrawler
# 清除所有代理设置
os.environ.pop('https_proxy', None)
os.environ.pop('http_proxy', None)
os.environ.pop('HTTPS_PROXY', None)
os.environ.pop('HTTP_PROXY', None)
async def test_direct_access():
    print("🔍 测试直连访问政府采购网站...")
    print("📡 网络模式: 直连（无代理）")

    crawler = AsyncWebCrawler()

    try:
        # 先测试主页（最简单的访问）
        print("\n1. 测试网站主页...")
        result = await crawler.arun(
            url="https://www.ccgp-sichuan.gov.cn/",
            strategy="dynamic",
            wait_for="body",
            timeout=30000,
            verbose=True
        )
        print(f"   主页访问: {'✅ 成功' if result.success else '❌ 失败'}")

        if result.success:
            print(f"   页面标题: {result.metadata.get('title', 'N/A')}")
            print(f"   内容长度: {len(result.html)} 字符")

        # 再测试搜索页面
        print("\n2. 测试搜索页面...")
        search_url = "https://www.ccgp-sichuan.gov.cn/maincms-web/fullSearching?searchKey=消防"
        print(f"   搜索URL: {search_url}")

        result2 = await crawler.arun(
            url=search_url,
            strategy="dynamic",
            wait_for=".list-item",  # 等待列表项
            timeout=60000,           # 60秒超时
            verbose=True
        )
        print(f"   搜索页面访问: {'✅ 成功' if result2.success else '❌ 失败'}")

        if result2.success:
            print(f"   搜索页面内容长度: {len(result2.html)} 字符")

            # 保存结果供检查
            with open("search_result.html", "w", encoding="utf-8") as f:
                f.write(result2.html)
            print("   💾 搜索结果已保存到: search_result.html")

            # 检查是否有列表项
            if ".list-item" in result2.html:
                print("   ✅ 检测到列表项 (.list-item)")
            else:
                print("   ⚠️  未找到列表项，可能选择器需要调整")
        else:
            print(f"   ❌ 错误信息: {result2.error_message}")

    except Exception as e:
        print(f"❌ 测试过程中发生异常: {str(e)}")
        import traceback
        traceback.print_exc()

    finally:
        await crawler.close()
if __name__ == "__main__":
    # 确认环境
    print("="*60)
    print("📋 环境配置检查:")
    print(f"Python路径: {os.path.dirname(os.__file__)}")
    print(f"代理设置: HTTPS_PROXY={os.environ.get('HTTPS_PROXY', '未设置')}")
    print(f"代理设置: HTTP_PROXY={os.environ.get('HTTP_PROXY', '未设置')}")
    print("="*60)

    asyncio.run(test_direct_access())