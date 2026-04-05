"""
SmartScout 阶段三：生产者流水线
抓取中国政府招标网10页数据，生成任务队列
"""

import asyncio
import json
import logging
import time
import os
from datetime import datetime
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from typing import List, Dict, Any

from crawl4ai import AsyncWebCrawler, BrowserConfig
from bs4 import BeautifulSoup

# 导入配置
from config_loader import get_default_page_limit, get_queue_file_path

logger = logging.getLogger(__name__)


class Producer:
    """生产者：抓取列表页并生成任务队列"""

    def __init__(self, target_url: str, max_pages: int = None):
        """
        初始化生产者

        Args:
            target_url: 目标URL（必须提供，从实战中复制的任意格式URL）
            max_pages: 最大抓取页数，如果为None则使用配置文件默认值

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

        # 提取协议和域名用于URL规范化
        self.scheme = parsed.scheme if parsed.scheme else 'http'
        self.netloc = parsed.netloc if parsed.netloc else parsed.hostname if parsed.hostname else 'www.ccgp.gov.cn'

        # 使用成功配置
        self.config = BrowserConfig(
            browser_mode="undetected",  # 防检测核心
            headless=True               # 无头模式
        )

        # 获取配置
        self.max_pages = max_pages if max_pages is not None else get_default_page_limit()  # 优先使用传入参数
        self.queue_file = get_queue_file_path()

        # 确保队列文件目录存在
        os.makedirs(os.path.dirname(os.path.abspath(self.queue_file)), exist_ok=True)

        logger.info(f"生产者初始化完成，目标URL: {self.target_url}")
        logger.info(f"最大翻页数: {self.max_pages}")
        logger.info(f"任务队列文件: {self.queue_file}")

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

    def normalize_url(self, href: str) -> str:
        """
        规范化URL，处理协议相对URL和绝对路径

        Args:
            href: 原始URL

        Returns:
            规范化后的完整URL
        """
        if href.startswith('http://') or href.startswith('https://'):
            return href
        elif href.startswith('//'):
            # 协议相对URL，使用当前页面的协议
            return f"{self.scheme}:{href}"
        elif href.startswith('/'):
            return f"{self.scheme}://{self.netloc}{href}"
        else:
            return f"{self.scheme}://{self.netloc}/{href}"

    def extract_items_from_html(self, html: str, page_num: int) -> List[Dict[str, Any]]:
        """
        从HTML中提取项目信息

        Args:
            html: HTML内容
            page_num: 当前页数

        Returns:
            项目列表
        """
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

            # 只保留公告详情页（路径包含/cggg/），仅对ccgp.gov.cn生效
            if 'ccgp.gov.cn' in self.netloc and '/cggg/' not in href:
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
                # 规范化URL
                full_url = self.normalize_url(href)

                # 去重检查（避免重复路径）
                duplicate_pattern = f'//{self.netloc}//{self.netloc}/'
                if duplicate_pattern in full_url:
                    full_url = full_url.replace(duplicate_pattern, f'//{self.netloc}/')

                item = {
                    "title": visible_text,
                    "detail_url": full_url,
                    "source_page": page_num,
                    "crawl_time": datetime.now().isoformat()
                }
                items.append(item)

        return items

    def save_to_queue(self, items: List[Dict[str, Any]]):
        """
        将项目保存到任务队列文件

        Args:
            items: 项目列表
        """
        if not items:
            logger.warning("没有项目需要保存到队列")
            return

        try:
            # 追加模式写入JSONL格式
            with open(self.queue_file, 'a', encoding='utf-8') as f:
                for item in items:
                    # 添加任务状态和创建时间
                    task = {
                        **item,
                        "task_id": f"task_{int(time.time() * 1000)}_{hash(item['detail_url']) % 10000:04d}",
                        "status": "pending",
                        "created_at": datetime.now().isoformat(),
                        "processed_at": None,
                        "error": None
                    }
                    f.write(json.dumps(task, ensure_ascii=False) + '\n')

            logger.info(f"保存 {len(items)} 个任务到队列文件: {self.queue_file}")

        except Exception as e:
            logger.error(f"保存到队列文件失败: {e}")
            raise

    def clear_queue(self):
        """清空任务队列文件"""
        try:
            if os.path.exists(self.queue_file):
                os.remove(self.queue_file)
                logger.info(f"已清空队列文件: {self.queue_file}")
        except Exception as e:
            logger.error(f"清空队列文件失败: {e}")

    def get_queue_stats(self) -> Dict[str, Any]:
        """
        获取队列统计信息

        Returns:
            统计信息字典
        """
        if not os.path.exists(self.queue_file):
            return {"total_tasks": 0, "pending_tasks": 0}

        try:
            with open(self.queue_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            tasks = []
            for line in lines:
                try:
                    task = json.loads(line.strip())
                    tasks.append(task)
                except json.JSONDecodeError:
                    continue

            pending = sum(1 for task in tasks if task.get("status") == "pending")
            processed = sum(1 for task in tasks if task.get("status") == "processed")
            failed = sum(1 for task in tasks if task.get("status") == "failed")

            return {
                "total_tasks": len(tasks),
                "pending_tasks": pending,
                "processed_tasks": processed,
                "failed_tasks": failed,
                "queue_file": self.queue_file
            }

        except Exception as e:
            logger.error(f"获取队列统计信息失败: {e}")
            return {"error": str(e)}

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

    async def run(self, clear_existing: bool = True):
        """
        运行生产者流水线

        Args:
            clear_existing: 是否清空现有队列
        """
        logger.info("=" * 80)
        logger.info("生产者流水线开始运行")
        logger.info("=" * 80)

        # 清空现有队列（如果需要）
        if clear_existing:
            self.clear_queue()

        # 创建爬虫实例
        crawler = AsyncWebCrawler(config=self.config)
        all_items = []

        try:
            # 依次爬取每一页
            for page_num in range(1, self.max_pages + 1):
                items = await self.crawl_page(crawler, page_num)
                if items:
                    # 保存到队列文件
                    self.save_to_queue(items)
                    all_items.extend(items)

                    # 详细页面统计
                    total_items = len(all_items)
                    progress_percent = int(page_num / self.max_pages * 100)
                    logger.info(f"[生产] 第{page_num}页: ✓ 成功 | 提取:{len(items)}项 | 累计:{total_items}项 | 进度:{progress_percent}%")
                else:
                    logger.warning(f"[生产] 第{page_num}页: ⚠️  无项目 | 可能已到最后一页 | 累计:{len(all_items)}项")
                    break

                # 请求间隔（避免触发反爬）
                await asyncio.sleep(2)

            # 显示统计信息
            stats = self.get_queue_stats()
            logger.info("=" * 80)
            logger.info("🏭 生产者流水线完成")
            logger.info("=" * 80)

            # 抓取统计
            logger.info("📊 抓取统计")
            logger.info(f"  • 总计爬取页数: {min(page_num, self.max_pages)}/{self.max_pages}")
            logger.info(f"  • 总计提取项目: {len(all_items)}")
            if len(all_items) > 0:
                avg_items_per_page = len(all_items) / min(page_num, self.max_pages)
                logger.info(f"  • 平均每页项目: {avg_items_per_page:.1f}")

            # 队列统计
            logger.info("\n📋 任务队列统计")
            if "error" in stats:
                logger.warning(f"  • 错误: {stats['error']}")
            else:
                logger.info(f"  • 总任务数: {stats.get('total_tasks', 0)}")
                logger.info(f"  • 待处理: {stats.get('pending_tasks', 0)}")
                logger.info(f"  • 已处理: {stats.get('processed_tasks', 0)}")
                logger.info(f"  • 失败: {stats.get('failed_tasks', 0)}")
                logger.info(f"  • 队列文件: {stats.get('queue_file', 'N/A')}")

            # 显示样本
            if all_items:
                logger.info("\n样本任务（前3个）:")
                for i, item in enumerate(all_items[:3]):
                    logger.info(f"\n{i+1}. URL: {item['detail_url']}")
                    logger.info(f"   标题: {item['title'][:80]}...")
                    logger.info(f"   来源页: {item['source_page']}")

        finally:
            await crawler.close()
            logger.info("爬虫实例已关闭")

        return all_items


async def main():
    """主函数：生产者演示"""
    import sys
    import logging
    import argparse

    # 解析命令行参数
    parser = argparse.ArgumentParser(description='运行SmartScout生产者流水线')
    parser.add_argument('--url', type=str, required=True, help='目标URL（从实战中复制的任意格式URL）')
    args = parser.parse_args()

    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )

    logger.info("=" * 80)
    logger.info("SmartScout Phase 2: 生产者流水线")
    logger.info("=" * 80)

    try:
        # 创建生产者实例
        producer = Producer(args.url)

        # 运行生产者
        items = await producer.run(clear_existing=True)

        if items:
            logger.info(f"\n✅ 生产者流水线成功完成，生成 {len(items)} 个任务")
            logger.info(f"任务队列文件: {producer.queue_file}")
        else:
            logger.warning("⚠️ 生产者流水线未生成任何任务")

    except Exception as e:
        logger.error(f"❌ 生产者流水线失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())