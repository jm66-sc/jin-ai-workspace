#!/usr/bin/env python3
"""
测试样本抓取逻辑
"""
import sys
import asyncio
import logging
from src.sample_crawler import crawl_samples_from_url

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

TEST_URL = "https://search.ccgp.gov.cn/bxsearch?searchtype=2&page_index=1&bidSort=&buyerName=&projectId=&pinMu=&bidType=&dbselect=bidx&kw=%E7%B3%BB%E7%BB%9F%E9%9B%86%E6%88%90&start_time=2026%3A03%3A11&end_time=2026%3A03%3A18&timeType=2&displayZone=&zoneId=&pppStatus=0&agentName="

async def test():
    print(f"测试URL: {TEST_URL}")
    try:
        titles = await crawl_samples_from_url(TEST_URL)
        print(f"抓取结果: {len(titles)} 个标题")
        if titles:
            print("\n前5个标题:")
            for i, title in enumerate(titles[:5]):
                print(f"{i+1}. {title}")
        else:
            print("未抓取到任何标题")
    except Exception as e:
        print(f"抓取失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test())