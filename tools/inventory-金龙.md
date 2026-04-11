# 金龙本地工具盘点

> 更新时间：2026-04-11 15:15
> 执行者：金龙 Agent

---

## 一、爬虫工具（~/Desktop/爬虫工具/）

### 1. SmartScout

| 项目 | 信息 |
|------|------|
| 位置 | `~/Desktop/爬虫工具/SmartScout/` |
| 类型 | Python 爬虫框架（Crawl4AI） |
| 启动方式 | `./Start-SmartScout.command` 或 `cd SmartScout && python3 src/main.py` |
| 依赖 | Python 3.10+, Crawl4AI, Playwright |
| 最后运行 | 2026-03-29 15:05（backend.log）|
| 状态 | ⚠️ 待验证（两周未跑，需测试是否正常）|

**目录结构：**
```
SmartScout/
├── src/
│   ├── main.py          # 主入口
│   ├── producer.py      # 生产者（爬虫）✅ 已修复 page_num bug
│   ├── consumer.py      # 消费者（处理）
│   └── config.py        # 配置
├── config/              # 配置文件
├── data/                # 数据输出
└── logs/                # 日志（backend.log 736KB）
```

**已知问题：**
- producer.py 第 312 行 page_num 未初始化 → ✅ 4月7日前已修复
- ccgp.gov.cn 需用 undetected 模式绕过反爬

---

## 二、自动化收集器（~/Desktop/自动化收集器/）

### 整体状态

| 项目 | 信息 |
|------|------|
| 位置 | `~/Desktop/自动化收集器/` |
| 主要 Python | 3.9.6（系统默认）|
| 依赖 | Crawl4AI, Playwright, PaddleOCR（可选）|
| 状态 | ✅ 正常运行（今日刚完成25,160篇标准化）|

### 活跃脚本（2026-04-11 更新）

| 脚本 | 功能 | 状态 |
|------|------|------|
| `batch_standard_document.py` | 批量标准化文档 | ✅ 今日运行 |
| `standard_document.py` | 单文档标准化 | ✅ 今日运行 |
| `initial_reading_optimized.py` | 批量初读 | ✅ 今日数据存在 |
| `ima_url_import.py` | iMA URL推送 | ⚠️ API配额用尽（待明天）|
| `ima_bulk_import.py` | iMA批量导入 | ⚠️ API配额用尽 |
| `ima_dedup_tagging.py` | iMA去重标注 | ⚠️ API配额用尽 |
| `incremental_crawl.py` | 增量爬取 | ✅ 可用 |
| `incremental_crawl_checker.py` | 增量检查 | ✅ 可用 |
| `crawl_new_siemens.py` | 西门子专项爬取 | ✅ 可用 |
| `fakeid_mapping_generator.py` | 公众号fakeid映射 | ✅ 可用 |
| `topic_cluster_and_recommend.py` | 话题聚类推荐 | ✅ 可用 |
| `backfill_ir_to_standard.py` | 初读→标准化回填 | ✅ 可用 |
| `pipeline_dashboard.py` | 流水线仪表盘 | ✅ 可用 |

### 主力配置文件

```
config/
├── accounts.json               # 公众号账号列表
├── account_fakeid_mapping.json # fakeid映射
├── wechat_auth.json            # 微信认证
├── source_pool_status.json     # 来源池状态
└── downloaded.json             # 已下载记录
```

### 工具子项目

| 项目 | 位置 | 状态 |
|------|------|------|
| wechat-article-exporter | `wechat-article-exporter/` | ⚠️ 待验证 |
| Crawl4AI 集成 | scripts/ 内置 | ✅ 已集成 |

---

## 三、Crawl4AI（全局安装）

| 项目 | 信息 |
|------|------|
| 安装位置 | Python 3.9（`~/Library/Python/3.9/lib/python/site-packages/`）|
| Playwright | ✅ 已安装（`playwright ok`）|
| 状态 | ✅ 可用 |
| 推荐配置 | `BrowserConfig(browser_mode="undetached", headless=True)` |

**注意：** 推荐使用 `python3`（系统默认）运行，Python 3.10 路径下未发现独立安装。

---

## 四、OpenCUA（视觉 AI）

| 项目 | 信息 |
|------|------|
| 位置 | `~/Desktop/OpenCUA/` |
| 目录状态 | ✅ 存在（CLAUDE.md, README, assets, data）|
| 模型 | OpenCUA-7B（15GB，存于 `models/OpenCUA-7B/`）|
| 依赖 | Python 3.9+, transformers, torch, PIL |
| 状态 | ⚠️ 待验证（近期未跑）|

**使用场景：**
- 需要模拟人工操作浏览器时
- 复杂网站（需要登录、验证码）无法直接爬取时

---

## 五、OpenClaw 定时任务（launchd）

| 项目 | 信息 |
|------|------|
| 位置 | `~/workspace/jin-ai-workspace/tools/launchd/` |
| 脚本 | `check-tasks-金龙.sh` |
| 状态 | ⚠️ 待验证 |

---

## 六、其他工具

| 工具 | 状态 | 说明 |
|------|------|------|
| fastgithub | ❌ 未装 | GitHub 加速，Homebrew 源被墙 |
| Homebrew | ✅ 可用 | `/opt/homebrew/bin/brew` |
| Claude CLI | ✅ 可用 | `claude` 命令 |
| git | ✅ 可用 | |

---

## 七、待处理/验证

| 任务 | 优先级 | 说明 |
|------|--------|------|
| SmartScout 验证 | 中 | 最后运行 3/29，需测试 producer 是否正常 |
| OpenCUA 验证 | 低 | 确认模型和依赖完整性 |
| wechat-article-exporter 验证 | 中 | 确认导出功能是否正常 |
| iMA API 配额重置 | 高 | 4/12 凌晨自动重置 |

---

_金龙 Agent | 2026-04-11_
