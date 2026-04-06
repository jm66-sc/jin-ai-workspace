# 工具盘点 - 金龙

> 盘点日期：2026-04-06 | 盘点者：金龙

---

## 一、本地爬虫工具

### 1.1 爬虫工具目录

**位置：** `~/Desktop/爬虫工具/`

| 文件/目录 | 类型 | 说明 |
|-----------|------|------|
| SmartScout/ | 目录 | 主要爬虫工具 |
| SmartScout.app | 应用程序 | macOS 应用版 |
| Start-SmartScout.command | 脚本 | 启动脚本 |
| 启动说明.txt | 文档 | 使用说明 |
| 第一批收口封板报告_20260317.md | 文档 | 历史报告 |

**当前状态：** 可用

---

### 1.2 自动化收集器目录

**位置：** `~/Desktop/自动化收集器/`

#### 核心脚本

| 文件 | 功能 | 状态 |
|------|------|------|
| mp_monitor.py | 公众号监控 | 可用 |
| books_ocr_task.py | 书籍 OCR 任务 | 可用 |
| run_30_initial_reading.py | 批量初读（30条） | 可用 |
| run_5_sample.py | 样本测试（5条） | 可用 |
| run_batch_initial_reading.py | 批量初读（批量） | 可用 |
| run_optimized_verification.py | 优化验证 | 可用 |
| sample_gongkong_forum.py | 工控论坛采样 | 可用 |
| sample_gongkongwang.py | 工控网采样 | 可用 |

#### 数据目录

| 目录 | 内容 |
|------|------|
| data/ | 运行数据存储 |
| logs/ | 运行日志 |
| scripts/ | 辅助脚本 |
| config/ | 配置文件 |
| docs/ | 文档 |
| wechat-article-exporter/ | 公众号文章导出器 |
| archive/ | 归档文件 |
| experiments/ | 实验性代码 |

#### 数据文件

| 文件 | 说明 |
|------|------|
| sample_list.json | 样本列表（原始） |
| sample_list_clean.json | 样本列表（清洗后） |
| sample_list_v2.json | 样本列表（v2） |
| mp_monitor_accounts.json | 监控的公众号账号 |

---

## 二、可执行命令

### 启动 SmartScout

```bash
# 方式1：命令行
cd ~/Desktop/爬虫工具/SmartScout
python3 main.py

# 方式2：快捷脚本
open ~/Desktop/爬虫工具/Start-SmartScout.command
```

### 运行自动化收集器

```bash
# 进入目录
cd ~/Desktop/自动化收集器/

# 运行监控
python3 mp_monitor.py

# 运行批量初读
python3 run_batch_initial_reading.py

# 运行样本测试
python3 run_5_sample.py
```

---

## 三、工具能力总结

| 能力 | 支持情况 |
|------|----------|
| 公众号文章抓取 | ✅ 支持 |
| 工控网站采样 | ✅ 支持 |
| 批量 OCR | ✅ 支持 |
| 定时监控 | ✅ 支持 |
| 数据清洗 | ✅ 支持 |
| 日志记录 | ✅ 支持 |

---

**盘点完成时间：** 2026-04-06 15:35