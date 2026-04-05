#!/usr/bin/env python3
# 测试国内网站可访问性

import asyncio
import os
from crawl4ai import AsyncWebCrawler

# 确保无代理
for key in ['https_proxy', 'http_proxy', 'HTTPS_PROXY', 'HTTP_PROXY']:
    os.environ.pop(key, None)

async def test_site(crawler, name, url, selector="body"):
    print(f"\n🔍 测试 {name} ({url})...")
    try:
        result = await crawler.arun(
            url=url,
            strategy="dynamic",
            wait_for=selector,
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

async def main():
    print("="*60)
    print("国内网站直连测试")
    print("="*60)

    crawler = AsyncWebCrawler()

    sites = [
        ("百度", "https://baidu.com", "body"),
        ("中国政府网", "https://www.gov.cn", "body"),
        ("四川省政府", "https://www.sc.gov.cn", "body"),
        ("测试目标网站", "https://www.ccgp-sichuan.gov.cn", "body"),
        ("测试目标搜索", "https://www.ccgp-sichuan.gov.cn/maincms-web/fullSearching?searchKey=消防", ".list-item"),
    ]

    results = []
    for name, url, selector in sites:
        success = await test_site(crawler, name, url, selector)
        results.append((name, url, success))

    print("\n" + "="*60)
    print("测试结果总结")
    print("="*60)

    for name, url, success in results:
        status = "✅ 可访问" if success else "❌ 不可访问"
        print(f"{name:20} {status}")

    # 分析
    print("\n🔎 问题分析:")
    domestic_sites = [r for r in results if "目标" not in r[0]]
    target_sites = [r for r in results if "目标" in r[0]]

    domestic_success = all(success for _, _, success in domestic_sites)
    target_success = any(success for _, _, success in target_sites)

    if domestic_success and not target_success:
        print("✅ 环境正常: 其他国内网站均可访问")
        print("❌ 问题: 仅目标网站不可访问")
        print("\n可能原因:")
        print("1. 🔒 网站防火墙/WAF阻止了您的IP")
        print("2. 🛡️  网站有反爬虫机制，识别了Playwright指纹")
        print("3. ⏰ 网站暂时宕机或维护")
        print("4. 🌐 区域网络限制（如仅限四川IP访问）")
    elif not domestic_success:
        print("❌ 环境问题: 所有国内网站都不可访问")
        print("   检查网络连接、DNS设置")
    else:
        print("⚠️  混合结果，需要进一步分析")

    await crawler.close()

if __name__ == "__main__":
    asyncio.run(main())