#!/usr/bin/env python3
"""
测试修复后的extract_items_from_html函数
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

from producer import Producer
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TARGET_URL = "http://www.gdtzb.com/zb/search.php?kw=%E6%B6%88%E9%98%B2&page_index=1"

def test_fix():
    # 读取之前抓取的HTML
    with open('debug_page.html', 'r', encoding='utf-8') as f:
        html = f.read()

    print(f"HTML长度: {len(html)} 字符")

    # 创建Producer实例
    producer = Producer(TARGET_URL)

    # 测试提取
    items = producer.extract_items_from_html(html, 1)
    print(f"\n修复后提取到 {len(items)} 个项目")

    if items:
        print("\n前10个项目:")
        for i, item in enumerate(items[:10]):
            print(f"{i+1}. 标题: {item['title'][:80]}...")
            print(f"   链接: {item['detail_url']}")
            print()

        # 保存样本
        with open('extracted_items.json', 'w', encoding='utf-8') as f:
            import json
            json.dump(items[:10], f, ensure_ascii=False, indent=2)
        print("前10个项目已保存到 extracted_items.json")
    else:
        print("提取结果仍为0，需要进一步调试")

    # 与修复前比较（模拟修复前逻辑）
    print("\n=== 修复前模拟（硬编码/cggg/过滤器和域名）===")
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, 'lxml')
    old_items = []
    for link in soup.find_all('a', href=True):
        href = link.get('href', '')
        if not href:
            continue
        if not ('htm' in href or 'html' in href):
            continue
        if href.startswith('javascript'):
            continue
        if '/cggg/' not in href:  # 硬编码过滤器
            continue
        excluded_pages = ['contact.shtml', 'about.shtml', 'help.shtml', 'index.shtml',
                         'policy.shtml', 'disclaimer.shtml', 'sitemap.shtml']
        if any(page in href for page in excluded_pages):
            continue
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
            # 硬编码域名
            if href.startswith('http://') or href.startswith('https://'):
                full_url = href
            elif href.startswith('//'):
                full_url = f"http:{href}"
            elif href.startswith('/'):
                full_url = f"http://www.ccgp.gov.cn{href}"
            else:
                full_url = f"http://www.ccgp.gov.cn/{href}"
            old_items.append({"title": visible_text, "detail_url": full_url})

    print(f"修复前提取到 {len(old_items)} 个项目")

if __name__ == "__main__":
    test_fix()