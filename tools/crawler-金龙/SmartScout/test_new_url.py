#!/usr/bin/env python3
# test_new_url.py - 测试中国政府招标网新URL（无代理）

import os
import sys
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

print("="*60)
print("🌐 测试中国政府招标网新URL（无代理）")
print("="*60)

# 确保清除所有代理环境变量
for var in ['http_proxy', 'https_proxy', 'HTTP_PROXY', 'HTTPS_PROXY', 'PROXY_SERVER', 'all_proxy', 'ALL_PROXY']:
    os.environ.pop(var, None)

print("🧹 代理环境变量已清除")
print(f"当前环境:")
print(f"  http_proxy: {os.environ.get('http_proxy', '未设置')}")
print(f"  https_proxy: {os.environ.get('https_proxy', '未设置')}")

# 目标URL - 中国政府招标网
target_url = "https://search.ccgp.gov.cn/bxsearch?searchtype=2&page_index=1&start_time=&end_time=&timeType=2&searchparam=&searchchannel=0&dbselect=bidx&kw=消防+&bidSort=0&pinMu=0&bidType=0&buyerName=&projectId=&displayZone=&zoneId=&agentName="

print(f"\n🎯 目标URL: {target_url}")
print(f"搜索关键词: '消防'")

# 创建带重试机制的Session
def create_session():
    """创建带重试机制的requests Session"""
    session = requests.Session()

    # 重试配置
    retry_strategy = Retry(
        total=3,  # 最大重试次数
        backoff_factor=0.5,  # 重试间隔
        status_forcelist=[429, 500, 502, 503, 504],  # 需要重试的状态码
        allowed_methods=["HEAD", "GET", "OPTIONS"]
    )

    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    return session

def test_direct_access():
    """测试直接访问"""
    print("\n1. 测试直接HTTP请求...")

    try:
        session = create_session()

        # 设置请求头
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }

        print("   🔄 发送请求...")
        response = session.get(
            target_url,
            headers=headers,
            timeout=30,  # 30秒超时
            verify=True,  # 验证SSL证书
            proxies={}    # 明确指定空代理
        )

        print(f"   ✅ 请求成功!")
        print(f"   状态码: {response.status_code}")
        print(f"   内容类型: {response.headers.get('Content-Type', 'N/A')}")
        print(f"   内容长度: {len(response.text)} 字符")
        print(f"   服务器: {response.headers.get('Server', 'N/A')}")

        # 检查响应内容
        if response.status_code == 200:
            content = response.text
            print(f"\n   📄 响应内容预览:")
            print(f"   {content[:500]}")

            # 检查是否包含关键词
            if "消防" in content:
                print("   ✅ 页面中包含'消防'关键词")
            else:
                print("   ⚠️  页面中未找到'消防'关键词")

            # 检查是否有结果列表
            if "result-item" in content or "vT-srch-result" in content or "search-result" in content:
                print("   ✅ 检测到搜索结果列表")

                # 粗略统计结果数量
                import re
                # 尝试查找公告链接
                announcement_links = re.findall(r'href="[^"]*view[^"]*"', content)
                if announcement_links:
                    print(f"   找到 {len(announcement_links)} 个公告链接")
                    for i, link in enumerate(announcement_links[:3]):
                        print(f"     {i+1}. {link}")
            else:
                print("   ⚠️  未检测到搜索结果列表结构")

            # 保存结果供检查
            with open("search_result_direct.html", "w", encoding="utf-8") as f:
                f.write(content)
            print("   💾 结果已保存到: search_result_direct.html")

        return response.status_code == 200

    except requests.exceptions.ProxyError as e:
        print(f"   ❌ 代理错误: {e}")
        print("   提示: 系统可能有残留的代理配置")
    except requests.exceptions.ConnectTimeout as e:
        print(f"   ❌ 连接超时: {e}")
    except requests.exceptions.ConnectionError as e:
        print(f"   ❌ 连接错误: {e}")
    except requests.exceptions.SSLError as e:
        print(f"   ❌ SSL错误: {e}")
    except Exception as e:
        print(f"   ❌ 请求失败: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

    return False

def test_with_crawl4ai():
    """使用Crawl4AI测试新URL"""
    print("\n2. 使用Crawl4AI测试...")

    try:
        from crawl4ai import AsyncWebCrawler, BrowserConfig
        import asyncio

        # 简单配置，不使用代理
        browser_config = BrowserConfig(
            browser_mode="chromium",
            headless=True,
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            proxy=None  # 禁用代理
        )

        async def crawl():
            async with AsyncWebCrawler(config=browser_config) as crawler:
                result = await crawler.arun(target_url)
                return result

        print("   🔄 启动Crawl4AI...")
        result = asyncio.run(crawl())

        print(f"   ✅ Crawl4AI结果: {'成功' if result.success else '失败'}")
        if result.success:
            print(f"   标题: {result.metadata.get('title', 'N/A')}")
            print(f"   内容长度: {len(result.html)} 字符")

            # 保存结果
            with open("search_result_crawl4ai.html", "w", encoding="utf-8") as f:
                f.write(result.html)
            print("   💾 结果已保存到: search_result_crawl4ai.html")

            return True
        else:
            print(f"   ❌ 错误: {result.error_message}")

    except ImportError as e:
        print(f"   ⚠️  Crawl4AI不可用: {e}")
    except Exception as e:
        print(f"   ❌ Crawl4AI测试失败: {type(e).__name__}: {e}")

    return False

if __name__ == "__main__":
    print(f"Python版本: {sys.version.split()[0]}")

    # 测试直接访问
    direct_success = test_direct_access()

    print("\n" + "="*60)
    print("📊 测试完成总结")
    print("="*60)

    if direct_success:
        print("🎉 成功！中国政府招标网可访问")
        print("👉 可以使用这个URL进行爬取工作")
    else:
        print("⚠️  访问失败")
        print("\n🔍 可能原因:")
        print("1. 网站访问限制（可能需要登录或验证）")
        print("2. 网络连接问题")
        print("3. 网站临时不可用")
        print("4. 请求头可能需要调整")

        # 测试Crawl4AI（备用）
        print("\n🔄 尝试使用Crawl4AI...")
        crawl4ai_success = test_with_crawl4ai()

        if crawl4ai_success:
            print("✅ Crawl4AI可以访问该网站")
        else:
            print("❌ 两种方法都无法访问")

    print("="*60)