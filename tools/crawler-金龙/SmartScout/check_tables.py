#!/usr/bin/env python3
"""
检查数据库表结构
"""
import sqlite3
import sys

DB_PATH = "data/database.sqlite"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# 获取所有表
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [row[0] for row in cursor.fetchall()]

print("数据库表:")
for table in tables:
    print(f"\n{table}:")
    cursor.execute(f"PRAGMA table_info({table})")
    columns = cursor.fetchall()
    for col in columns:
        print(f"  {col[1]} ({col[2]})")

# 检查tasks和feedback表
required_tables = ["projects", "results", "tasks", "feedback"]
for table in required_tables:
    if table in tables:
        print(f"\n✓ {table}表存在")
    else:
        print(f"\n✗ {table}表不存在")

conn.close()

# 检查现有数据
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM projects")
project_count = cursor.fetchone()[0]
cursor.execute("SELECT COUNT(*) FROM results")
result_count = cursor.fetchone()[0]
cursor.execute("SELECT COUNT(*) FROM tasks")
task_count = cursor.fetchone()[0]
cursor.execute("SELECT COUNT(*) FROM feedback")
feedback_count = cursor.fetchone()[0]

print(f"\n数据统计:")
print(f"  项目数: {project_count}")
print(f"  结果数: {result_count}")
print(f"  任务数: {task_count}")
print(f"  反馈数: {feedback_count}")

conn.close()