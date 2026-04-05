#!/usr/bin/env python3
# test_final_attempt.py - 最终尝试

from crawl4ai import AsyncWebCrawler, BrowserConfig
import asyncio
import os
import sys

# 代理设置
os.environ['https_proxy'] = 'http://127.0.0.1:8118'
os.environ['http_proxy'] = 'http://127.0.0.1:8118'

async def test_with_config(config_name, browser_config=None, url=None, wait_for="body"):
    """使用特定配置测试"""
    print(f"\n🔧 测试配置: {config_name}")
    print(f"   目标URL: {url}")

    if browser_config:
        crawler = AsyncWebCrawler(config=browser_config)
    else:
        crawler = AsyncWebCrawler()

    try:
        result = await crawler.arun(
            url=url,
            strategy="dynamic",
            wait_for=wait_for,
            timeout=120000,  # 120秒超时
        )

        success = False
        html_len = 0
        error_msg = ""

        if hasattr(result, '_results') and len(result._results) > 0:
            actual = result._results[0]
            success = actual.success
            html_len = len(actual.cleaned_html) if actual.cleaned_html else 0
            error_msg = actual.error_message if actual.error_message else ""

        print(f"   {'✅' if success else '❌'} 结果: 成功={success}, HTML长度={html_len}")
        if error_msg:
            print(f"   错误: {error_msg[:200]}...")

        return success, html_len, error_msg

    except Exception as e:
        print(f"   ❌ 异常: {type(e).__name__}: {str(e)[:200]}")
        return False, 0, str(e)
    finally:
        await crawler.close()

async def main():
    print("="*70)
    print("政府采购网站爬取 - 最终尝试")
    print("="*70)

    base_url = "https://www.ccgp-sichuan.gov.cn"
    search_url = "https://www.ccgp-sichuan.gov.cn/maincms-web/fullSearching?searchKey=消防"

    # 配置1: 默认配置
    await test_with_config("1. 默认配置", None, base_url)

    # 配置2: 完整浏览器指纹
    browser_config2 = BrowserConfig(
        headless=True,
        browser_type="chromium",
        user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        viewport={"width": 1920, "height": 1080},
        extra_http_headers={
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Referer": "https://www.google.com/",
            "DNT": "1",
            "Upgrade-Insecure-Requests": "1",
        }
    )
    await test_with_config("2. 完整浏览器指纹", browser_config2, base_url)

    # 配置3: 尝试HTTP (非HTTPS)
    http_url = "http://www.ccgp-sichuan.gov.cn"
    await test_with_config("3. HTTP协议", None, http_url)

    # 配置4: 不同的等待选择器
    await test_with_config("4. 等待div", None, base_url, wait_for="div")

    # 配置5: 尝试其他政府网站（对比测试）
    other_gov_url = "https://www.gov.cn"
    await test_with_config("5. 其他政府网站(gov.cn)", None, other_gov_url)

    # 配置6: 尝试搜索页面（原始目标）
    await test_with_config("6. 搜索页面", browser_config2, search_url)

    print("\n" + "="*70)
    print("测试完成总结")
    print("="*70)
    print("如果所有测试都失败，可能的原因:")
    print("1. 🔒 网站防火墙屏蔽了您的IP/代理IP")
    print("2. 🌐 网络连接问题（尝试禁用代理测试）")
    print("3. ⏰ 网站暂时不可用（稍后重试）")
    print("4. 🛡️  SSL/TLS握手失败（检查证书）")
    print("\n建议:")
    print("1. 临时禁用代理，测试直接连接")
    print("2. 尝试不同的网络环境（如手机热点）")
    print("3. 等待几小时后重试")
    print("4. 联系网站技术支持")

if __name__ == "__main__":
    print("🔧 Python版本:", sys.version.split()[0])
    print("📦 crawl4ai版本: 0.8.0")
    print("🖥️  浏览器: Chromium")

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️ 用户中断")
    except Exception as e:
        print(f"\n💥 主程序异常: {e}")