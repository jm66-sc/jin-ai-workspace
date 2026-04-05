#!/usr/bin/env python3
"""
================================================================================
⚠️⚠️⚠️ 【已废弃】Crawl4AI v0.6.3 时期的垃圾脚本 ⚠️⚠️⚠️
================================================================================

【废弃原因】
1. 基于 Crawl4AI v0.6.3 开发，该版本不支持 strategy="dynamic" 参数
2. 被迫使用 JavaScript 注入 Hack，效率极低
3. 使用 querySelectorAll('*') 暴力遍历，抓取页面噪音而非真实数据
4. 满屏 sleep 和死等，无法保证数据准确性

【正确替代】
1. 升级到 Crawl4AI v0.8.x+ 版本
2. 使用 strategy="dynamic" 和 wait_for 参数
3. 参考新版本的最简用法：
   crawler.crawl(url, strategy="dynamic", wait_for=".list-item")

【历史记录】
- 开发时间：2026-02-10
- 废弃时间：2026-02-10
- 废弃原因：版本限制导致方法论完全错误
================================================================================

SmartScout Phase 1.1 实弹验证脚本 - 强化版（已废弃）
目标：强制使用JavaScript注入抓取四川政府采购网站公告数据
宪法约束：纯抓取逻辑，不依赖LLM，必须在原阵地攻坚
"""

import asyncio
import json
import sys
import time
from typing import List, Dict, Any
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_crawl4ai_scout_with_js_injection():
    """
    使用JavaScript强制注入抓取政府采购网站
    目标：必须拿到20-50条包含"消防"字样的公告数据
    """
    try:
        # 动态导入，确保依赖已安装
        import crawl4ai
        from crawl4ai import AsyncWebCrawler
        from crawl4ai import BrowserConfig, CrawlerRunConfig, CacheMode

        target_url = "https://www.ccgp-sichuan.gov.cn/maincms-web/fullSearching?searchKey=消防"
        logger.info(f"🚀 开始强制抓取目标URL: {target_url}")

        # JavaScript代码：强制滚动、等待、提取数据
        js_code = """
        // 等待Vue应用加载完成
        console.log('开始执行强制渲染JavaScript...');

        // 等待5秒确保Vue框架加载
        await new Promise(resolve => setTimeout(resolve, 5000));
        // 强制滚动到底部触发懒加载
        window.scrollTo(0, document.body.scrollHeight);
        // 再等待2秒让内容加载
        await new Promise(resolve => setTimeout(resolve, 2000));

        // 提取所有包含"消防"的公告项
        const items = [];
        const allElements = document.querySelectorAll('*');
        for (const el of allElements) {
            const text = el.innerText || el.textContent || '';
            if (text.includes('消防') && text.length > 10) {
                // 查找最近的链接
                let link = '';
                const linkEl = el.querySelector('a') || el.closest('a');
                if (linkEl && linkEl.href) {
                    link = linkEl.href;
                }
                items.push({
                    title: text.trim().substring(0, 200),
                    link: link || window.location.href,
                    source: 'JavaScript提取'
                });
                // 限制数量
                if (items.length >= 50) break;
            }
        }
        console.log(`提取到 ${items.length} 个包含"消防"的公告`);
        return items;
        """

        # 创建浏览器配置
        browser_config = BrowserConfig(
            headless=False,  # 必须显示浏览器窗口
            verbose=True,
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
        )

        # 创建爬虫运行配置
        crawler_config = CrawlerRunConfig(
            verbose=True,
            wait_until="load",  # 等待页面加载
            page_timeout=180000,  # 3分钟超时
            js_code=js_code,  # 注入我们的JavaScript
            wait_for="body",  # 等待body元素
            scan_full_page=False,  # 禁用Crawl4AI的自动滚动，用我们的JS控制
            scroll_delay=0,
            remove_overlay_elements=False,
            cache_mode=CacheMode.BYPASS,
            delay_before_return_html=10,  # 额外等待10秒
            log_console=True,
        )

        # 使用AsyncWebCrawler
        crawler = AsyncWebCrawler(config=browser_config)

        # 最大重试次数
        max_retries = 3
        for attempt in range(max_retries):
            logger.info(f"尝试第 {attempt + 1}/{max_retries} 次抓取...")

            try:
                logger.info("正在抓取页面内容（将显示浏览器窗口）...")

                # 直接调用arun，使用配置
                result = await crawler.arun(
                    url=target_url,
                    config=crawler_config,
                )

                if hasattr(result, 'console_messages'):
                    logger.info(f"Console messages: {result.console_messages}")
                if not result.success:
                    logger.error(f"抓取失败: {result.error_message}")
                    if attempt < max_retries - 1:
                        logger.info(f"等待5秒后重试...")
                        await asyncio.sleep(5)
                        continue
                    return []

                html_length = len(result.html) if result.html else 0
                logger.info(f"抓取成功，HTML长度: {html_length} 字符")

                # 检查HTML长度（用户要求：小于5000字符则失败）
                if html_length < 5000:
                    logger.warning(f"HTML长度 {html_length} < 5000，可能未正确渲染")

                    if attempt < max_retries - 1:
                        logger.info(f"HTML太短，等待10秒后重试...")
                        await asyncio.sleep(10)

                        # 尝试更激进的配置
                        crawler_config["timeout"] = 240000  # 增加超时到4分钟
                        crawler_config["headless"] = False  # 确保显示窗口
                        continue
                    else:
                        logger.error(f"经过 {max_retries} 次尝试，HTML长度仍不足5000字符")
                else:
                    logger.info(f"✅ HTML长度检查通过: {html_length} 字符")

                    # 打印HTML片段以便调试
                    print(f"\n=== HTML片段（前3000字符，长度{html_length}）===")
                    print(result.html[:3000])
                    print("=== 结束片段 ===\n")

                    # 检查是否包含"消防"字样
                    if "消防" in result.html:
                        logger.info("✅ 页面中包含'消防'关键词")

                        # 首先尝试使用JavaScript提取的结果
                        extracted_items = []
                        if hasattr(result, 'js_execution_result') and result.js_execution_result:
                            logger.info(f"JavaScript执行结果类型: {type(result.js_execution_result)}")
                            js_result = result.js_execution_result
                            # 检查结构：{'success': True, 'results': [list]}
                            if isinstance(js_result, dict) and 'results' in js_result:
                                results_list = js_result['results']
                                if isinstance(results_list, list) and len(results_list) > 0:
                                    items = results_list[0]
                                    if isinstance(items, list):
                                        extracted_items = items
                                        logger.info(f"从JavaScript提取到 {len(extracted_items)} 个公告项")
                                    else:
                                        logger.warning(f"results[0] 不是列表: {type(items)}")
                                else:
                                    logger.warning(f"results 字段不是有效列表: {results_list}")
                            else:
                                logger.warning(f"js_execution_result 结构不符合预期: {js_result}")
                        else:
                            logger.info("JavaScript执行结果为空或不存在")

                        # 如果JavaScript提取失败，尝试从HTML中提取数据
                        if len(extracted_items) == 0:
                            extracted_items = extract_items_from_html(result.html)
                            logger.info(f"从HTML提取到 {len(extracted_items)} 个公告项")

                        return extracted_items
                    else:
                        logger.warning("页面中未找到'消防'关键词")
                        if attempt < max_retries - 1:
                            await asyncio.sleep(8)
                            continue

            except Exception as e:
                logger.error(f"抓取过程中发生错误: {e}")
                import traceback
                traceback.print_exc()

                if attempt < max_retries - 1:
                    logger.info(f"等待8秒后重试...")
                    await asyncio.sleep(8)
                    continue

        logger.error("所有重试尝试均失败")
        return []

    except ImportError as e:
        logger.error(f"导入Crawl4AI失败: {e}")
        logger.error("请确保已安装依赖: pip install -r requirements.txt")
        return []
    except Exception as e:
        logger.error(f"函数执行过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return []

def extract_items_from_html(html: str) -> List[Dict[str, Any]]:
    """
    从HTML中提取公告项
    这是一个简化的提取器，实际应根据网页结构调整
    """
    items = []

    # 简单的文本提取逻辑
    lines = html.split('\n')
    for i, line in enumerate(lines):
        if '消防' in line and len(line.strip()) > 10:
            # 尝试找到链接
            link_start = line.find('href="')
            link = ''
            if link_start != -1:
                link_end = line.find('"', link_start + 6)
                if link_end != -1:
                    link = line[link_start + 6:link_end]
                    # 确保链接完整
                    if link.startswith('/'):
                        link = f"https://www.ccgp-sichuan.gov.cn{link}"
                    elif not link.startswith('http'):
                        link = f"https://www.ccgp-sichuan.gov.cn/{link}"

            items.append({
                "title": line.strip()[:200],
                "link": link,
                "source": f"HTML行{i+1}"
            })

            if len(items) >= 50:
                break

    return items

def main():
    """主函数"""
    logger.info("=== SmartScout Phase 1.1 强化版实弹验证开始 ===")
    logger.info("目标：使用JavaScript强制注入抓取四川政府采购网公告数据")
    logger.info("宪法：不换阵地，不换库，必须在本网站拿到数据")

    # 运行异步任务
    try:
        items = asyncio.run(test_crawl4ai_scout_with_js_injection())
    except RuntimeError:
        # 如果已有事件循环，使用nest_asyncio
        try:
            import nest_asyncio
            nest_asyncio.apply()
            items = asyncio.run(test_crawl4ai_scout_with_js_injection())
        except ImportError:
            logger.error("需要安装nest_asyncio或使用异步环境")
            items = []

    # 输出JSON结果
    if items:
        print("\n" + "="*80)
        print("抓取结果（JSON格式）")
        print("="*80)
        print(json.dumps(items, ensure_ascii=False, indent=2))
        logger.info(f"✅ 成功提取 {len(items)} 个公告项")

        # 检查是否包含"消防"字样
        fire_related = sum(1 for item in items if "消防" in item.get("title", ""))
        logger.info(f"其中包含'消防'字样的公告: {fire_related} 个")

        if fire_related > 0:
            logger.info("🎯 Phase 1.1 验证成功：终端输出了包含'消防'字样的JSON数据列表")
            print(f"\n✅ 今日任务完成：成功获取 {fire_related} 条包含'消防'的公告数据")

            # 保存数据到文件
            import os
            result_file = os.path.join(os.path.dirname(__file__), '..', 'scout_result.json')
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump(items, f, ensure_ascii=False, indent=2)
            logger.info(f"✅ 数据已保存到: {os.path.abspath(result_file)}")

            # 显示前3条数据
            print("\n" + "="*80)
            print("前3条公告数据（JSON格式）")
            print("="*80)
            for i, item in enumerate(items[:3]):
                print(f"\n第 {i+1} 条:")
                print(json.dumps(item, ensure_ascii=False, indent=2))

            # 核心技术点总结
            print("\n" + "="*80)
            print("核心技术点总结")
            print("="*80)
            print("1. v0.6.3 API兼容性：必须使用 CrawlerRunConfig 对象而非字典参数")
            print("2. 动态渲染策略：通过 js_code 注入 + wait_until='load' + 强制滚动实现")
            print("3. 数据提取方法：JavaScript DOM遍历比HTML解析更可靠")
            print("4. 结果结构解析：正确处理 js_execution_result 的嵌套结构")
            print("5. 三重等待机制：Vue框架加载 + 滚动触发 + 内容渲染")
        else:
            logger.warning("⚠️  警告：提取的公告中未包含'消防'字样")
            print(f"\n⚠️  警告：提取的公告中未包含'消防'字样")
    else:
        logger.error("❌ Phase 1.1 验证失败：未能提取任何公告数据")
        print("\n" + "="*80)
        print("抓取结果（JSON格式）")
        print("="*80)
        print(json.dumps([], ensure_ascii=False, indent=2))
        print(f"\n❌ 今日任务失败：未能获取到包含'消防'字样的数据")

    logger.info("=== SmartScout Phase 1.1 强化版实弹验证结束 ===")

if __name__ == "__main__":
    main()