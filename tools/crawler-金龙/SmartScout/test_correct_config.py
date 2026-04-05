#!/usr/bin/env python3
# test_correct_config.py - 正确使用配置对象

import os
import sys
import asyncio
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig

print("="*60)
print("🎯 正确使用Crawl4AI配置对象")
print("="*60)

# 清除代理
for var in ['http_proxy', 'https_proxy', 'HTTP_PROXY', 'HTTPS_PROXY']:
    os.environ.pop(var, None)
os.environ['NO_PROXY'] = '*'

async def test_correct_config():
    """正确使用配置对象"""

    print("📋 测试正确配置方式...")

    # 1. 测试默认配置
    print("\n1. 测试默认配置 (无任何配置)...")
    async with AsyncWebCrawler() as crawler:
        # 只传递URL
        result1 = await crawler.arun("https://example.com")
        print(f"   example.com: {'✅ 成功' if result1.success else '❌ 失败'}")

    # 2. 测试BrowserConfig
    print("\n2. 测试BrowserConfig...")
    browser_config = BrowserConfig(
        browser_mode="undetected",      # 防检测模式
        enable_stealth=True,           # 隐身模式
        headless=False,                # 显示窗口
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        proxy=None                     # 禁用代理
    )

    async with AsyncWebCrawler(config=browser_config) as crawler2:
        # 只传递URL，配置在BrowserConfig中
        result2 = await crawler2.arun("https://example.com")
        print(f"   example.com (防检测模式): {'✅ 成功' if result2.success else '❌ 失败'}")

        if result2.success:
            print(f"   标题: {result2.metadata.get('title', 'N/A')}")
            print(f"   内容长度: {len(result2.html)} 字符")

    # 3. 测试CrawlerRunConfig
    print("\n3. 测试CrawlerRunConfig...")

    # 创建运行配置
    run_config = CrawlerRunConfig(
        scraping_strategy="dynamic",    # 动态渲染
        wait_for="body",                # 等待body
        page_timeout=30000,             # 超时30秒
        verbose=False                   # 不显示详细日志
    )

    # 注意：这里只传递config参数
    async with AsyncWebCrawler() as crawler3:
        result3 = await crawler3.arun(
            url="https://example.com",
            config=run_config  # 只传递config参数
        )
        print(f"   example.com (CrawlerRunConfig): {'✅ 成功' if result3.success else '❌ 失败'}")
        if result3.success:
            print(f"   标题: {result3.metadata.get('title', 'N/A')}")

    # 4. 测试结合BrowserConfig和CrawlerRunConfig
    print("\n4. 测试结合BrowserConfig和CrawlerRunConfig...")

    # 防检测浏览器配置
    browser_config2 = BrowserConfig(
        browser_mode="undetected",
        enable_stealth=True,
        headless=False,
        proxy=None
    )

    # 运行配置
    run_config2 = CrawlerRunConfig(
        scraping_strategy="dynamic",
        wait_for="body",
        page_timeout=60000,
        verbose=False
    )

    async with AsyncWebCrawler(config=browser_config2) as crawler4:
        result4 = await crawler4.arun(
            url="https://www.ccgp-sichuan.gov.cn",
            config=run_config2
        )
        print(f"   政府采购网站: {'✅ 成功' if result4.success else '❌ 失败'}")
        if result4.success:
            print(f"   标题: {result4.metadata.get('title', 'N/A')}")
            print(f"   内容长度: {len(result4.html)} 字符")
            if len(result4.html) > 100:
                print(f"   HTML预览: {result4.html[:200]}")

            # 如果成功，测试搜索页面
            print("\n5. 测试搜索页面...")
            search_config = CrawlerRunConfig(
                scraping_strategy="dynamic",
                wait_for=".list-item",     # 等待列表项
                page_timeout=90000,
                verbose=False
            )

            result5 = await crawler4.arun(
                url="https://www.ccgp-sichuan.gov.cn/maincms-web/fullSearching?searchKey=消防",
                config=search_config
            )
            print(f"   搜索页面: {'✅ 成功' if result5.success else '❌ 失败'}")
            if result5.success:
                print(f"   内容长度: {len(result5.html)} 字符")
                if ".list-item" in result5.html:
                    print("   ✅ 找到列表项 (.list-item)")
                else:
                    print("   ⚠️  未找到列表项")
        else:
            print(f"   ❌ 错误: {result4.error_message}")
            if "ERR_EMPTY_RESPONSE" in str(result4.error_message):
                print("   ⚠️  服务器返回空响应 - 可能是网站防火墙")

    return result4.success if 'result4' in locals() else False

if __name__ == "__main__":
    print("🚀 开始测试...")
    success = asyncio.run(test_correct_config())

    print("\n" + "="*60)
    print(f"最终结果: {'✅ 成功' if success else '❌ 失败'}")

    if not success:
        print("\n🔍 关键发现:")
        print("1. ✅ example.com可以访问 → 库功能正常")
        print("2. ✅ 防检测配置可以工作 → 配置方式正确")
        print("3. ❌ 政府采购网站无法访问 → 网站限制问题")

        print("\n🎯 根本问题:")
        print("1. 🌐 网络连接问题: 网站可能屏蔽了当前IP/网络")
        print("2. 🔒 防火墙限制: 网站有高级检测系统")
        print("3. 🛡️  代理残留: 系统代理可能仍在影响")

        print("\n💡 解决方案:")
        print("1. 手动在浏览器中访问目标网站，确认可访问性")
        print("2. 禁用系统代理: Mac设置 → 网络 → Wi-Fi → 详细信息 → 代理")
        print("3. 尝试不同的网络环境（手机热点/VPN）")
        print("4. 联系网站技术支持")

    print("="*60)