import asyncio
import time
import json
from datetime import datetime
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from crawl4ai import AsyncWebCrawler, BrowserConfig

# 目标URL（手工输入）
TARGET_URL = "https://search.ccgp.gov.cn/bxsearch?searchtype=2&page_index=1&kw=消防"

async def crawl_simple_list():
    """最简单的爬取：可见文本 + URL"""
    print("🚀 开始简单爬取")
    print(f"🎯 目标URL: {TARGET_URL}")
    print("=" * 50)

    # 解析基础URL和参数
    parsed = urlparse(TARGET_URL)
    params = parse_qs(parsed.query)
    # 提取基础参数
    base_params = {k: v[0] for k, v in params.items() if k != 'page_index'}

    config = BrowserConfig(
        browser_mode="undetected",
        enable_stealth=True,
        headless=True
    )

    crawler = AsyncWebCrawler(config=config)
    all_items = []
    page_num = 1
    max_pages = 10  # 防止无限循环

    try:
        while len(all_items) < 50 and page_num <= max_pages:
            # 构建当前页URL
            current_params = base_params.copy()
            current_params['page_index'] = str(page_num)
            current_query = urlencode(current_params)
            current_url = urlunparse(parsed._replace(query=current_query))

            print(f"\n📄 第 {page_num} 页: {current_url}")

            start = time.time()
            result = await crawler.arun(current_url, timeout=30000)
            elapsed = time.time() - start

            if not result.success:
                print(f"❌ 爬取失败: {result.error_message}")
                break

            print(f"✅ 爬取成功 ({elapsed:.1f}秒)")

            from bs4 import BeautifulSoup
            soup = BeautifulSoup(result.html, 'lxml')

            found_items = []

            for link in soup.find_all('a', href=True):
                href = link.get('href', '')
                if not href:
                    continue

                if ('htm' in href or 'html' in href) and not href.startswith('javascript'):
                    parent = link.parent
                    visible_text = ""

                    for _ in range(3):
                        if parent:
                            text = parent.get_text(strip=True, separator=' ')
                            if len(text) > 50:
                                visible_text = text
                                break
                            parent = parent.parent

                    if visible_text and len(visible_text) > 50:
                        full_url = href
                        if not href.startswith('http'):
                            if href.startswith('/'):
                                full_url = f"http://www.ccgp.gov.cn{href}"
                            else:
                                full_url = f"http://www.ccgp.gov.cn/{href}"

                        item = {
                            "visible_text": visible_text,
                            "detail_url": full_url,
                            "source_page": page_num,
                            "crawl_time": datetime.now().isoformat()
                        }
                        found_items.append(item)

            print(f"🔍 找到 {len(found_items)} 个可能项目")

            unique_items = []
            seen_urls = set()
            for item in found_items:
                if item["detail_url"] not in seen_urls:
                    seen_urls.add(item["detail_url"])
                    unique_items.append(item)

            print(f"✅ 去重后: {len(unique_items)} 个")

            all_items.extend(unique_items)
            print(f"📊 累计: {len(all_items)}/50 条")

            if not found_items:
                print("⚠️  本页未找到项目，停止翻页")
                break

            page_num += 1
            await asyncio.sleep(2)

        final_items = all_items[:50]

        print("\n" + "=" * 50)
        print(f"🎉 完成！获取 {len(final_items)} 条数据")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"simple_bids_50_{timestamp}.json"

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(final_items, f, ensure_ascii=False, indent=2)

        print(f"💾 保存到: {filename}")

        print("\n📋 样本（前3条）:")
        for i, item in enumerate(final_items[:3]):
            print(f"\n{i+1}. URL: {item['detail_url']}")
            print(f"   可见文本: {item['visible_text'][:100]}...")
            print(f"   长度: {len(item['visible_text'])} 字符")

        return final_items

    finally:
        await crawler.close()
        print("\n🔧 爬虫关闭")

if __name__ == "__main__":
    asyncio.run(crawl_simple_list())
