"""
SmartScout 阶段四：消费者流水线
处理任务队列，过滤并提取详情页信息
"""

import asyncio
import json
import logging
import os
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import re

from crawl4ai import AsyncWebCrawler, BrowserConfig

# 导入项目模块
from sqlite_manager import SQLiteManager
from deepseek_extractor import DeepSeekExtractor
from config_loader import get_queue_file_path, get_database_path

logger = logging.getLogger(__name__)


class RuleFilter:
    """规则过滤器：基于黑白名单过滤标题"""

    def __init__(self, white_list: List[str], black_list: List[str]):
        """
        初始化规则过滤器

        Args:
            white_list: 白名单关键词列表
            black_list: 黑名单关键词列表
        """
        self.white_list = white_list
        self.black_list = black_list

        # 编译正则表达式模式以提高性能
        self.black_patterns = [re.compile(re.escape(keyword), re.IGNORECASE) for keyword in black_list]
        self.white_patterns = [re.compile(re.escape(keyword), re.IGNORECASE) for keyword in white_list]

        logger.debug(f"规则过滤器初始化: 白名单{len(white_list)}个, 黑名单{len(black_list)}个")

    def check_title(self, title: str) -> Tuple[bool, str, Optional[str]]:
        """
        检查标题是否符合规则

        Args:
            title: 待检查的标题

        Returns:
            (是否通过, 原因, 匹配的关键词)
        """
        # 首先检查黑名单
        for i, pattern in enumerate(self.black_patterns):
            if pattern.search(title):
                black_keyword = self.black_list[i]
                return False, f"命中黑名单关键词: {black_keyword}", black_keyword

        # 然后检查白名单
        white_matches = []
        for i, pattern in enumerate(self.white_patterns):
            if pattern.search(title):
                white_matches.append(self.white_list[i])

        if white_matches:
            return True, f"匹配白名单关键词: {', '.join(white_matches)}", white_matches[0]

        # 既不在黑名单也不在白名单
        return True, "未匹配任何规则，默认通过", None


class Consumer:
    """消费者：处理任务队列"""

    def __init__(self, project_url_key: str, max_workers: int = 3):
        """
        初始化消费者

        Args:
            project_url_key: 项目URL标识
            max_workers: 最大并发工作数
        """
        self.project_url_key = project_url_key
        self.max_workers = max_workers

        # 配置文件路径
        self.queue_file = get_queue_file_path()
        self.database_path = get_database_path()

        # 加载项目规则
        self.white_list, self.black_list = self.load_project_rules()
        self.rule_filter = RuleFilter(self.white_list, self.black_list)

        # 初始化组件
        self.extractor = DeepSeekExtractor()
        self.config = BrowserConfig(
            browser_mode="undetected",
            headless=True
        )

        # 统计信息
        self.stats = {
            "total_tasks": 0,
            "skipped_blacklist": 0,
            "skipped_no_rule": 0,  # 保留字段：目前永远为0，用于未来扩展
            "passed_whitelist": 0,  # 所有通过的任务（匹配白名单 + 默认通过）
            "passed_whitelist_matched": 0,  # 新增：真正匹配白名单的任务
            "passed_default": 0,  # 新增：未匹配规则但默认通过的任务
            "detail_crawled": 0,
            "detail_failed": 0,
            "extraction_success": 0,
            "extraction_failed": 0
        }

        logger.info(f"消费者初始化完成，项目: {project_url_key}")
        logger.info(f"白名单: {len(self.white_list)}个关键词")
        logger.info(f"黑名单: {len(self.black_list)}个关键词")

    def load_project_rules(self) -> Tuple[List[str], List[str]]:
        """
        从数据库加载项目规则

        Returns:
            (白名单, 黑名单)
        """
        try:
            with SQLiteManager() as db:
                project = db.get_project(self.project_url_key)
                if not project:
                    logger.error(f"项目不存在: {self.project_url_key}")
                    # 使用默认规则
                    return (
                        ["消防设备", "消防工程", "设备改造", "设备采购"],
                        ["物流配送", "食堂配送", "服务咨询", "保安", "建筑材料"]
                    )

                return project["white_list"], project["black_list"]

        except Exception as e:
            logger.error(f"加载项目规则失败: {e}")
            # 返回默认规则
            return (
                ["消防设备", "消防工程", "设备改造", "设备采购"],
                ["物流配送", "食堂配送", "服务咨询", "保安", "建筑材料"]
            )

    def load_tasks(self, limit: int = 0) -> List[Dict[str, Any]]:
        """
        从队列文件加载任务

        Args:
            limit: 限制加载的任务数量，0表示无限制

        Returns:
            任务列表
        """
        if not os.path.exists(self.queue_file):
            logger.warning(f"队列文件不存在: {self.queue_file}")
            return []

        try:
            with open(self.queue_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            tasks = []
            for line in lines:
                try:
                    task = json.loads(line.strip())
                    # 只加载待处理的任务
                    if task.get("status") == "pending":
                        tasks.append(task)
                except json.JSONDecodeError:
                    continue

            if limit > 0:
                tasks = tasks[:limit]

            logger.info(f"从队列文件加载了 {len(tasks)} 个待处理任务")
            return tasks

        except Exception as e:
            logger.error(f"加载任务失败: {e}")
            return []

    def update_task_status(self, task_id: str, status: str, error: str = None):
        """
        更新任务状态

        Args:
            task_id: 任务ID
            status: 新状态
            error: 错误信息（如果有）
        """
        try:
            # 读取整个文件
            with open(self.queue_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            # 更新任务状态
            updated_lines = []
            for line in lines:
                try:
                    task = json.loads(line.strip())
                    if task.get("task_id") == task_id:
                        task["status"] = status
                        task["processed_at"] = datetime.now().isoformat()
                        if error:
                            task["error"] = error
                    updated_lines.append(json.dumps(task, ensure_ascii=False) + '\n')
                except json.JSONDecodeError:
                    updated_lines.append(line)

            # 写回文件
            with open(self.queue_file, 'w', encoding='utf-8') as f:
                f.writelines(updated_lines)

            logger.debug(f"任务状态更新: {task_id} -> {status}")

        except Exception as e:
            logger.error(f"更新任务状态失败: {e}")

    async def crawl_detail_page(self, crawler: AsyncWebCrawler, detail_url: str) -> Optional[str]:
        """
        爬取详情页并转换为Markdown

        Args:
            crawler: 爬虫实例
            detail_url: 详情页URL

        Returns:
            Markdown格式的内容，失败则返回None
        """
        logger.info(f"开始爬取详情页: {detail_url}")

        try:
            start_time = time.time()
            result = await crawler.arun(detail_url, timeout=30000)
            elapsed = time.time() - start_time

            if not result.success:
                logger.error(f"详情页爬取失败: {result.error_message}")
                return None

            logger.info(f"详情页爬取成功 ({elapsed:.1f}秒)")

            # 使用Crawl4AI的Markdown转换功能
            if hasattr(result, 'markdown') and result.markdown:
                markdown_content = result.markdown
            else:
                # 如果没有markdown属性，使用html
                markdown_content = f"# 原始HTML内容\n\n```html\n{result.html[:5000]}\n```"

            logger.debug(f"详情页内容长度: {len(markdown_content)} 字符")
            return markdown_content

        except Exception as e:
            logger.error(f"详情页爬取异常: {e}")
            return None

    async def process_task(self, crawler: AsyncWebCrawler, task: Dict[str, Any]) -> bool:
        """
        处理单个任务

        Args:
            crawler: 爬虫实例
            task: 任务数据

        Returns:
            是否成功处理
        """
        task_id = task.get("task_id", "unknown")
        title = task.get("title", "")
        detail_url = task.get("detail_url", "")

        logger.info(f"开始处理任务: {task_id}")
        logger.debug(f"标题: {title[:100]}...")
        logger.debug(f"URL: {detail_url}")

        # 1. 规则过滤
        passed, reason, keyword = self.rule_filter.check_title(title)

        if not passed:
            self.stats["skipped_blacklist" if keyword in self.black_list else "skipped_no_rule"] += 1
            logger.info(f"[SKIP] {reason}: {title[:80]}...")
            self.update_task_status(task_id, "skipped", reason)
            return False

        # 更新统计：区分匹配白名单和默认通过
        self.stats["passed_whitelist"] += 1  # 所有通过的任务

        if keyword is not None and keyword in self.white_list:
            # 真正匹配白名单
            self.stats["passed_whitelist_matched"] += 1
            log_prefix = "[PASS-WHITE]"
        else:
            # 未匹配规则，默认通过
            self.stats["passed_default"] += 1
            log_prefix = "[PASS-DEFAULT]"

        logger.info(f"{log_prefix} {reason}: {title[:80]}...")

        # 2. 爬取详情页
        markdown_content = await self.crawl_detail_page(crawler, detail_url)
        if not markdown_content:
            self.stats["detail_failed"] += 1
            self.update_task_status(task_id, "failed", "详情页爬取失败")
            return False

        self.stats["detail_crawled"] += 1

        # 3. 提取字段
        try:
            extracted_fields = self.extractor.extract_fields(markdown_content)
            validation = self.extractor.validate_extraction(extracted_fields)

            if validation["filled_fields_count"] >= 5:  # 至少填充5个字段才算成功
                self.stats["extraction_success"] += 1

                # 4. 保存到数据库
                with SQLiteManager() as db:
                    result_id = db.save_extraction_result(
                        project_key=self.project_url_key,
                        title=title,
                        detail_url=detail_url,
                        raw_markdown=markdown_content[:10000],  # 限制长度
                        extracted_fields=extracted_fields
                    )

                logger.info(f"✅ 提取成功，保存到数据库，ID: {result_id}")
                logger.info(f"   填充字段: {validation['filled_fields_count']}/12")
                self.update_task_status(task_id, "processed")
                return True
            else:
                self.stats["extraction_failed"] += 1
                logger.warning(f"⚠️ 提取字段不足: {validation['filled_fields_count']}/12")
                self.update_task_status(task_id, "failed", "提取字段不足")
                return False

        except Exception as e:
            self.stats["extraction_failed"] += 1
            logger.error(f"❌ 字段提取异常: {e}")
            self.update_task_status(task_id, "failed", str(e))
            return False

    async def run(self, task_limit: int = 0, batch_size: int = 10):
        """
        运行消费者流水线

        Args:
            task_limit: 处理任务数量限制，0表示无限制
            batch_size: 批处理大小
        """
        logger.info("=" * 80)
        logger.info("消费者流水线开始运行")
        logger.info("=" * 80)

        # 加载任务
        all_tasks = self.load_tasks(limit=task_limit)
        if not all_tasks:
            logger.warning("没有待处理的任务")
            return

        self.stats["total_tasks"] = len(all_tasks)
        logger.info(f"总共加载 {len(all_tasks)} 个任务")

        # 分批处理
        batches = [all_tasks[i:i + batch_size] for i in range(0, len(all_tasks), batch_size)]

        crawler = AsyncWebCrawler(config=self.config)

        try:
            for batch_num, batch in enumerate(batches, 1):
                # 批次开始：显示进度和累计统计
                progress_percent = int((batch_num - 1) / len(batches) * 100) if len(batches) > 0 else 0
                completed_tasks = (batch_num - 1) * batch_size
                remaining_tasks = self.stats["total_tasks"] - completed_tasks

                logger.info(f"[批次 {batch_num}/{len(batches)}] 开始处理 {len(batch)} 个任务")
                logger.info(f"  进度: {progress_percent}% | 已完成: {completed_tasks}/{self.stats['total_tasks']} | 剩余: {remaining_tasks}")

                # 并发处理批内任务
                tasks = [self.process_task(crawler, task) for task in batch]
                results = await asyncio.gather(*tasks, return_exceptions=True)

                # 统计本批结果
                success_count = sum(1 for r in results if r is True)
                fail_count = sum(1 for r in results if r is False)
                skip_count = len(batch) - success_count - fail_count

                # 批次结束：详细统计
                batch_success_rate = success_count / len(batch) if len(batch) > 0 else 0
                batch_skip_rate = skip_count / len(batch) if len(batch) > 0 else 0

                logger.info(f"[批次 {batch_num}/{len(batches)}] 完成 {len(batch)} 个任务")
                logger.info(f"  结果: 成功={success_count} | 跳过={skip_count} | 失败={fail_count}")
                logger.info(f"  比率: 成功率={batch_success_rate:.1%} | 跳过率={batch_skip_rate:.1%}")

                # 请求间隔
                if batch_num < len(batches):
                    logger.info(f"等待2秒后继续下一批...")
                    await asyncio.sleep(2)

        finally:
            await crawler.close()
            logger.info("爬虫实例已关闭")

        # 输出统计信息
        self.print_statistics()

    def print_statistics(self):
        """输出统计信息"""
        logger.info("=" * 80)
        logger.info("消费者流水线统计摘要")
        logger.info("=" * 80)

        total_skipped = self.stats["skipped_blacklist"] + self.stats["skipped_no_rule"]
        total_processed = self.stats["detail_crawled"] + self.stats["detail_failed"]
        success_rate = self.stats["extraction_success"] / total_processed if total_processed > 0 else 0
        skip_rate = total_skipped / self.stats['total_tasks'] if self.stats['total_tasks'] > 0 else 0

        # 总体统计
        logger.info("📊 总体统计")
        logger.info(f"  • 总任务数: {self.stats['total_tasks']}")
        logger.info(f"  • 跳过率: {skip_rate:.1%} (目标: 75%)")
        logger.info(f"  • 提取成功率: {success_rate:.1%}")

        # 跳过统计
        logger.info("\n⏭️  跳过统计")
        logger.info(f"  • 总跳过: {total_skipped}")
        logger.info(f"    - 黑名单跳过: {self.stats['skipped_blacklist']}")
        logger.info(f"    - 其他跳过: {self.stats['skipped_no_rule']} (保留字段，目前永远为0)")

        # 通过统计
        logger.info("\n✅ 通过统计")
        logger.info(f"  • 总通过: {self.stats['passed_whitelist']}")
        logger.info(f"    - 匹配白名单: {self.stats['passed_whitelist_matched']}")
        logger.info(f"    - 默认通过: {self.stats['passed_default']}")

        # 抓取统计
        logger.info("\n🌐 详情页抓取")
        logger.info(f"  • 成功: {self.stats['detail_crawled']}")
        logger.info(f"  • 失败: {self.stats['detail_failed']}")
        if total_processed > 0:
            logger.info(f"  • 抓取成功率: {self.stats['detail_crawled']/total_processed:.1%}")
        else:
            logger.info("  • 抓取成功率: N/A")

        # 提取统计
        logger.info("\n🔍 字段提取")
        logger.info(f"  • 成功: {self.stats['extraction_success']}")
        logger.info(f"  • 失败: {self.stats['extraction_failed']}")
        logger.info(f"  • 提取成功率: {success_rate:.1%}")

        # 成本控制指标
        logger.info("\n💰 成本控制指标")
        logger.info(f"  • 跳过率: {skip_rate:.1%} (目标: 75%)")
        if skip_rate >= 0.75:
            logger.info(f"  • 状态: ✅ 达到目标跳过率")
        else:
            logger.info(f"  • 状态: ⚠️  未达到目标跳过率 (差 {(0.75 - skip_rate):.1%})")


async def main():
    """主函数：消费者演示"""
    import sys
    import logging
    import argparse

    # 解析命令行参数
    parser = argparse.ArgumentParser(description='运行SmartScout消费者流水线')
    parser.add_argument('--url', type=str, required=True, help='项目URL标识（与数据库中的项目一致）')
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
    logger.info("SmartScout Phase 3: 消费者流水线")
    logger.info("=" * 80)

    try:
        # 使用命令行参数提供的项目URL标识
        project_url_key = args.url

        # 创建消费者实例
        consumer = Consumer(project_url_key, max_workers=3)

        # 运行消费者
        # 先测试处理20个任务
        await consumer.run(task_limit=20, batch_size=10)

        logger.info("\n✅ 消费者流水线完成")
        logger.info(f"数据库文件: {consumer.database_path}")
        logger.info(f"任务队列文件: {consumer.queue_file}")

        # 显示数据库统计
        with SQLiteManager() as db:
            stats = db.get_statistics()
            logger.info(f"\n数据库统计:")
            logger.info(f"项目数量: {stats.get('project_count', 0)}")
            logger.info(f"解析结果数量: {stats.get('result_count', 0)}")

    except Exception as e:
        logger.error(f"❌ 消费者流水线失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())