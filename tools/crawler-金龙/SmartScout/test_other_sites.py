#!/usr/bin/env python3
# 测试其他网站以确认环境

from crawl4ai import AsyncWebCrawler
import asyncio
import os

os.environ['https_proxy'] = 'http://127.0.0.1:8118'
os.environ['http_proxy'] = 'http://127.0.0.1:8118'

async def test_site(name, url):
    print(f"\n🔍 测试 {name} ({url})...")
    crawler = AsyncWebCrawler()

    try:
        result = await crawler.arun(
            url=url,
            strategy="dynamic",
            wait_for="body",
            timeout=30000,
        )

        if hasattr(result, '_results') and len(result._results) > 0:
            actual = result._results[0]
            status = "✅" if actual.success else "❌"
            print(f"   {status} 成功: {actual.success}")
            print(f"   📄 HTML长度: {len(actual.cleaned_html) if actual.cleaned_html else 0}")
            if actual.error_message:
                print(f"   ❌ 错误: {actual.error_message[:200]}")
            return actual.success
        return False

    except Exception as e:
        print(f"   ❌ 异常: {type(e).__name__}: {str(e)[:200]}")
        return False
    finally:
        await crawler.close()

async def main():
    print("="*60)
    print("其他网站可访问性测试")
    print("="*60)

    sites = [
        ("Example", "https://example.com"),
        ("百度", "https://baidu.com"),
        ("中国政府网", "https://www.gov.cn"),
        ("四川省政府", "https://www.sc.gov.cn"),
        ("测试目标网站", "https://www.ccgp-sichuan.gov.cn"),
    ]

    results = []
    for name, url in sites:
        success = await test_site(name, url)
        results.append((name, url, success))

    print("\n" + "="*60)
    print("测试结果总结")
    print("="*60)

    for name, url, success in results:
        status = "✅ 可访问" if success else "❌ 不可访问"
        print(f"{name:20} {status}")

    print("\n🔎 分析:")
    if all(success for name, url, success in results if name != "测试目标网站"):
        print("只有目标网站不可访问 → 网站特定问题")
    elif any(success for name, url, success in results):
        print("部分网站可访问 → 代理/网络配置正常，目标网站有特殊限制")
    else:
        print("所有网站都不可访问 → 代理/网络配置问题")

if __name__ == "__main__":
    asyncio.run(main())