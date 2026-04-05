#!/usr/bin/env python3
# test_official_bypass.py - 按照Crawl4AI官方文档的防检测配置

import os
import sys
import asyncio
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig

print("="*60)
print("🎯 按照Crawl4AI官方文档的防检测配置")
print("="*60)

# 彻底清除所有代理设置
print("🧹 彻底清除所有代理环境变量...")
proxy_vars = ['http_proxy', 'https_proxy', 'HTTP_PROXY', 'HTTPS_PROXY', 'all_proxy', 'ALL_PROXY']
for var in proxy_vars:
    if var in os.environ:
        print(f"   移除 {var}={os.environ[var]}")
        os.environ.pop(var, None)

# 设置NO_PROXY为通配所有
os.environ['NO_PROXY'] = '*'
os.environ['no_proxy'] = '*'

print(f"\n📋 当前环境:")
print(f"  Python版本: {sys.version.split()[0]}")
print(f"  NO_PROXY: {os.environ.get('NO_PROXY', '未设置')}")
print(f"  http_proxy: {os.environ.get('http_proxy', '未设置')}")

async def test_official_config():
    """按照官方文档的防检测配置进行测试"""

    print("\n🔧 按照Crawl4AI官方文档配置:")
    print("  1. browser_mode='undetected' - 防检测浏览器模式")
    print("  2. enable_stealth=True - 隐身模式")
    print("  3. headless=False - 显示窗口（减少检测）")

    # 1. 按照官方文档的配置
    browser_config = BrowserConfig(
        browser_mode="undetected",      # 🚀 官方防检测浏览器模式
        enable_stealth=True,           # 🚀 官方隐身模式
        headless=False,                # 显示窗口（调试时有用）
        viewport_width=1366,
        viewport_height=768,
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        proxy=None,                    # 显式禁用代理
        ignore_https_errors=True       # 临时忽略HTTPS错误
    )

    # 2. 运行配置 - 使用官方推荐的参数名
    run_config = CrawlerRunConfig(
        scraping_strategy="dynamic",   # 动态渲染策略
        wait_for="body",               # 先等待body，更通用
        page_timeout=60000,            # 页面超时60秒
        verbose=True                   # 详细日志
    )

    print(f"\n📊 配置验证:")
    print(f"  - browser_mode: {browser_config.browser_mode}")
    print(f"  - enable_stealth: {browser_config.enable_stealth}")
    print(f"  - headless: {browser_config.headless}")
    print(f"  - proxy: {browser_config.proxy}")

    # 使用配置
    async with AsyncWebCrawler(config=browser_config) as crawler:
        # 先测试简单网站验证配置
        print("\n1. 验证配置：测试 example.com...")
        try:
            result1 = await crawler.arun(
                url="https://example.com",
                config=run_config
            )
            print(f"   ✅ 成功: {result1.success}")
            if result1.success:
                print(f"   标题: {result1.metadata.get('title', 'N/A')}")
                print(f"   内容长度: {len(result1.html)} 字符")
            else:
                print(f"   ❌ 错误: {result1.error_message}")
        except Exception as e:
            print(f"   ❌ 异常: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            return False

        # 测试政府采购网站
        target_url = "https://www.ccgp-sichuan.gov.cn"
        print(f"\n2. 测试目标网站: {target_url}")
        try:
            result2 = await crawler.arun(
                url=target_url,
                config=run_config
            )
            print(f"   ✅ 成功: {result2.success}")
            if result2.success:
                print(f"   标题: {result2.metadata.get('title', 'N/A')}")
                print(f"   内容长度: {len(result2.html)} 字符")
                if len(result2.html) > 100:
                    print(f"   HTML预览: {result2.html[:200]}")
            else:
                print(f"   ❌ 错误: {result2.error_message}")
                # 检查错误类型
                if "ERR_EMPTY_RESPONSE" in str(result2.error_message):
                    print("   ⚠️  错误类型: 服务器返回空响应")
                    print("     可能原因: 网站防火墙/IP限制")
        except Exception as e:
            print(f"   ❌ 异常: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            return False

        # 如果主页成功，测试搜索页面
        if result2.success:
            search_url = "https://www.ccgp-sichuan.gov.cn/maincms-web/fullSearching?searchKey=消防"
            print(f"\n3. 测试搜索页面: {search_url}")

            # 修改等待选择器为列表项
            search_config = CrawlerRunConfig(
                scraping_strategy="dynamic",
                wait_for=".list-item",     # 等待列表项
                page_timeout=90000,        # 90秒超时
                verbose=True
            )

            try:
                result3 = await crawler.arun(
                    url=search_url,
                    config=search_config
                )
                print(f"   ✅ 成功: {result3.success}")
                if result3.success:
                    print(f"   标题: {result3.metadata.get('title', 'N/A')}")
                    print(f"   内容长度: {len(result3.html)} 字符")
                    # 检查是否有列表项
                    if ".list-item" in result3.html:
                        print("   ✅ 找到列表项 (.list-item)")
                        # 提取URL示例
                        import re
                        urls = re.findall(r'href="([^"]+)"', result3.html)
                        print(f"   找到 {len(urls)} 个链接")
                        # 显示前几个相关链接
                        list_urls = [u for u in urls if "fullSearching" in u or "view" in u]
                        for i, url in enumerate(list_urls[:5]):
                            print(f"     {i+1}. {url}")
                    else:
                        print("   ⚠️  未找到.list-item选择器，可能需要调整")
                else:
                    print(f"   ❌ 错误: {result3.error_message}")
            except Exception as e:
                print(f"   ❌ 异常: {type(e).__name__}: {e}")

        return result2.success

if __name__ == "__main__":
    print("\n🚀 开始测试...")
    success = asyncio.run(test_official_config())

    print("\n" + "="*60)
    if success:
        print("🎉 成功！官方防检测配置有效")
        print("👉 可以开始正式的爬取工作了")
    else:
        print("⚠️  测试失败")
        print("\n🔍 问题分析:")
        print("1. 🔒 网站可能有严格的防火墙/IP限制")
        print("2. 🌐 网络连接问题（即使配置正确也无法连接）")
        print("3. 🛡️  地区性访问限制")
        print("\n🎯 建议:")
        print("1. 手动在浏览器中访问目标网站，确认可访问性")
        print("2. 尝试不同的网络环境（如手机热点）")
        print("3. 检查系统级代理设置（Mac: 系统设置 → 网络 → 代理）")
        print("4. 如果手动可访问但代码不可访问，可能是网站针对自动化工具的检测")
    print("="*60)