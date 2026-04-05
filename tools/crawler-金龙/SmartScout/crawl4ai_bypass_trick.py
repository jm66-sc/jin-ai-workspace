#!/usr/bin/env python3
# crawl4ai_bypass_trick.py

import asyncio
import os
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig

# 清除所有代理设置
for proxy_var in ['https_proxy', 'http_proxy', 'HTTPS_PROXY', 'HTTP_PROXY', 'all_proxy', 'ALL_PROXY']:
    os.environ.pop(proxy_var, None)

async def bypass_with_trick():
    """使用Crawl4ai的小技巧绕过网站限制"""

    print("🎯 使用Crawl4ai的防检测小技巧...")

    # 1. 关键配置：启用防检测浏览器
    browser_config = BrowserConfig(
        browser_mode="undetected",  # 🚀 这是关键！
        headless=False,             # 显示窗口（减少检测）
        viewport_width=1366,
        viewport_height=768,
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )

    # 2. 运行配置
    run_config = CrawlerRunConfig(
        scraping_strategy="dynamic",  # 动态渲染策略
        wait_for=".list-item",        # 等待列表项
        page_timeout=90000,           # 页面超时
        verbose=True
    )

    print(f"🔧 配置详情:")
    print(f"   - 浏览器模式: {browser_config.browser_mode}")
    print(f"   - 无头模式: {browser_config.headless}")
    print(f"   - 抓取策略: {run_config.scraping_strategy}")
    print(f"   - 等待选择器: {run_config.wait_for}")
    print(f"   - 页面超时: {run_config.page_timeout}")

    # 3. 使用配置
    async with AsyncWebCrawler(config=browser_config) as crawler:
        url = "https://www.ccgp-sichuan.gov.cn/maincms-web/fullSearching?searchKey=消防"
        print(f"\n🌐 访问: {url}")

        result = await crawler.arun(url=url, config=run_config)

        print(f"\n📊 结果:")
        print(f"   成功: {'✅ 是' if result.success else '❌ 否'}")
        print(f"   错误: {result.error_message or '无'}")

        if result.success:
            print(f"   HTML长度: {len(result.html)}")
            # 检查列表项
            if ".list-item" in result.html:
                print("   ✅ 找到列表项 (.list-item)")
                # 提取URL
                import re
                urls = re.findall(r'href="([^"]+)"', result.html)
                print(f"   找到 {len(urls)} 个链接")

                # 显示一些示例
                list_urls = [u for u in urls if "fullSearching" in u or "view" in u]
                for i, url in enumerate(list_urls[:5]):
                    print(f"     {i+1}. {url}")

        return result

if __name__ == "__main__":
    print("="*60)
    print("🔧 Crawl4ai防检测小技巧测试")
    print("="*60)

    result = asyncio.run(bypass_with_trick())

    print("\n" + "="*60)
    print("🎯 测试完成")
    print("="*60)