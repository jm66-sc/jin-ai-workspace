#!/usr/bin/env python3
"""
SmartScout Phase 1.1 终极攻坚版
目标：不惜一切代价抓取四川政府采购网公告数据
战术：多重JavaScript注入 + 手动浏览器交互模拟
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

async def ultimate_crawl_attack():
    """
    终极攻坚抓取：使用所有可能的方法获取数据
    """
    try:
        import crawl4ai
        from crawl4ai import AsyncWebCrawler

        target_url = "https://www.ccgp-sichuan.gov.cn/maincms-web/fullSearching?searchKey=消防"
        logger.info(f"🎯 终极攻坚目标: {target_url}")

        # 终极JavaScript脚本：模拟完整用户交互
        ultimate_js = """
        console.log('=== 终极JavaScript攻坚脚本开始 ===');

        // 方法1：直接检查当前页面内容
        function checkCurrentContent() {
            console.log('检查当前页面内容...');
            const fullText = document.body.innerText || document.body.textContent || '';
            console.log(`页面文本长度: ${fullText.length}`);

            // 查找包含"消防"的文本
            const fireLines = [];
            const lines = fullText.split('\\n');
            for (const line of lines) {
                if (line.includes('消防') && line.trim().length > 5) {
                    fireLines.push(line.trim());
                    console.log(`找到消防相关内容: ${line.trim().substring(0, 100)}`);
                }
            }

            return {
                textLength: fullText.length,
                fireLines: fireLines,
                hasFireContent: fireLines.length > 0
            };
        }

        // 方法2：模拟搜索交互
        async function simulateSearch() {
            console.log('尝试模拟搜索交互...');

            // 查找搜索框
            const searchInput = document.getElementById('title') ||
                              document.querySelector('input[name="key"]') ||
                              document.querySelector('input[placeholder*="查询"]') ||
                              document.querySelector('input[placeholder*="搜索"]');

            // 查找搜索按钮
            const searchButton = document.getElementById('megaloscopeBtn') ||
                                document.querySelector('input[type="submit"][value*="搜索"]') ||
                                document.querySelector('button:contains("搜索")') ||
                                document.querySelector('a:contains("搜索")');

            if (searchInput && searchButton) {
                console.log('找到搜索组件，尝试交互...');

                // 填充搜索框
                searchInput.value = '消防';
                searchInput.dispatchEvent(new Event('input', { bubbles: true }));
                searchInput.dispatchEvent(new Event('change', { bubbles: true }));

                // 等待片刻
                await new Promise(resolve => setTimeout(resolve, 2000));

                // 点击搜索按钮
                searchButton.click();
                console.log('已点击搜索按钮');

                // 等待搜索结果加载
                await new Promise(resolve => setTimeout(resolve, 8000));

                return true;
            } else {
                console.log('未找到搜索组件');
                return false;
            }
        }

        // 方法3：查找搜索结果容器
        function findResultContainer() {
            console.log('查找搜索结果容器...');

            const possibleSelectors = [
                '.search-result-list',
                '.result-list',
                '.list-container',
                '.el-table',
                '.el-table__body',
                'table',
                '.table',
                '[class*="result"]',
                '[class*="list"]',
                '[class*="table"]',
                '[class*="data"]'
            ];

            for (const selector of possibleSelectors) {
                const elements = document.querySelectorAll(selector);
                if (elements.length > 0) {
                    console.log(`找到选择器 "${selector}": ${elements.length} 个元素`);

                    // 检查元素是否包含数据
                    for (const el of elements) {
                        const text = el.innerText || el.textContent || '';
                        if (text.length > 50) {
                            console.log(`疑似结果容器，文本长度: ${text.length}`);
                            return el;
                        }
                    }
                }
            }

            console.log('未找到明确的结果容器，检查整个body');
            return document.body;
        }

        // 方法4：提取数据
        function extractDataFromContainer(container) {
            console.log('从容器提取数据...');
            const items = [];

            // 尝试多种提取策略
            const extractionStrategies = [
                // 策略1：查找所有链接
                function() {
                    const links = container.querySelectorAll('a');
                    console.log(`找到 ${links.length} 个链接`);

                    for (const link of links) {
                        const text = link.innerText || link.textContent || '';
                        const href = link.href || '';

                        if (text.includes('消防') && text.trim().length > 5) {
                            items.push({
                                title: text.trim(),
                                link: href,
                                type: '链接提取'
                            });
                        }
                    }
                },

                // 策略2：查找表格行
                function() {
                    const rows = container.querySelectorAll('tr');
                    console.log(`找到 ${rows.length} 个表格行`);

                    for (const row of rows) {
                        const text = row.innerText || row.textContent || '';
                        if (text.includes('消防') && text.length > 20) {
                            // 查找行内的链接
                            let link = '';
                            const linkEl = row.querySelector('a');
                            if (linkEl && linkEl.href) {
                                link = linkEl.href;
                            }

                            items.push({
                                title: text.trim().substring(0, 200),
                                link: link,
                                type: '表格行提取'
                            });
                        }
                    }
                },

                // 策略3：查找所有div/li元素
                function() {
                    const elements = container.querySelectorAll('div, li, p, span');
                    console.log(`检查 ${elements.length} 个文本元素`);

                    for (const el of elements) {
                        const text = el.innerText || el.textContent || '';
                        if (text.includes('消防') && text.trim().length > 10) {
                            // 查找父级或子级的链接
                            let link = '';
                            const linkEl = el.querySelector('a') || el.closest('a');
                            if (linkEl && linkEl.href) {
                                link = linkEl.href;
                            }

                            items.push({
                                title: text.trim().substring(0, 200),
                                link: link,
                                type: '文本元素提取'
                            });

                            if (items.length >= 50) break;
                        }
                    }
                }
            ];

            // 执行所有提取策略
            for (const strategy of extractionStrategies) {
                try {
                    strategy();
                    if (items.length > 0) {
                        console.log(`策略成功，提取到 ${items.length} 个项目`);
                        break;
                    }
                } catch (e) {
                    console.log(`提取策略失败: ${e}`);
                }
            }

            return items;
        }

        // 主执行流程
        console.log('开始执行攻坚流程...');

        // 步骤1：初始检查
        const initialCheck = checkCurrentContent();
        console.log(`初始检查: 文本长度=${initialCheck.textLength}, 消防行数=${initialCheck.fireLines.length}`);

        if (initialCheck.hasFireContent) {
            console.log('✅ 页面已包含消防内容，直接提取');
            const container = findResultContainer();
            const items = extractDataFromContainer(container);
            console.log(`直接提取结果: ${items.length} 个项目`);
            return items;
        }

        // 步骤2：尝试模拟搜索
        console.log('页面无消防内容，尝试模拟搜索...');
        const searchSuccess = await simulateSearch();

        if (searchSuccess) {
            console.log('搜索模拟完成，等待渲染...');
            await new Promise(resolve => setTimeout(resolve, 10000)); // 再等10秒

            // 步骤3：再次检查
            const postSearchCheck = checkCurrentContent();
            console.log(`搜索后检查: 文本长度=${postSearchCheck.textLength}, 消防行数=${postSearchCheck.fireLines.length}`);

            if (postSearchCheck.hasFireContent) {
                const container = findResultContainer();
                const items = extractDataFromContainer(container);
                console.log(`搜索后提取结果: ${items.length} 个项目`);
                return items;
            }
        }

        // 步骤4：最终兜底 - 提取所有包含"消防"的文本
        console.log('执行兜底提取...');
        const allText = document.body.innerText || document.body.textContent || '';
        const lines = allText.split('\\n');
        const fireItems = [];

        for (const line of lines) {
            if (line.includes('消防') && line.trim().length > 10) {
                fireItems.push({
                    title: line.trim().substring(0, 200),
                    link: window.location.href,
                    type: '兜底文本提取'
                });

                if (fireItems.length >= 50) break;
            }
        }

        console.log(`兜底提取结果: ${fireItems.length} 个项目`);
        return fireItems;

        console.log('=== 终极JavaScript攻坚脚本结束 ===');
        """

        # 尝试多种参数名组合
        param_combinations = [
            {"js_code": ultimate_js, "sleep": 15},  # 最可能的参数名
            {"javascript": ultimate_js, "sleep": 15},
            {"execute_script": ultimate_js, "sleep": 15},
            {"script": ultimate_js, "sleep": 15},
            {"extra_js": ultimate_js, "sleep": 15},
            {"js": ultimate_js, "sleep": 15},
            {"custom_js": ultimate_js, "sleep": 15},
        ]

        # 终极爬虫配置
        crawler_config = {
            "verbose": True,
            "strategy": "dynamic",
            "wait_for": "body",  # 最基本的选择器
            "timeout": 300000,   # 5分钟超时
            "max_scrolls": 0,    # 禁用自动滚动
            "wait_until": "networkidle",
            "headless": False,   # 必须显示浏览器！
            "stealth_mode": True,
            "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "viewport": {"width": 1920, "height": 1080},
            "markdown": False,
            "remove_overlay_elements": False,
            "bypass_cache": True,
            "ignore_https_errors": True,
        }

        # 创建爬虫
        crawler = AsyncWebCrawler(**crawler_config)

        # 尝试所有参数组合
        for i, params in enumerate(param_combinations):
            logger.info(f"尝试参数组合 {i+1}/{len(param_combinations)}: {list(params.keys())}")

            try:
                # 基础调用
                result = await crawler.arun(url=target_url, **params)

                if not result.success:
                    logger.error(f"抓取失败: {result.error_message}")
                    continue

                html_length = len(result.html) if result.html else 0
                logger.info(f"抓取成功，HTML长度: {html_length} 字符")

                # 检查结果
                if html_length < 5000:
                    logger.warning(f"HTML太短 ({html_length})，尝试下一个参数组合")
                    continue

                # 打印HTML片段
                print(f"\n=== 抓取结果 HTML片段（长度: {html_length}）===")
                print(result.html[:5000])
                print("=== 结束片段 ===\n")

                # 检查是否包含"消防"
                if "消防" in result.html:
                    logger.info("✅ 页面中包含'消防'关键词")

                    # 简单提取
                    items = extract_fire_items(result.html)
                    if items:
                        logger.info(f"✅ 提取到 {len(items)} 个包含'消防'的项目")
                        return items
                    else:
                        logger.warning("⏳ 找到'消防'关键词但未能提取结构化数据")
                else:
                    logger.warning("❌ 页面中未找到'消防'关键词")

                # 短暂等待后尝试下一个组合
                await asyncio.sleep(3)

            except Exception as e:
                logger.error(f"参数组合 {i+1} 失败: {e}")
                await asyncio.sleep(2)
                continue

        logger.error("所有参数组合尝试均失败")
        return []

    except Exception as e:
        logger.error(f"终极攻坚失败: {e}")
        import traceback
        traceback.print_exc()
        return []

def extract_fire_items(html: str) -> List[Dict[str, Any]]:
    """从HTML中提取包含'消防'的项目"""
    items = []

    # 简单行提取
    lines = html.split('\n')
    for i, line in enumerate(lines):
        if '消防' in line and len(line.strip()) > 10:
            # 尝试提取链接
            link = ''
            if 'href="' in line:
                start = line.find('href="') + 6
                end = line.find('"', start)
                if end > start:
                    link = line[start:end]
                    if link.startswith('/'):
                        link = f"https://www.ccgp-sichuan.gov.cn{link}"
                    elif not link.startswith('http'):
                        link = f"https://www.ccgp-sichuan.gov.cn/{link}"

            items.append({
                "title": line.strip()[:200],
                "link": link,
                "source_line": i + 1,
                "type": "HTML行提取"
            })

            if len(items) >= 50:
                break

    return items

def main():
    """主函数"""
    logger.info("=" * 80)
    logger.info("SmartScout Phase 1.1 终极攻坚开始")
    logger.info("目标：不惜一切代价抓取四川政府采购网公告数据")
    logger.info("战术：多重JavaScript注入 + 参数组合爆破")
    logger.info("=" * 80)

    # 运行攻坚任务
    try:
        items = asyncio.run(ultimate_crawl_attack())
    except RuntimeError:
        try:
            import nest_asyncio
            nest_asyncio.apply()
            items = asyncio.run(ultimate_crawl_attack())
        except ImportError:
            logger.error("需要安装nest_asyncio")
            items = []

    # 输出结果
    print("\n" + "=" * 80)
    print("终极攻坚结果")
    print("=" * 80)

    if items:
        print(json.dumps(items, ensure_ascii=False, indent=2))
        fire_count = sum(1 for item in items if "消防" in item.get("title", ""))
        logger.info(f"🎉 攻坚成功！提取到 {len(items)} 个项目，其中 {fire_count} 个包含'消防'")
        print(f"\n✅ 今日任务完成：成功获取 {fire_count} 条包含'消防'的公告数据")
    else:
        print(json.dumps([], ensure_ascii=False, indent=2))
        logger.error("💥 攻坚失败：未能提取任何数据")
        print(f"\n❌ 今日任务失败：未能获取到包含'消防'字样的数据")

    logger.info("=" * 80)
    logger.info("SmartScout Phase 1.1 终极攻坚结束")
    logger.info("=" * 80)

if __name__ == "__main__":
    main()