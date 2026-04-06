# 金龙本地工具盘点

> 盘点日期：2026-04-06 | 盘点者：金龙

---

## 一、工具目录

```
~/Desktop/爬虫工具/
├── SmartScout/          # 主要爬虫项目
├── SmartScout.app/      # macOS 应用
├── Start-SmartScout.command  # 启动脚本
├── 启动说明.txt         # 启动说明
└── 第一批收口封板报告_20260317.md  # 历史报告
```

---

## 二、SmartScout 详细结构

### 2.1 核心文件

| 文件/目录 | 说明 | 状态 |
|----------|------|------|
| main.py | 主程序入口 | 可执行 |
| run.py | 运行脚本 | 可执行 |
| start.sh | Shell 启动脚本 | 可执行 |
| requirements.txt | Python 依赖 | 需检查 |

### 2.2 核心模块

| 目录 | 说明 |
|------|------|
| src/ | 源代码 |
| api/ | API 接口封装 |
| core/ | 核心逻辑 |
| config/ | 配置 |
| services/ | 服务 |
| utils/ | 工具函数 |
| scripts/ | 脚本 |
| docs/ | 文档 |
| frontend/ | 前端 |
| electron/ | Electron 桌面端 |

### 2.3 数据目录

| 目录 | 说明 |
|------|------|
| data/ | 爬取数据 |
| logs/ | 运行日志 |
| venv/ | Python 虚拟环境 |

---

## 三、可执行命令

### 3.1 启动命令

```bash
# 方式1: Shell 脚本
cd ~/Desktop/爬虫工具/SmartScout/
./start.sh

# 方式2: 桌面快捷方式
open ~/Desktop/爬虫工具/Start-SmartScout.command
open ~/Desktop/爬虫工具/SmartScout.app

# 方式3: Python 直接运行
cd ~/Desktop/爬虫工具/SmartScout/
python3 main.py
python3 run.py
```

### 3.2 测试命令

```bash
# 环境检查
python3 check_environment.py

# 运行测试
python3 test_simple.py
python3 test_api.py
python3 run_test.py
```

---

## 四、当前状态

### 4.1 最后运行时间
- 最后运行：2026-03-23
- 最后数据：extracted_items.json

### 4.2 已知问题
- 爬取速度受限
- 部分网站需要代理
- 长时间运行可能有反爬问题

### 4.3 依赖环境
- Python 3.x
- Selenium
- Playwright
- Chromium/Electron
- Node.js (前端/桌面端)

---

## 五、输出位置

- 爬取数据：`data/` 目录
- 运行日志：`logs/` 目录
- 结果文件：`scout_result.json`、`extracted_items.json`

---

**盘点完成**