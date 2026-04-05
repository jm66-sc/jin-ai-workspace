#!/usr/bin/env python3
# test_no_proxy.py - 无代理测试

import os
import sys
import asyncio
from crawl4ai import AsyncWebCrawler

# 清除所有代理设置
print("🧹 清除所有代理设置...")
for proxy_var in ['https_proxy', 'http_proxy', 'HTTPS_PROXY', 'HTTP_PROXY', 'all_proxy', 'ALL_PROXY']:
    if proxy_var in os.environ:
        print(f"   移除 {proxy_var}={os.environ[proxy_var]}")
        os.environ.pop(proxy_var, None)
    else:
        print(f"   {proxy_var}: 未设置")

print(f"\n📡 当前代理设置:")
print(f"   https_proxy: {os.environ.get('https_proxy', '未设置')}")
print(f"   http_proxy: {os.environ.get('http_proxy', '未设置')}")

async def test_without_proxy():
    print("\n🧪 开始无代理测试")
    print(f"Python: {sys.version.split()[0]}")
    print(f"crawl4ai: 0.8.0")

    crawler = AsyncWebCrawler()

    # 测试1: example.com (基准测试)
    print("\n1. 测试 example.com...")
    try:
        result = await crawler.arun(
            url="https://example.com",
            strategy="dynamic",
            wait_for="body",
            timeout=30000,
        )
        print(f"   成功: {result.success}")
        if result.success:
            print(f"   标题: {result.metadata.get('title', 'N/A')}")
            print(f"   内容长度: {len(result.html)} 字符")
        else:
            print(f"   错误: {result.error_message}")
    except Exception as e:
        print(f"   异常: {type(e).__name__}: {e}")

    # 测试2: 政府采购网站
    print("\n2. 测试政府采购网站主页...")
    try:
        result2 = await crawler.arun(
            url="https://www.ccgp-sichuan.gov.cn",
            strategy="dynamic",
            wait_for="body",
            timeout=60000,
        )
        print(f"   成功: {result2.success}")
        if result2.success:
            print(f"   标题: {result2.metadata.get('title', 'N/A')}")
            print(f"   内容长度: {len(result2.html)} 字符")
            print(f"   HTML预览: {result2.html[:200]}")
        else:
            print(f"   错误: {result2.error_message}")
    except Exception as e:
        print(f"   异常: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

    # 测试3: 使用简单HTTP请求测试网络连通性
    print("\n3. 测试网络连通性...")
    try:
        # 安装requests如果不存在
        try:
            import requests
        except ImportError:
            import subprocess
            subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
            import requests

        print("   🔄 尝试直接HTTP请求...")
        response = requests.get("https://www.ccgp-sichuan.gov.cn", timeout=10)
        print(f"   ✅ HTTP状态码: {response.status_code}")
        print(f"   响应长度: {len(response.text)} 字符")
        print(f"   服务器: {response.headers.get('Server', 'N/A')}")
    except Exception as e:
        print(f"   ❌ HTTP请求失败: {type(e).__name__}: {e}")

    await crawler.close()

    print("\n" + "="*60)
    print("测试完成总结:")
    if 'result2' in locals() and result2.success:
        print("✅ 政府采购网站可访问（无代理）")
    else:
        print("❌ 政府采购网站无法访问")
        print("\n可能原因:")
        print("1. 🔒 网站防火墙/IP限制")
        print("2. 🌐 网络连接问题（DNS、路由等）")
        print("3. ⏰ 网站暂时不可用")
        print("4. 🛡️  地区性访问限制")

    return result2.success if 'result2' in locals() else False

if __name__ == "__main__":
    success = asyncio.run(test_without_proxy())