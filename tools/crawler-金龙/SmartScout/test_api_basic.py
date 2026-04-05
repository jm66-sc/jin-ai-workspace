#!/usr/bin/env python3
"""
SmartScout API 基本测试
检查API模块能否正常导入和初始化
"""
import sys
import os
import sqlite3
import json
from pathlib import Path

print("=" * 60)
print("SmartScout API 基本测试")
print("=" * 60)

# 检查Python版本
print(f"Python版本: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")

# 检查目录结构
required_dirs = ["src", "config", "data", "logs"]
for dir_name in required_dirs:
    if os.path.exists(dir_name):
        print(f"✓ 目录存在: {dir_name}")
    else:
        print(f"✗ 目录不存在: {dir_name}")

# 检查配置文件
config_files = ["config/settings.yaml", "config/secrets.yaml"]
for config_file in config_files:
    if os.path.exists(config_file):
        print(f"✓ 配置文件存在: {config_file}")
    else:
        print(f"⚠️ 配置文件不存在: {config_file}")

# 检查样本文件
sample_files = list(Path(".").glob("simple_bids_50_*.json"))
if sample_files:
    latest_sample = max(sample_files, key=lambda x: x.stat().st_mtime)
    print(f"✓ 样本文件存在: {latest_sample.name} ({latest_sample.stat().st_size} bytes)")
else:
    print("⚠️ 样本文件不存在")

# 检查数据库
db_path = "data/database.sqlite"
if os.path.exists(db_path):
    print(f"✓ 数据库文件存在: {db_path} ({os.path.getsize(db_path)} bytes)")

    # 检查表结构
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    print(f"  数据库表: {', '.join(tables)}")
    conn.close()
else:
    print(f"⚠️ 数据库文件不存在: {db_path}")

# 尝试导入核心模块
print("\n导入核心模块...")
try:
    sys.path.insert(0, "src")
    from deepseek_rule_expander import DeepSeekRuleExpander
    from sqlite_manager import SQLiteManager
    from producer import Producer
    from consumer import Consumer
    from config_loader import get_database_path, get_queue_file_path
    print("✓ 现有爬虫模块导入成功")
except ImportError as e:
    print(f"✗ 导入现有模块失败: {e}")

# 尝试导入FastAPI相关模块
print("\n导入FastAPI模块...")
try:
    from fastapi import FastAPI
    from pydantic import BaseModel
    import uvicorn
    print("✓ FastAPI模块导入成功")
except ImportError as e:
    print(f"✗ 导入FastAPI模块失败: {e}")
    print("请运行: pip install -r requirements_api.txt")

# 检查API主文件
if os.path.exists("main.py"):
    print("✓ API主文件存在: main.py")

    # 检查API端点定义
    with open("main.py", "r", encoding="utf-8") as f:
        content = f.read()
        endpoints = [
            ("规则确诊", "/api/rule-diagnosis"),
            ("保存规则", "/api/rules/"),
            ("启动生产", "/api/production/"),
            ("获取结果", "/api/results/"),
            ("提交反馈", "/api/feedback"),
            ("任务状态", "/api/tasks/")
        ]

        for name, endpoint in endpoints:
            if endpoint in content:
                print(f"  ✓ API端点: {name} ({endpoint})")
            else:
                print(f"  ✗ API端点缺失: {name} ({endpoint})")
else:
    print("✗ API主文件不存在: main.py")

# 检查启动脚本
if os.path.exists("run.py"):
    print("✓ 启动脚本存在: run.py")
else:
    print("✗ 启动脚本不存在: run.py")

print("\n" + "=" * 60)
print("测试完成")
print("=" * 60)

# 建议
print("\n下一步:")
print("1. 安装依赖: pip install -r requirements_api.txt")
print("2. 启动API: python run.py")
print("3. 访问API文档: http://localhost:8000/docs")
print("4. 使用以下curl命令测试:")
print("   curl -X POST http://localhost:8000/api/rule-diagnosis \\")
print("     -H \"Content-Type: application/json\" \\")
print("     -d '{\"urls\":[\"https://example.com\"],\"initial_blacklist\":[],\"initial_whitelist\":[]}'")