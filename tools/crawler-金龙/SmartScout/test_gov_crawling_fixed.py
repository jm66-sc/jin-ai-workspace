#!/usr/bin/env python3
# test_gov_crawling_fixed.py

from crawl4ai import AsyncWebCrawler, BrowserConfig
import asyncio
import os
import sys

# 代理设置
os.environ['https_proxy'] = 'http://127.0.0.1:8118'
os.environ['http_proxy'] = 'http://127.0.0.1:8118'

async def test_gov_procurement():
    """测试政府采购网站爬取 - 修正版"""
    print("🚀 开始测试政府采购网站爬取...")
    print(f"目标URL: https://www.ccgp-sichuan.gov.cn/maincms-web/fullSearching?searchKey=消防")

    # 配置浏览器（添加更多选项）
    browser_config = BrowserConfig(
        headless=True,
        browser_type="chromium",
        user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        viewport={"width": 1920, "height": 1080},
        stealth_mode=True,  # 启用隐身模式
        ignore_https_errors=False,  # 不忽略HTTPS错误
    )

    crawler = AsyncWebCrawler(config=browser_config)

    try:
        print("🔄 执行爬取...")
        # 执行爬取 - 不传递verbose参数
        result = await crawler.arun(
            url="https://www.ccgp-sichuan.gov.cn/maincms-web/fullSearching?searchKey=消防",
            strategy="dynamic",      # 动态渲染模式
            wait_for="body",         # 先等待body，如果.list-item不存在
            timeout=90000,           # 90秒超时（网站可能较慢）
            wait_until="domcontentloaded",
        )

        # 输出结果
        print("\n" + "="*60)
        print("📊 爬取结果总结:")

        # 检查结果结构
        if hasattr(result, '_results') and len(result._results) > 0:
            actual_result = result._results[0]
            print(f"✅ 成功: {actual_result.success}")
            print(f"📄 HTML长度: {len(actual_result.cleaned_html) if actual_result.cleaned_html else 0} 字符")
            print(f"❌ 错误信息: {actual_result.error_message if actual_result.error_message else '无'}")

            if actual_result.success and actual_result.cleaned_html:
                # 提取关键信息
                html = actual_result.cleaned_html
                print(f"\n🔍 HTML预览（前500字符）:")
                print(html[:500])

                # 检查是否有列表项
                if ".list-item" in html:
                    print("✅ 检测到列表项 (.list-item)")
                else:
                    print("⚠️  未找到列表项 (.list-item)")

                # 检查是否包含"消防"
                if "消防" in html:
                    print("✅ 页面中包含'消防'关键词")
                else:
                    print("⚠️  页面中未找到'消防'关键词")

                # 保存HTML供检查
                with open("test_result_fixed.html", "w", encoding="utf-8") as f:
                    f.write(html)
                print("💾 HTML已保存到: test_result_fixed.html")
        else:
            print(f"❌ 结果结构异常")
            print(f"   result类型: {type(result)}")
            print(f"   result属性: {[a for a in dir(result) if not a.startswith('_')]}")

    except Exception as e:
        print(f"❌ 爬取过程中发生异常: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()

    finally:
        await crawler.close()

if __name__ == "__main__":
    print("🔧 环境检查...")
    print(f"Python版本: {sys.version}")
    print(f"工作目录: {os.getcwd()}")

    # 运行测试
    asyncio.run(test_gov_procurement())