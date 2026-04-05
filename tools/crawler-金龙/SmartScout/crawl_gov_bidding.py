#!/usr/bin/env python3
# crawl_gov_bidding.py - 爬取中国政府招标网搜索结果

import os
import sys
import asyncio
import json
from datetime import datetime
from crawl4ai import AsyncWebCrawler, BrowserConfig
from bs4 import BeautifulSoup

print("="*60)
print("📋 中国政府招标网爬取工具")
print("="*60)

# 清除所有代理设置
for var in ['http_proxy', 'https_proxy', 'HTTP_PROXY', 'HTTPS_PROXY']:
    os.environ.pop(var, None)

# 目标URL - 中国政府招标网搜索"消防"
BASE_URL = "https://search.ccgp.gov.cn/bxsearch"
SEARCH_PARAMS = {
    "searchtype": "2",
    "page_index": "1",
    "start_time": "",
    "end_time": "",
    "timeType": "2",
    "searchparam": "",
    "searchchannel": "0",
    "dbselect": "bidx",
    "kw": "消防",
    "bidSort": "0",
    "pinMu": "0",
    "bidType": "0",
    "buyerName": "",
    "projectId": "",
    "displayZone": "",
    "zoneId": "",
    "agentName": ""
}

def build_search_url(page=1):
    """构建搜索URL"""
    params = SEARCH_PARAMS.copy()
    params["page_index"] = str(page)
    query_string = "&".join([f"{k}={v}" for k, v in params.items() if v])
    return f"{BASE_URL}?{query_string}"

def parse_search_results(html):
    """解析搜索结果页面"""
    soup = BeautifulSoup(html, 'lxml')
    results = []

    # 查找结果列表
    result_list = soup.find('ul', class_='vT-srch-result-list-bid')
    if not result_list:
        print("⚠️  未找到搜索结果列表")
        return results

    # 提取每个结果项
    for item in result_list.find_all('li'):
        try:
            # 提取标题和链接
            title_link = item.find('a')
            if not title_link:
                continue

            title = title_link.get_text(strip=True)
            url = title_link.get('href', '')

            # 提取描述（p标签）
            description_elem = item.find('p')
            description = description_elem.get_text(strip=True) if description_elem else ""

            # 提取其他信息（span标签）
            info_span = item.find('span')
            info_text = info_span.get_text(strip=True) if info_span else ""

            # 解析信息文本
            info_parts = {}
            if info_text:
                # 分割各部分信息
                parts = info_text.split('|')
                for part in parts:
                    part = part.strip()
                    if '：' in part:
                        key, value = part.split('：', 1)
                        info_parts[key.strip()] = value.strip()
                    elif ':' in part:
                        key, value = part.split(':', 1)
                        info_parts[key.strip()] = value.strip()

            # 提取时间（通常在第一部分）
            time_part = info_text.split('|')[0].strip() if '|' in info_text else info_text
            publish_time = time_part

            # 构建结果对象
            result = {
                'title': title,
                'url': url,
                'description': description,
                'publish_time': publish_time,
                'buyer': info_parts.get('采购人', ''),
                'agency': info_parts.get('代理机构', ''),
                'raw_info': info_text
            }

            results.append(result)

        except Exception as e:
            print(f"⚠️  解析结果项时出错: {e}")
            continue

    return results

async def crawl_search_page(page=1, use_stealth=False):
    """爬取搜索页面"""

    target_url = build_search_url(page)
    print(f"🌐 爬取第 {page} 页: {target_url}")

    # 配置浏览器
    if use_stealth:
        browser_config = BrowserConfig(
            browser_mode="undetected",      # 防检测模式
            enable_stealth=True,           # 隐身模式
            headless=True,                  # 无头模式
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            proxy=None                      # 禁用代理
        )
    else:
        browser_config = BrowserConfig(
            browser_mode="chromium",
            headless=True,
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            proxy=None
        )

    try:
        async with AsyncWebCrawler(config=browser_config) as crawler:
            # 执行爬取
            result = await crawler.arun(
                url=target_url,
                timeout=60000  # 60秒超时
            )

            if not result.success:
                print(f"❌ 爬取失败: {result.error_message}")
                return []

            print(f"✅ 爬取成功，HTML长度: {len(result.html)} 字符")

            # 解析结果
            search_results = parse_search_results(result.html)
            print(f"📊 解析到 {len(search_results)} 个结果")

            return search_results

    except Exception as e:
        print(f"❌ 爬取过程中出错: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return []

async def main():
    """主函数"""
    print(f"Python版本: {sys.version.split()[0]}")
    print(f"搜索关键词: '{SEARCH_PARAMS['kw']}'")

    # 测试直接请求（不使用防检测）
    print("\n1. 测试普通爬取...")
    results1 = await crawl_search_page(page=1, use_stealth=False)

    if results1:
        print(f"\n✅ 普通爬取成功，获取到 {len(results1)} 个结果")
        print("\n📋 结果示例:")
        for i, result in enumerate(results1[:3]):
            print(f"\n  {i+1}. {result['title']}")
            print(f"     链接: {result['url']}")
            print(f"     发布时间: {result['publish_time']}")
            print(f"     采购人: {result['buyer']}")
            print(f"     代理机构: {result['agency']}")

        # 保存结果
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"search_results_{timestamp}.json"

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results1, f, ensure_ascii=False, indent=2)

        print(f"\n💾 结果已保存到: {output_file}")

        # 如果需要，测试防检测模式
        print("\n2. 测试防检测模式...")
        results2 = await crawl_search_page(page=1, use_stealth=True)

        if results2:
            print(f"✅ 防检测模式成功，获取到 {len(results2)} 个结果")
        else:
            print("❌ 防检测模式失败")

    else:
        print("❌ 普通爬取失败，尝试防检测模式...")
        results2 = await crawl_search_page(page=1, use_stealth=True)

        if results2:
            print(f"✅ 防检测模式成功，获取到 {len(results2)} 个结果")

            # 保存结果
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"search_results_stealth_{timestamp}.json"

            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results2, f, ensure_ascii=False, indent=2)

            print(f"\n💾 结果已保存到: {output_file}")
        else:
            print("❌ 两种模式都失败")

    return len(results1) > 0 or len(results2) > 0

if __name__ == "__main__":
    print("🚀 开始爬取...")
    success = asyncio.run(main())

    print("\n" + "="*60)
    print(f"最终结果: {'✅ 成功' if success else '❌ 失败'}")

    if success:
        print("\n🎯 下一步:")
        print("1. 可以调整搜索关键词和参数")
        print("2. 可以添加多页爬取功能")
        print("3. 可以添加详情页爬取")
        print("4. 可以集成到SmartScout系统中")
    else:
        print("\n🔍 问题分析:")
        print("1. 网站访问限制")
        print("2. 页面结构可能已变化")
        print("3. 需要调整解析逻辑")

    print("="*60)