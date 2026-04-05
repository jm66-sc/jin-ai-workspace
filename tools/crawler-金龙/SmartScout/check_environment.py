#!/usr/bin/env python3
# check_environment.py - 检查真实环境

import sys
import os

print("="*60)
print("🔍 环境验证脚本")
print("="*60)

# 检查Python版本
print(f"Python版本: {sys.version}")
print(f"Python可执行文件: {sys.executable}")
print(f"当前目录: {os.getcwd()}")

# 检查是否在虚拟环境中
in_venv = sys.prefix != sys.base_prefix
print(f"虚拟环境中: {'✅ 是' if in_venv else '❌ 否'}")
if in_venv:
    print(f"虚拟环境路径: {sys.prefix}")

# 尝试导入crawl4ai
try:
    import crawl4ai
    print(f"✅ crawl4ai导入成功")

    # 检查版本
    if hasattr(crawl4ai, '__version__'):
        version = crawl4ai.__version__
        if hasattr(version, '__version__'):
            print(f"crawl4ai版本: {version.__version__}")
        else:
            print(f"crawl4ai版本对象: {version}")
    else:
        print("⚠️  crawl4ai没有__version__属性")

    # 检查AsyncWebCrawler
    from crawl4ai import AsyncWebCrawler
    print(f"✅ AsyncWebCrawler导入成功")

    # 检查可用方法
    methods = [m for m in dir(AsyncWebCrawler) if not m.startswith('_')]
    print(f"AsyncWebCrawler方法: {', '.join(methods)}")

    # 特别检查crawl方法
    has_crawl = 'crawl' in dir(AsyncWebCrawler)
    has_arun = 'arun' in dir(AsyncWebCrawler)
    print(f"是否有crawl方法: {'✅ 有' if has_crawl else '❌ 无'}")
    print(f"是否有arun方法: {'✅ 有' if has_arun else '❌ 无'}")

except ImportError as e:
    print(f"❌ crawl4ai导入失败: {e}")
except Exception as e:
    print(f"❌ 检查过程中出错: {e}")

print("="*60)