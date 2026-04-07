# 金龙本地工具盘点

> 更新时间：2026-04-07 16:20

---

## 1. SmartScout（招标爬虫）

**位置：** `~/Desktop/爬虫工具/SmartScout/`

**技术栈：**
- Python 3.10.19 (`/opt/homebrew/bin/python3.10`)
- Crawl4AI 0.8.6（undetected 模式）
- Playwright + Stealth

**可执行命令：**
```bash
# 运行爬虫
cd ~/Desktop/爬虫工具/SmartScout/src
/opt/homebrew/bin/python3.10 producer.py
```

**当前状态：**
- ✅ producer.py bug 已修复（page_num 初始化）
- ✅ Crawl4AI 已安装
- ✅ 已用于爬取 ccgp.gov.cn 和国企招标平台

**输出：**
- `intel/queue-ccgp.json`（95条）
- `intel/queue-国企.json`（105条）

---

## 2. OpenCUA（视觉 AI 操作电脑）

**位置：** `~/Desktop/OpenCUA/`

**模型：**
- OpenCUA-7B（15GB，已下载）
- 位置：`~/Desktop/OpenCUA/models/OpenCUA-7B/`

**依赖：**
- transformers 4.53.0
- torch 2.8.0（MPS GPU 加速）
- PIL（截图功能）

**可执行命令：**
```bash
# 测试截图
cd ~/Desktop/OpenCUA
python3 -c "from PIL import ImageGrab; img = ImageGrab.grab(); img.save('test.png')"

# 运行模型推理
cd ~/Desktop/OpenCUA/model/inference
python3 huggingface_inference.py
```

**当前状态：**
- ✅ 项目已恢复
- ✅ 模型已下载（15GB）
- ✅ 截图功能正常
- ⚠️ 视觉操作功能需要系统权限（屏幕录制授权）

**用途：**
- 理解屏幕截图
- 输出 pyautogui 操作指令
- 自动操作浏览器（需要配合实际执行）

---

## 3. 自动化收集器（公众号文章采集）

**位置：** `~/Desktop/自动化收集器/`

**功能：**
- 公众号文章采集
- OCR 处理（PaddleOCR）
- 文章分析

**可执行脚本：**
```bash
cd ~/Desktop/自动化收集器
python3 run_5_sample.py        # 采集5篇样本
python3 mp_monitor.py          # 公众号监控
python3 sample_gongkongwang.py # 工控网样本采集
```

**当前状态：**
- ✅ 项目存在
- ⚠️ 未测试运行状态

**输出目录：**
- `test_output/`
- `test_batch_output/`

---

## 4. Git 仓库（任务管理）

**位置：** `~/.qclaw/workspace/jin-ai-workspace/`

**关键文件：**
- `TASKS.md` — 任务清单
- `briefs/` — 任务说明
- `intel/` — 爬取结果
- `state/` — 状态通知

**可执行命令：**
```bash
cd ~/.qclaw/workspace/jin-ai-workspace
git pull
git status
git add -A && git commit -m "消息" && git push
```

---

## 5. Gateway（钉钉连接器）

**位置：** `~/.qclaw/openclaw.json`

**状态：**
- ✅ 配置已写入（clientId + clientSecret）
- ✅ Gateway 已重启
- ⚠️ 待验证 Stream 连接是否正常

**测试命令：**
```bash
curl -s http://127.0.0.1:28789/health
```

---

## 总结

| 工具 | 状态 | 用途 |
|------|------|------|
| SmartScout | ✅ 可用 | 招标网站爬取 |
| OpenCUA | ✅ 模型已下载 | 视觉 AI 操作 |
| 自动化收集器 | ⚠️ 待测试 | 公众号采集 |
| Git 仓库 | ✅ 正常 | 任务管理 |
| Gateway | ⚠️ 待验证 | 钉钉连接 |

---

_金龙 | 2026-04-07_
