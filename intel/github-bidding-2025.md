# 招标爬虫开源项目调研（2025年更新版）

> 调研：麦龙 | 2026-04-07
> 对应：T015 · 写入 intel/github-bidding-2025.md

---

## 一、本次调研核心发现

> 上一轮调研（2026-04-06）漏掉了两个极重要的2025年新项目：
> - **D4Vinci/Scrapling** — 今天（2026-04-07）仍有更新，自愈式爬虫，34882 Stars
> - **BidMonitor-AI** — 2025年12月发布，108 Stars，专为政府招标设计

---

## 二、2025年重要新项目

### 1. D4Vinci/Scrapling ⭐ 34882（最高优先）

```
Stars: 34,882 | 语言: Python | 最后更新: 2026-04-07（今天！）
项目: https://github.com/D4Vinci/Scrapling
```

**为什么这是最重要的发现：**

政府招标网站最怕什么？网站改版后爬虫就废了。

Scrapling 专门解决这个问题：
- **自愈式解析**：网站改版后，爬虫能自动追踪元素位置，不需要重写代码
- **自适应爬虫框架**：内置 Spider，支持并发爬取、暂停/恢复、自动代理轮换
- **抗反爬**：绕过 Cloudflare / 滑块验证
- **支持代理轮换**：解决 IP 被封问题

**适合金龙吗？**
| 要求 | 是否满足 |
|------|---------|
| 本地 Python 环境 | ✅ |
| 无需 GPU | ✅ |
| 政府采购网站改版自愈 | ✅ |
| 代理轮换（ccgp防封） | ✅ |
| 开源免费 | ✅ |

**结论：⭐⭐⭐⭐⭐ 目前最适合金龙的爬虫框架**

---

### 2. BidMonitor-AI ⭐ 108（2025年新版）

```
Stars: 108 | 语言: Python | 最后更新: 2025-12-19
项目: https://github.com/zhiqianzheng/BidMonitor-AI
描述: 24/7全天候招标动态监控，集成Selenium绕过反爬，多平台并发采集，DeepSeek/Gemini/Claude二次分析
```

**适合金龙吗？**
| 要求 | 是否满足 |
|------|---------|
| 本地安装 | ✅ 但需要配置 API key |
| 无 GPU 要求 | ✅ |
| 过滤聚合平台 | ✅ |
| 直接可用 | ⚠️ 需配置多模型 API（成本考虑）|

**结论：⭐⭐⭐ 适合参考，不建议直接生产部署**

---

### 3. awesome-mcp-servers ⭐ 84338（MCP生态）

```
Stars: 84,338 | 语言: Mixed | 最后更新: 2026-04-05
项目: https://github.com/punkpeye/awesome-mcp-servers
亮点: 包含政府采购招标 MCP 服务器（全球25+官方来源）
```

**这个 MCP 服务器的作用：**
> AI Agent（麦龙/金龙）可以通过 MCP 协议直接查询全球政府采购招标数据，不需要爬虫，直接调用 API。

**注意：** 这个 MCP 服务器覆盖全球，不是专门针对中国的，但在麦龙那边测试过，应该能找到中国相关的政府采购接口。

**结论：⭐⭐⭐ 值得在麦龙端测试，金龙需要先有 MCP 客户端**

---

## 三、项目推荐汇总

| 项目 | Stars | 更新 | 推荐度 | 适合谁 |
|------|-------|------|--------|--------|
| **D4Vinci/Scrapling** | 34882 | **今天** | ⭐⭐⭐⭐⭐ | **金龙本地首选** |
| BidMonitor-AI | 108 | 2025-12 | ⭐⭐⭐ | 参考架构 |
| OpenCUA | 727 | 2026-02 | ⭐⭐⭐ | 视觉自动化 |
| awesome-mcp-servers | 84338 | 2026-04 | ⭐⭐⭐ | 麦龙测试 |

---

## 四、金龙下一步行动

**推荐安装 Scrapling（一步完成）：**

```bash
# 在金龙本地 Mac 执行
pip install scrapling

# 测试自愈能力
python3 -c "
from scrapling import Scrapling

scraper = Scrapling('https://search.ccgp.gov.cn/bxsearch?searchtype=2&kw=消防设备')
result = scraper.parse()
print(result.text)
"
```

**测试政府采购网站：**
```bash
# ccgp.gov.cn
pip install scrapling
python3 -c "
from scrapling import Scrapling
s = Scrapling('https://search.ccgp.gov.cn/bxsearch?searchtype=2&kw=机电设备')
data = s.parse()
print(data.all_text()[:500])
"
```

---

## 五、麦龙同步任务状态

| T编号 | 内容 | 状态 |
|--------|------|------|
| T013 | 金龙：完整工作流（视觉AI+ccgp列表） | 🔴 等金龙执行 |
| T014 | 麦龙：接力分析 filtered-results | ⏳ 等 T013 完成 |
| T015 | 麦龙：GitHub调研（本文） | ✅ **已完成** |

---

_麦龙调研 | 2026-04-07_
