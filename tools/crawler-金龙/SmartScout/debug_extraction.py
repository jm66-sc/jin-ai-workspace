#!/usr/bin/env python3
"""
调试目标站点的列表提取问题
"""
import asyncio
import logging
from crawl4ai import AsyncWebCrawler, BrowserConfig
from bs4 import BeautifulSoup
import sys

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

TARGET_URL = "http://www.gdtzb.com/zb/search.php?kw=%E6%B6%88%E9%98%B2&page_index=1"

async def fetch_html():
    """抓取HTML"""
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

def simulate_extract_items_from_html(html):
    """模拟producer.py中的extract_items_from_html函数"""
    soup = BeautifulSoup(html, 'lxml')
    items = []

    for link in soup.find_all('a', href=True):
        href = link.get('href', '')
        if not href:
            continue

        # 过滤非公告URL
        if not ('htm' in href or 'html' in href):
            continue
        if href.startswith('javascript'):
            continue

        # 只保留公告详情页（路径包含/cggg/）
        if '/cggg/' not in href:
            continue

        # 过滤常见非公告页面
        excluded_pages = ['contact.shtml', 'about.shtml', 'help.shtml', 'index.shtml',
                         'policy.shtml', 'disclaimer.shtml', 'sitemap.shtml']
        if any(page in href for page in excluded_pages):
            continue

        # 查找可见文本（向上查找父元素）
        parent = link.parent
        visible_text = ""

        # 向上查找3层父元素，获取足够长的文本
        for _ in range(3):
            if parent:
                text = parent.get_text(strip=True, separator=' ')
                if len(text) > 50:  # 只保留足够长的文本
                    visible_text = text
                    break
                parent = parent.parent

        if visible_text and len(visible_text) > 50:
            # 规范化URL（模拟producer的normalize_url）
            if href.startswith('http://') or href.startswith('https://'):
                full_url = href
            elif href.startswith('//'):
                full_url = f"http:{href}"
            elif href.startswith('/'):
                full_url = f"http://www.ccgp.gov.cn{href}"
            else:
                full_url = f"http://www.ccgp.gov.cn/{href}"

            # 去重检查（避免重复路径）
            if '//www.ccgp.gov.cn//www.ccgp.gov.cn/' in full_url:
                full_url = full_url.replace('//www.ccgp.gov.cn//www.ccgp.gov.cn/', '//www.ccgp.gov.cn/')

            item = {
                "title": visible_text,
                "detail_url": full_url,
                "source_page": 1,
            }
            items.append(item)

    return items

def analyze_html_structure(html):
    """分析HTML结构，查找列表项"""
    soup = BeautifulSoup(html, 'lxml')
    print("=== 页面标题 ===")
    print(soup.title.string if soup.title else "无标题")

    # 查找所有链接并分类
    links = soup.find_all('a', href=True)
    print(f"\n总共找到 {len(links)} 个链接")

    # 按href特征分组
    htm_links = [l for l in links if 'htm' in l.get('href', '').lower() or 'html' in l.get('href', '').lower()]
    print(f"包含htm/html的链接: {len(htm_links)}")

    # 显示前10个htm链接
    print("\n--- 前10个htm/html链接 ---")
    for i, link in enumerate(htm_links[:10]):
        href = link.get('href', '')
        text = link.get_text(strip=True)
        parent = link.parent
        parent_text = parent.get_text(strip=True, separator=' ')[:100] if parent else ""
        print(f"{i+1}. href: {href}")
        print(f"   文本: {text}")
        print(f"   父元素文本: {parent_text[:80]}...")
        print()

    # 检查是否有明显的列表容器
    print("\n=== 查找列表容器 ===")
    for tag in ['div', 'ul', 'li', 'table', 'tbody', 'tr']:
        elements = soup.find_all(tag, limit=10)
        for elem in elements:
            child_links = elem.find_all('a', href=True)
            if len(child_links) >= 2:
                classes = elem.get('class', [])
                id_attr = elem.get('id', '')
                print(f"<{tag}> 包含 {len(child_links)} 个链接, class: {classes}, id: {id_attr}")
                # 检查这些链接是否包含htm/html
                htm_count = sum(1 for l in child_links if 'htm' in l.get('href', '').lower() or 'html' in l.get('href', '').lower())
                print(f"  其中htm/html链接: {htm_count}")
                break

    # 检查是否有JavaScript渲染的迹象
    print("\n=== JavaScript检查 ===")
    scripts = soup.find_all('script')
    print(f"script标签数量: {len(scripts)}")
    for script in scripts[:3]:
        if script.string and len(script.string) > 100:
            content = script.string.lower()
            if 'document.write' in content or 'innerhtml' in content or 'appendchild' in content:
                print("发现动态生成内容的脚本")
                break

    # 检查页面正文中是否有大量文本
    body = soup.find('body')
    if body:
        body_text = body.get_text(strip=True, separator=' ')
        print(f"正文文本长度: {len(body_text)} 字符")
        # 查找包含"消防"的文本（搜索关键词）
        if '消防' in body_text:
            print("正文包含搜索关键词'消防'")
        else:
            print("正文未找到'消防'，可能内容为空或由JS加载")

def propose_fix(html):
    """基于分析提出修复方案"""
    soup = BeautifulSoup(html, 'lxml')
    print("\n=== 修复建议 ===")

    # 查找可能的公告链接模式
    links = soup.find_all('a', href=True)
    candidate_links = []
    for link in links:
        href = link.get('href', '')
        # 排除javascript和空链接
        if href.startswith('javascript') or not href.strip():
            continue
        # 查找可能包含公告的链接（根据常见模式）
        if 'detail' in href.lower() or 'view' in href.lower() or 'show' in href.lower():
            candidate_links.append(link)
        elif 'htm' in href.lower() or 'html' in href.lower():
            candidate_links.append(link)

    print(f"候选链接（基于常见模式）: {len(candidate_links)}")

    # 检查这些链接是否有合理的父元素文本
    valid_links = []
    for link in candidate_links[:20]:
        parent = link.parent
        visible_text = ""
        for _ in range(3):
            if parent:
                text = parent.get_text(strip=True, separator=' ')
                if len(text) > 30:
                    visible_text = text
                    break
                parent = parent.parent
        if visible_text:
            valid_links.append((link, visible_text))

    print(f"有足够文本的链接: {len(valid_links)}")
    for i, (link, text) in enumerate(valid_links[:5]):
        print(f"{i+1}. 文本: {text[:80]}...")
        print(f"   URL: {link.get('href', '')}")

    # 判断根本原因
    print("\n=== 根因判断 ===")
    if len(links) == 0:
        print("A. 页面结构和当前选择器不匹配（无链接或链接结构不同）")
    elif len(candidate_links) == 0:
        print("A. 页面结构和当前选择器不匹配（链接模式不匹配）")
    else:
        # 检查是否有/cggg/过滤问题
        cggg_links = [l for l in links if '/cggg/' in l.get('href', '')]
        if len(cggg_links) == 0:
            print("A. 页面结构和当前选择器不匹配（硬编码的/cggg/路径过滤器）")
        else:
            print("需要进一步分析")

async def main():
    print("步骤1: 抓取原始HTML")
    html = await fetch_html()
    if not html:
        print("抓取失败")
        return

    # 保存HTML
    with open('debug_page.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"HTML已保存 ({len(html)} 字符)")

    print("\n步骤2: 分析页面结构")
    analyze_html_structure(html)

    print("\n步骤3: 模拟当前提取函数")
    items = simulate_extract_items_from_html(html)
    print(f"提取到 {len(items)} 个项目")
    if items:
        for i, item in enumerate(items[:5]):
            print(f"{i+1}. 标题: {item['title'][:80]}...")
            print(f"   链接: {item['detail_url']}")
    else:
        print("提取结果为0，分析原因:")

    print("\n步骤4: 提出修复建议")
    propose_fix(html)

if __name__ == "__main__":
    asyncio.run(main())