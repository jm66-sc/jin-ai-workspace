#!/usr/bin/env python3
# test_bypass_proxy.py - 绕过系统代理

import os
import sys
import asyncio
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig

print("="*60)
print("🛡️  绕过系统代理测试")
print("="*60)

# 彻底清除所有代理相关环境变量
print("🧹 清除代理环境变量...")
for var in ['http_proxy', 'https_proxy', 'HTTP_PROXY', 'HTTPS_PROXY', 'all_proxy', 'ALL_PROXY']:
    os.environ.pop(var, None)

# 设置NO_PROXY环境变量（通配所有）
os.environ['NO_PROXY'] = '*'
os.environ['no_proxy'] = '*'

print(f"当前环境:")
print(f"  NO_PROXY: {os.environ.get('NO_PROXY', '未设置')}")
print(f"  Python: {sys.version.split()[0]}")

async def test_without_proxy():
    """显式绕过所有代理"""

    # 配置浏览器 - 显式禁用代理
    browser_config = BrowserConfig(
        browser_mode="chromium",  # 使用标准模式
        headless=True,            # 无头模式
        proxy=None,               # 🚀 关键：显式禁用代理
        viewport_width=1366,
        viewport_height=768,
        user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        ignore_https_errors=True,  # 忽略HTTPS错误（临时测试）
    )

    # 运行配置
    run_config = CrawlerRunConfig(
        scraping_strategy="dynamic",
        wait_for="body",          # 先等待body，更通用
        page_timeout=60000,
        verbose=True
    )

    print(f"\n🔧 浏览器配置:")
    print(f"  - 代理设置: {browser_config.proxy}")
    print(f"  - 忽略HTTPS错误: {browser_config.ignore_https_errors}")
    print(f"  - 无头模式: {browser_config.headless}")

    print(f"\n🔧 运行配置:")
    print(f"  - 抓取策略: {run_config.scraping_strategy}")
    print(f"  - 等待选择器: {run_config.wait_for}")

    # 使用配置
    async with AsyncWebCrawler(config=browser_config) as crawler:
        # 先测试简单网站
        print("\n1. 测试 example.com...")
        try:
            result1 = await crawler.arun(url="https://example.com", config=run_config)
            print(f"   ✅ 成功: {result1.success}")
            print(f"   标题: {result1.metadata.get('title', 'N/A')}")
        except Exception as e:
            print(f"   ❌ 失败: {e}")

        # 测试目标网站
        target_url = "https://www.ccgp-sichuan.gov.cn"
        print(f"\n2. 测试目标网站: {target_url}")
        try:
            result2 = await crawler.arun(url=target_url, config=run_config)
            print(f"   ✅ 成功: {result2.success}")
            if result2.success:
                print(f"   标题: {result2.metadata.get('title', 'N/A')}")
                print(f"   内容长度: {len(result2.html)} 字符")
                print(f"   HTML预览: {result2.html[:200]}")
            else:
                print(f"   ❌ 错误: {result2.error_message}")
        except Exception as e:
            print(f"   ❌ 异常: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()

        return result2.success if 'result2' in locals() else False

if __name__ == "__main__":
    success = asyncio.run(test_without_proxy())

    print("\n" + "="*60)
    if success:
        print("🎉 成功！系统代理已被绕过")
        print("👉 现在可以尝试搜索页面了")
    else:
        print("⚠️  仍然失败")
        print("\n🔍 下一步建议:")
        print("1. 在系统设置中禁用代理:")
        print("   Mac: 系统设置 → 网络 → Wi-Fi → 详细信息 → 代理 → 取消勾选所有代理")
        print("2. 或者确保代理服务正在运行:")
        print("   ➤ 检查端口8118: `lsof -i :8118`")
        print("   ➤ 启动代理服务（如果有）")
        print("3. 尝试不同的网络环境（如手机热点）")
    print("="*60)