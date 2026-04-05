#!/usr/bin/env python3
# test_bare_minimum.py - 最简测试，只传递URL

import os
import sys
import asyncio
from crawl4ai import AsyncWebCrawler

print("="*60)
print("🧪 最简Crawl4AI测试 - 只传递URL")
print("="*60)

# 清除代理
for var in ['http_proxy', 'https_proxy', 'HTTP_PROXY', 'HTTPS_PROXY']:
    os.environ.pop(var, None)

async def test_bare_minimum():
    """只传递URL，使用默认配置"""

    print("📋 使用默认配置，只传递URL...")

    # 使用默认配置
    async with AsyncWebCrawler() as crawler:
        # 测试1: 只传递URL
        print("\n1. 测试 example.com (只传递URL)...")
        try:
            result = await crawler.arun("https://example.com")
            print(f"   ✅ 成功: {result.success}")
            if result.success:
                print(f"   标题: {result.metadata.get('title', 'N/A')}")
                print(f"   内容长度: {len(result.html)} 字符")
                print(f"   错误信息: {result.error_message or '无'}")
            else:
                print(f"   ❌ 错误: {result.error_message}")
        except Exception as e:
            print(f"   ❌ 异常: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()

        # 测试2: 传递超时参数
        print("\n2. 测试 example.com (传递timeout)...")
        try:
            result2 = await crawler.arun(
                url="https://example.com",
                timeout=30000
            )
            print(f"   ✅ 成功: {result2.success}")
            if result2.success:
                print(f"   标题: {result2.metadata.get('title', 'N/A')}")
                print(f"   内容长度: {len(result2.html)} 字符")
            else:
                print(f"   ❌ 错误: {result2.error_message}")
        except Exception as e:
            print(f"   ❌ 异常: {type(e).__name__}: {e}")

        # 测试3: 查看arun方法的签名
        print("\n3. 检查arun方法签名...")
        try:
            import inspect
            sig = inspect.signature(crawler.arun)
            params = list(sig.parameters.keys())
            print(f"   arun参数: {params[:10]}...")

            # 检查哪些参数有默认值
            print(f"   参数详情:")
            for name, param in sig.parameters.items():
                if param.default != inspect.Parameter.empty:
                    print(f"     - {name} = {param.default}")
        except Exception as e:
            print(f"   检查失败: {e}")

        return result.success if 'result' in locals() else False

if __name__ == "__main__":
    success = asyncio.run(test_bare_minimum())

    print("\n" + "="*60)
    print(f"测试结果: {'✅ 成功' if success else '❌ 失败'}")

    if not success:
        print("\n🔍 问题分析:")
        print("1. 即使最简配置也失败 → 可能是库安装或环境问题")
        print("2. 代理问题 → 系统代理可能影响所有网络请求")
        print("3. 库版本兼容性 → crawl4ai 0.8.0可能有bug")

        print("\n🎯 建议:")
        print("1. 检查crawl4ai安装: `pip show crawl4ai`")
        print("2. 查看库文档或GitHub issues")
        print("3. 尝试降级版本: `pip install crawl4ai==0.7.0`")
        print("4. 检查Playwright浏览器: `playwright install chromium`")

    print("="*60)