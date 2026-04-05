#!/usr/bin/env python3
# test_real_simple.py - 真实最简单的测试

import asyncio
import sys
from crawl4ai import AsyncWebCrawler

async def test_simple():
    print("🧪 最简单的测试")
    print(f"Python: {sys.version.split()[0]}")
    print(f"crawl4ai: 0.8.0")

    crawler = AsyncWebCrawler()

    # 测试1: example.com (应该100%成功)
    print("\n1. 测试 example.com...")
    try:
        result = await crawler.arun(
            url="https://example.com",
            strategy="dynamic",
            wait_for="body",
            timeout=30000,
            verbose=False
        )

        print(f"   成功: {result.success}")
        if result.success:
            print(f"   标题: {result.metadata.get('title', 'N/A')}")
            print(f"   HTML长度: {len(result.html)}")
        else:
            print(f"   错误: {result.error_message}")

    except Exception as e:
        print(f"   异常: {type(e).__name__}: {e}")

    # 测试2: 政府采购网站主页
    print("\n2. 测试政府采购网站主页...")
    try:
        result2 = await crawler.arun(
            url="https://www.ccgp-sichuan.gov.cn",
            strategy="dynamic",
            wait_for="body",
            timeout=60000,
            verbose=False
        )

        print(f"   成功: {result2.success}")
        if result2.success:
            print(f"   标题: {result2.metadata.get('title', 'N/A')}")
            print(f"   HTML长度: {len(result2.html)}")
            # 检查是否有内容
            if len(result2.html) > 100:
                print(f"   HTML预览: {result2.html[:200]}")
        else:
            print(f"   错误: {result2.error_message}")

    except Exception as e:
        print(f"   异常: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

    # 测试3: 搜索页面
    print("\n3. 测试搜索页面...")
    try:
        result3 = await crawler.arun(
            url="https://www.ccgp-sichuan.gov.cn/maincms-web/fullSearching?searchKey=消防",
            strategy="dynamic",
            wait_for=".list-item",
            timeout=90000,
            verbose=False
        )

        print(f"   成功: {result3.success}")
        if result3.success:
            print(f"   标题: {result3.metadata.get('title', 'N/A')}")
            print(f"   HTML长度: {len(result3.html)}")
            # 检查是否有列表项
            if ".list-item" in result3.html:
                print("   ✅ 检测到.list-item选择器")
            else:
                print("   ⚠️  未找到.list-item选择器")
        else:
            print(f"   错误: {result3.error_message}")

    except Exception as e:
        print(f"   异常: {type(e).__name__}: {e}")

    await crawler.close()

    print("\n" + "="*60)
    print("测试完成")

    # 总结
    if result2.success:
        print("✅ 政府采购网站可访问")
    else:
        print("❌ 政府采购网站无法访问")
        print("可能原因：")
        print("1. 网站防火墙/限制")
        print("2. 网络连接问题")
        print("3. 代理设置问题")

    return result2.success

if __name__ == "__main__":
    success = asyncio.run(test_simple())