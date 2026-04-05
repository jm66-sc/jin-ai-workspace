"""
动态样本抓取模块
用于从目标URL抓取50个样本标题，供DeepSeek规则扩充使用
"""

import asyncio
import time
import json
import logging
from datetime import datetime
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from typing import List, Dict, Any, Optional

from crawl4ai import AsyncWebCrawler, BrowserConfig
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class SampleCrawler:
    """样本抓取器：从目标URL抓取50个样本标题"""

    def __init__(self, target_url: str):
        """
        初始化样本抓取器

        Args:
            target_url: 目标URL（从实战中复制的任意格式URL）

        Raises:
            ValueError: 如果target_url为空或无效
        """
        if not target_url:
            raise ValueError("目标URL不能为空，请提供从实战中复制的URL")

        self.target_url = target_url

        # 解析基础URL和参数
        parsed = urlparse(self.target_url)
        self.base_params = {k: v[0] for k, v in parse_qs(parsed.query).items() if k != 'page_index'}
        self.base_url = parsed._replace(query=None)

        # 浏览器配置（与producer.py保持一致）
        self.config = BrowserConfig(
            browser_mode="undetected",
            headless=True
        )

        logger.info(f"样本抓取器初始化完成，目标URL: {self.target_url}")

    def build_page_url(self, page_num: int) -> str:
        """
        构建指定页数的URL

        Args:
            page_num: 页数

        Returns:
            完整的URL
        """
        params = self.base_params.copy()
        params['page_index'] = str(page_num)
        query = urlencode(params)
        return urlunparse(self.base_url._replace(query=query))

    def extract_items_from_html(self, html: str, page_num: int) -> List[Dict[str, Any]]:
        """
        从HTML中提取项目信息

        Args:
            html: HTML内容
            page_num: 当前页数

        Returns:
            项目列表（包含visible_text等字段）
        """
        soup = BeautifulSoup(html, 'lxml')
        items = []

        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            if not href:
                continue

            # 查找包含htm/html的链接，并且是公告详情页
            if ('htm' in href or 'html' in href) and not href.startswith('javascript'):
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
                    # 构建完整URL
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
                    items.append(item)

        return items

    async def crawl_page(self, crawler: AsyncWebCrawler, page_num: int) -> List[Dict[str, Any]]:
        """
        爬取单个页面

        Args:
            crawler: 爬虫实例
            page_num: 页数

        Returns:
            提取的项目列表
        """
        page_url = self.build_page_url(page_num)
        logger.info(f"开始爬取第 {page_num} 页: {page_url}")

        try:
            start_time = time.time()
            result = await crawler.arun(page_url, timeout=30000)
            elapsed = time.time() - start_time

            if not result.success:
                logger.error(f"第 {page_num} 页爬取失败: {result.error_message}")
                return []

            logger.info(f"第 {page_num} 页爬取成功 ({elapsed:.1f}秒)")

            # 提取项目
            items = self.extract_items_from_html(result.html, page_num)
            logger.info(f"第 {page_num} 页提取到 {len(items)} 个项目")

            # 去重（基于URL）
            unique_items = []
            seen_urls = set()
            for item in items:
                if item["detail_url"] not in seen_urls:
                    seen_urls.add(item["detail_url"])
                    unique_items.append(item)

            if len(unique_items) < len(items):
                logger.info(f"第 {page_num} 页去重后: {len(unique_items)} 个（去除了 {len(items) - len(unique_items)} 个重复项）")

            return unique_items

        except Exception as e:
            logger.error(f"第 {page_num} 页处理异常: {e}")
            return []

    async def crawl_50_samples(self) -> List[str]:
        """
        抓取50个样本标题

        Returns:
            标题列表（至少50个，如不足则返回所有找到的）
        """
        logger.info("=" * 80)
        logger.info("开始抓取50个样本标题")
        logger.info("=" * 80)

        crawler = AsyncWebCrawler(config=self.config)
        all_items = []
        page_num = 1
        max_pages = 10  # 防止无限循环

        try:
            while len(all_items) < 50 and page_num <= max_pages:
                items = await self.crawl_page(crawler, page_num)
                if items:
                    all_items.extend(items)
                    logger.info(f"第 {page_num} 页抓到 {len(items)} 个，累计 {len(all_items)}/50 个样本")
                else:
                    logger.warning(f"第 {page_num} 页没有提取到项目，可能已到最后一页")
                    break

                # 请求间隔（避免触发反爬）
                await asyncio.sleep(2)
                page_num += 1

            # 限制为50个样本
            final_items = all_items[:50]

            # 提取标题列表
            titles = [item["visible_text"] for item in final_items]

            logger.info("=" * 80)
            logger.info(f"样本抓取完成：获取 {len(titles)} 个标题")
            logger.info("=" * 80)

            if len(titles) < 50:
                logger.warning(f"警告：只获取到 {len(titles)} 个样本，少于目标50个")

            # 显示样本（前3个）
            if titles:
                logger.info("样本标题（前3个）:")
                for i, title in enumerate(titles[:3]):
                    logger.info(f"{i+1}. {title[:80]}...")

            return titles

        finally:
            await crawler.close()
            logger.info("爬虫实例已关闭")

    async def crawl_50_samples_with_details(self) -> List[Dict[str, Any]]:
        """
        抓取50个样本的详细信息（包含标题、URL等）

        Returns:
            样本详细信息列表
        """
        logger.info("=" * 80)
        logger.info("开始抓取50个样本详细信息")
        logger.info("=" * 80)

        crawler = AsyncWebCrawler(config=self.config)
        all_items = []
        page_num = 1
        max_pages = 10

        try:
            while len(all_items) < 50 and page_num <= max_pages:
                items = await self.crawl_page(crawler, page_num)
                if items:
                    all_items.extend(items)
                    logger.info(f"第 {page_num} 页抓到 {len(items)} 个，累计 {len(all_items)}/50 个样本")
                else:
                    logger.warning(f"第 {page_num} 页没有提取到项目，可能已到最后一页")
                    break

                # 请求间隔
                await asyncio.sleep(2)
                page_num += 1

            # 限制为50个样本
            final_items = all_items[:50]

            logger.info("=" * 80)
            logger.info(f"样本抓取完成：获取 {len(final_items)} 个样本")
            logger.info("=" * 80)

            return final_items

        finally:
            await crawler.close()
            logger.info("爬虫实例已关闭")


async def crawl_samples_from_url(target_url: str) -> List[str]:
    """
    从目标URL抓取50个样本标题（便捷函数）

    Args:
        target_url: 目标URL

    Returns:
        标题列表
    """
    crawler = SampleCrawler(target_url)
    return await crawler.crawl_50_samples()


async def crawl_samples_with_details_from_url(target_url: str) -> List[Dict[str, Any]]:
    """
    从目标URL抓取50个样本的详细信息（便捷函数）

    Args:
        target_url: 目标URL

    Returns:
        样本详细信息列表
    """
    crawler = SampleCrawler(target_url)
    return await crawler.crawl_50_samples_with_details()


# 同步包装函数（用于非异步环境）
def crawl_samples_from_url_sync(target_url: str) -> List[str]:
    """
    从目标URL抓取50个样本标题（同步版本）

    Args:
        target_url: 目标URL

    Returns:
        标题列表
    """
    return asyncio.run(crawl_samples_from_url(target_url))


def crawl_samples_with_details_from_url_sync(target_url: str) -> List[Dict[str, Any]]:
    """
    从目标URL抓取50个样本的详细信息（同步版本）

    Args:
        target_url: 目标URL

    Returns:
        样本详细信息列表
    """
    return asyncio.run(crawl_samples_with_details_from_url(target_url))


if __name__ == "__main__":
    # 测试代码
    import sys
    import logging

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )

    # 使用默认URL测试
    test_url = "https://search.ccgp.gov.cn/bxsearch?searchtype=2&page_index=1&kw=消防"

    async def test():
        print(f"测试URL: {test_url}")
        titles = await crawl_samples_from_url(test_url)
        print(f"抓取到 {len(titles)} 个标题")

        if titles:
            print("\n前5个标题:")
            for i, title in enumerate(titles[:5]):
                print(f"{i+1}. {title[:100]}...")

    asyncio.run(test())