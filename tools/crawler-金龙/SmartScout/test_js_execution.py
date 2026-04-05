#!/usr/bin/env python3
"""
⚠️⚠️⚠️ 【已废弃】Crawl4AI v0.6.3 JavaScript注入测试 ⚠️⚠️⚠️

【废弃原因】
1. 测试 v0.6.3 的 extra_js 参数，该版本已废弃
2. v0.8.x+ 使用 strategy="dynamic" 而非JavaScript注入
3. 仅作为历史参考，禁止在新版本中使用

【历史记录】
- 创建时间：2026-02-10
- 废弃时间：2026-02-10
- 废弃原因：Crawl4AI版本升级
================================================================================

测试Crawl4AI的extra_js参数是否执行JavaScript（已废弃）"""
import asyncio
import crawl4ai
from crawl4ai import AsyncWebCrawler

async def test_js_execution():
    print("测试extra_js参数是否执行JavaScript")

    # 简单的测试JavaScript：修改页面标题
    test_js = """
    console.log('JavaScript执行测试开始');
    // 修改页面标题作为标记
    document.title = 'CRAWL4AI_JS_TEST_' + new Date().getTime();
    console.log('页面标题已修改为: ' + document.title);
    return document.title;
    """

    crawler = AsyncWebCrawler(
        verbose=True,
        strategy="dynamic",
        headless=False,
        timeout=30000
    )

    # 测试URL
    test_url = "https://example.com"

    print(f"测试URL: {test_url}")
    print(f"测试JavaScript: {test_js[:100]}...")

    try:
        # 使用extra_js参数
        result = await crawler.arun(
            url=test_url,
            extra_js=test_js
        )

        print(f"\n抓取结果:")
        print(f"成功: {result.success}")
        print(f"HTML长度: {len(result.html) if result.html else 0}")

        # 检查标题是否被修改
        if result.html and 'CRAWL4AI_JS_TEST_' in result.html:
            print("✅ JavaScript成功执行：页面标题被修改")
            # 提取标题
            import re
            title_match = re.search(r'<title>(.*?)</title>', result.html)
            if title_match:
                print(f"实际标题: {title_match.group(1)}")
        else:
            print("❌ JavaScript可能未执行：页面标题未修改")

        # 打印HTML片段查看标题
        if result.html:
            print("\nHTML片段（包含标题部分）:")
            title_start = result.html.find('<title>')
            if title_start != -1:
                title_end = result.html.find('</title>', title_start)
                if title_end != -1:
                    print(result.html[title_start:title_end+8])
            else:
                print("未找到<title>标签")

    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()

    print("\n测试完成")

if __name__ == "__main__":
    asyncio.run(test_js_execution())