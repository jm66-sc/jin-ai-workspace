#!/usr/bin/env python3
# test_gov_crawling.py

from crawl4ai import AsyncWebCrawler
import asyncio
import os

# 确保代理设置
os.environ['https_proxy'] = 'http://127.0.0.1:8118'
os.environ['http_proxy'] = 'http://127.0.0.1:8118'

async def test_gov_procurement():
    """测试政府采购网站爬取"""
    print("🚀 开始测试政府采购网站爬取...")
    print(f"目标URL: https://www.ccgp-sichuan.gov.cn/maincms-web/fullSearching?searchKey=消防")

    crawler = AsyncWebCrawler()

    try:
        # 执行爬取
        result = await crawler.arun(
            url="https://www.ccgp-sichuan.gov.cn/maincms-web/fullSearching?searchKey=消防",
            strategy="dynamic",      # 动态渲染模式
            wait_for=".list-item",   # 等待列表项加载
            timeout=60000,           # 60秒超时
            verbose=True             # 显示详细日志
        )

        # 输出结果
        print("\n" + "="*50)
        print("📊 爬取结果总结:")
        print(f"✅ 成功: {result.success}")
        print(f"📄 HTML长度: {len(result.html)} 字符")
        print(f"⏱️  耗时: {result.elapsed_time:.2f} 秒")

        if result.success:
            # 提取关键信息
            print(f"\n🔍 页面标题: {result.metadata.get('title', 'N/A')}")
            print(f"🔗 最终URL: {result.metadata.get('url', 'N/A')}")

            # 检查是否有列表项
            if ".list-item" in result.html:
                print("✅ 检测到列表项 (.list-item)")
            else:
                print("⚠️  未找到列表项 (.list-item)，可能需要调整选择器")

            # 保存HTML供检查
            with open("test_result.html", "w", encoding="utf-8") as f:
                f.write(result.html)
            print("💾 HTML已保存到: test_result.html")
        else:
            print(f"❌ 错误信息: {result.error_message}")

    except Exception as e:
        print(f"❌ 爬取过程中发生异常: {str(e)}")
        import traceback
        traceback.print_exc()

    finally:
        await crawler.close()

if __name__ == "__main__":
    print("🔧 激活虚拟环境...")
    # 确保在虚拟环境中运行
    print(f"Python路径: {os.path.dirname(os.__file__)}")

    # 运行测试
    asyncio.run(test_gov_procurement())