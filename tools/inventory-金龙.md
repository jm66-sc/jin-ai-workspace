# 金龙本地工具盘点

> 更新时间：2026-04-07 16:50
> 执行者：金龙 Agent

---

## 一、爬虫工具（~/Desktop/爬虫工具/）

### 1. SmartScout

| 项目 | 信息 |
|------|------|
| 位置 | `~/Desktop/爬虫工具/SmartScout/` |
| 类型 | Python 爬虫框架（Crawl4AI） |
| 启动方式 | `./Start-SmartScout.command` 或 `python3 src/main.py` |
| 依赖 | Python 3.10+, Crawl4AI, Playwright |
| 状态 | ✅ 可用（producer.py bug 已修复） |
| 功能 | 招标网站爬取、黑白名单筛选 |

**目录结构：**
```
SmartScout/
├── src/
│   ├── main.py          # 主入口
│   ├── producer.py      # 生产者（爬虫）
│   ├── consumer.py      # 消费者（处理）
│   └── config.py        # 配置
├── config/              # 配置文件
├── data/                # 数据输出
└── logs/                # 日志
```

**已知问题：**
- producer.py 第 312 行 page_num 未初始化 → ✅ 已修复
- ccgp.gov.cn 需用 undetected 模式绕过反爬

---

## 二、自动化收集器（~/Desktop/自动化收集器/）

### 1. 公众号文章收集器

| 项目 | 信息 |
|------|------|
| 位置 | `~/Desktop/自动化收集器/` |
| 类型 | Python 自动化脚本 |
| 主要脚本 | `mp_monitor.py`（公众号监控）|
| 依赖 | Python 3.9+, PaddleOCR（可选）|
| 状态 | ✅ 可用 |
| 功能 | 监控公众号更新、文章抓取、OCR 识别 |

**主要脚本：**
```
mp_monitor.py              # 公众号监控主程序
mp_monitor_accounts.json   # 账号配置
run_5_sample.py            # 样本采集
run_batch_initial_reading.py # 批量初始读取
sample_gongkongwang.py     # 工控网样本
sample_gongkong_forum.py   # 工控论坛样本
```

### 2. 微信文章导出器

| 项目 | 信息 |
|------|------|
| 位置 | `~/Desktop/自动化收集器/wechat-article-exporter/` |
| 类型 | 微信文章导出工具 |
| 状态 | 待确认 |

---

## 三、OpenCUA（视觉 AI）

| 项目 | 信息 |
|------|------|
| 位置 | `~/Desktop/OpenCUA/` |
| 类型 | 港大视觉 AI 项目 |
| 模型 | OpenCUA-7B（15GB）|
| 依赖 | Python 3.9+, transformers, torch, PIL |
| 状态 | ✅ 可用 |
| 功能 | 截图识别、UI 元素定位、自动化操作 |

**模型位置：** `~/Desktop/OpenCUA/models/OpenCUA-7B/`

**使用场景：**
- 需要模拟人工操作浏览器时
- 复杂网站（需要登录、验证码）无法直接爬取时

---

## 四、其他工具

### Crawl4AI（已安装）

| 项目 | 信息 |
|------|------|
| Python 版本 | 3.10.19 |
| Crawl4AI 版本 | 0.8.6 |
| 安装位置 | /opt/homebrew/lib/python3.10/ |
| 状态 | ✅ 可用 |
| 推荐配置 | `BrowserConfig(browser_mode="undetected", enable_stealth=True, headless=True)` |

---

## 五、待安装/配置

| 工具 | 状态 | 说明 |
|------|------|------|
| fastgithub | ❌ 未装 | GitHub 加速（brew 源被墙）|
| Playwright Chromium | ✅ 已装 | Crawl4AI 依赖 |

---

_金龙 Agent | 2026-04-07_
