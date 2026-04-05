#!/usr/bin/env python3
"""
测试 producer.extract_items_from_html 在目标URL上的表现
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.producer import Producer
from crawl4ai import AsyncWebCrawler, BrowserConfig
import asyncio
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

TARGET_URL = "http://www.gdtzb.com/zb/search.php?kw=%E6%B6%88%E9%98%B2&page_index=1"

async def fetch_html():
    """使用与producer相同的配置抓取HTML"""
    config = BrowserConfig(
        browser_mode="undetected",
        headless=True
    )
    crawler = AsyncWebCrawler(config=config)
    try:
        result = await crawler.arun(TARGET_URL, timeout=30000)
        if result.success:
            return result.html
        else:
            logger.error(f"抓取失败: {result.error_message}")
            return None
    finally:
        await crawler.close()

def analyze_html(html):
    """分析HTML结构，查找可能的标题和链接"""
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, 'lxml')

    print("=== 页面标题 ===")
    print(soup.title.string if soup.title else "无标题")

    print("\n=== 所有链接 (a标签) ===")
    links = soup.find_all('a', href=True)
    print(f"共找到 {len(links)} 个链接")

    # 显示前20个链接
    for i, link in enumerate(links[:20]):
        href = link.get('href', '')
        text = link.get_text(strip=True)
        parent = link.parent
        parent_text = parent.get_text(strip=True, separator=' ')[:100] if parent else ""
        print(f"{i+1}. href: {href}")
        print(f"   文本: {text}")
        print(f"   父元素文本: {parent_text}")
        print()

    print("\n=== 可能的列表项容器 ===")
    # 查找常见的列表容器
    for tag_name in ['div', 'ul', 'li', 'table', 'tbody', 'tr']:
        elements = soup.find_all(tag_name)
        if elements:
            # 检查是否有包含多个链接的容器
            for elem in elements[:5]:
                child_links = elem.find_all('a', href=True)
                if len(child_links) >= 2:
                    print(f"容器 <{tag_name}> 包含 {len(child_links)} 个链接")
                    # 打印类名和ID
                    classes = elem.get('class', [])
                    id_attr = elem.get('id', '')
                    if classes or id_attr:
                        print(f"   类: {classes}, ID: {id_attr}")

    print("\n=== 检查是否有JavaScript渲染内容 ===")
    script_tags = soup.find_all('script')
    print(f"页面包含 {len(script_tags)} 个script标签")
    # 检查是否有明显的JS框架
    for script in script_tags[:3]:
        if script.string:
            content = script.string.lower()
            if 'react' in content or 'vue' in content or 'angular' in content:
                print("检测到前端框架")
                break

def test_extraction(html):
    """使用当前的extract_items_from_html函数测试提取"""
    # 创建一个Producer实例（需要target_url参数，但我们可以传递任意值）
    producer = Producer("http://dummy.com")

    # 直接调用提取函数
    items = producer.extract_items_from_html(html, 1)
    print(f"\n=== extract_items_from_html 结果 ===")
    print(f"提取到 {len(items)} 个项目")

    for i, item in enumerate(items[:10]):
        print(f"{i+1}. 标题: {item['title'][:80]}...")
        print(f"   链接: {item['detail_url']}")
        print()

    # 如果提取为0，分析原因
    if len(items) == 0:
        print("分析提取失败原因:")
        # 检查过滤条件
        soup = BeautifulSoup(html, 'lxml')
        links = soup.find_all('a', href=True)
        htm_links = [l for l in links if 'htm' in l.get('href', '') or 'html' in l.get('href', '')]
        print(f"   - 包含htm/html的链接: {len(htm_links)}")

        cggg_links = [l for l in htm_links if '/cggg/' in l.get('href', '')]
        print(f"   - 包含/cggg/的链接: {len(cggg_links)}")

        # 检查normalize_url的影响
        print(f"   - 规范化URL域名为: www.ccgp.gov.cn (硬编码)")

        # 检查文本长度要求
        long_text_links = []
        for link in links:
            parent = link.parent
            visible_text = ""
            for _ in range(3):
                if parent:
                    text = parent.get_text(strip=True, separator=' ')
                    if len(text) > 50:
                        visible_text = text
                        break
                    parent = parent.parent
            if visible_text:
                long_text_links.append(link)
        print(f"   - 父元素有长文本(>50字符)的链接: {len(long_text_links)}")

async def main():
    print("步骤1: 抓取原始HTML")
    html = await fetch_html()
    if not html:
        print("抓取失败")
        return

    # 保存HTML供检查
    with open('debug_page.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"HTML已保存到 debug_page.html ({len(html)} 字符)")

    print("\n步骤2: 分析页面结构")
    analyze_html(html)

    print("\n步骤3: 测试当前提取函数")
    test_extraction(html)

    print("\n步骤4: 判断根因")
    # 基于分析判断

if __name__ == "__main__":
    asyncio.run(main())